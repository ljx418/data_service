import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.agent_productization.persistence import (
    authority_rule_suggestions_path,
    no_hardcode_audit_path,
    path_pattern_suggestions_path,
    profile_draft_path,
    taxonomy_suggestions_path,
)
from data_service.code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _write_repo(repo: Path) -> None:
    files = {
        "README.md": "# Profile Fixture\n\nThis repo has profile onboarding docs.\n",
        "docs/V2_TARGET_ARCHITECTURE.md": "# Target Architecture\n\n- Agent gateway reads evidence-backed artifacts.\n",
        "docs/V2_SERVICE_PRD.md": "# PRD\n\n- The project exposes MCP and CLI usage.\n",
        "docs/V2_GAP_ANALYSIS.md": "# Gap\n\n- Profile onboarding should remain draft.\n",
        "docs/V2_ACCEPTANCE_PLAN.md": "# Acceptance\n\n- Profile artifact must be persisted.\n",
        "src/main.py": "def main():\n    return 'ok'\n",
        "tests/test_main.py": "def test_main():\n    assert True\n",
        "pyproject.toml": "[project]\nname='profile-fixture'\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "profile_fixture_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V47 Profile Onboarding")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="ProfileFixture")["asset"]
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload: dict, repo: Path, workspace_root: Path) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw


def _assert_profile_payload(payload: dict, *, repo: Path, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.46-52"
    assert payload["artifact_type"] == "project_profile_onboarding"
    assert payload["profile_draft"]["profile_status"] == "draft"
    assert payload["profile_draft"]["doc_assets"]
    assert payload["taxonomy_suggestions"]["suggestions"]
    assert payload["authority_rule_suggestions"]["rules"]
    assert payload["path_pattern_suggestions"]["patterns"]
    assert payload["no_hardcode_audit"]["status"] == "passed"
    assert payload["summary"]["taxonomy_suggestion_count"] == len(payload["taxonomy_suggestions"]["suggestions"])
    assert payload["summary"]["authority_rule_count"] == len(payload["authority_rule_suggestions"]["rules"])
    assert payload["summary"]["path_pattern_count"] == len(payload["path_pattern_suggestions"]["patterns"])
    assert payload["artifact_refs"]
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v47_profile_onboarding_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    service = AgentProfileOnboardingService(workspace, workspace_id=workspace_id)
    payload = service.build_profile_onboarding(codebase_id)
    assert payload["profile_draft"]["profile_status"] == "draft"
    assert profile_draft_path(workspace, codebase_id).exists()
    assert taxonomy_suggestions_path(workspace, codebase_id).exists()
    assert authority_rule_suggestions_path(workspace, codebase_id).exists()
    assert path_pattern_suggestions_path(workspace, codebase_id).exists()
    assert no_hardcode_audit_path(workspace, codebase_id).exists()

    read_payload = service.read_profile_onboarding(codebase_id)
    assert read_payload["summary"]["doc_asset_count"] >= 4

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/profile/build")
    assert http_build.status_code == 200
    http_build_data = _v2(http_build.json())["data"]["agent_productization_profile"]
    _assert_profile_payload(http_build_data, repo=repo, workspace_root=workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/profile")
    assert http_read.status_code == 200
    http_read_data = _v2(http_read.json())["data"]["agent_productization_profile"]
    assert http_read_data["summary"]["taxonomy_suggestion_count"] == http_build_data["summary"]["taxonomy_suggestion_count"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_profile_build", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    mcp_build_data = _v2(mcp_build)["data"]["agent_productization_profile"]
    _assert_profile_payload(mcp_build_data, repo=repo, workspace_root=workspace_root)

    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_profile_read", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    mcp_read_data = _v2(mcp_read)["data"]["agent_productization_profile"]
    assert mcp_read_data["summary"]["path_pattern_count"] == mcp_build_data["summary"]["path_pattern_count"]

    assert knowledge_main(["code", "agent-productization", "profile-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    cli_build_data = _v2(cli_build)["data"]["agent_productization_profile"]
    _assert_profile_payload(cli_build_data, repo=repo, workspace_root=workspace_root)

    assert knowledge_main(["code", "agent-productization", "profile", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    cli_read_data = _v2(cli_read)["data"]["agent_productization_profile"]
    assert cli_read_data["summary"]["authority_rule_count"] == http_read_data["summary"]["authority_rule_count"]

    stable_counts = {
        http_read_data["summary"]["taxonomy_suggestion_count"],
        mcp_read_data["summary"]["taxonomy_suggestion_count"],
        cli_read_data["summary"]["taxonomy_suggestion_count"],
    }
    assert len(stable_counts) == 1


def test_v47_profile_onboarding_missing_returns_structured_error(tmp_path, monkeypatch):
    client, _workspace_root, _workspace, workspace_id, codebase_id, _repo = _prepare(tmp_path, monkeypatch)
    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/profile")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "PROJECT_PROFILE_ONBOARDING_NOT_BUILT"

