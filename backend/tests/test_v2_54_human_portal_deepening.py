import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.agent_productization.human_portal import AgentHumanPortalService
from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService
from data_service.code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService
from data_service.code_assets.human_agent_deepening.human_portal import HumanPortalDeepeningService
from data_service.code_assets.human_agent_deepening.persistence import (
    chart_audit_path,
    portal_v2_html_path,
    project_story_path,
    reading_path_path,
    risk_priority_path,
)
from data_service.code_assets.registry import CodebaseRegistry
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_tool_registry import all_tool_specs
from data_service.mcp_workspace_runtime import WorkspaceRuntime


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _write_repo(repo: Path) -> None:
    files = {
        "README.md": "# Human Portal Deepening Fixture\n\nThis repo validates Portal V2.\n",
        "docs/V2_TARGET_ARCHITECTURE.md": "# Target Architecture\n\n- Portal V2 reads persisted artifacts only.\n",
        "docs/V2_SERVICE_PRD.md": "# PRD\n\n- Maintainers need project story, risk, evidence, and next actions.\n",
        "src/main.py": "def main():\n    return 'ok'\n",
        "tests/test_main.py": "def test_main():\n    assert True\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "portal_deepening_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V54 Human Portal Deepening")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="PortalDeepeningFixture")["asset"]
    AgentMCPProductizationService(workspace, workspace_id=workspace_id).build_mcp_usage(asset.codebase_id, all_tool_specs())
    AgentProfileOnboardingService(workspace, workspace_id=workspace_id).build_profile_onboarding(asset.codebase_id)
    AgentHumanPortalService(workspace, workspace_id=workspace_id).build_portal(asset.codebase_id)
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload, repo: Path, workspace_root: Path) -> None:
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw
    assert "Traceback (most recent call last)" not in raw


def _assert_portal_deepening_payload(payload: dict, *, repo: Path, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.54-58"
    assert payload["artifact_type"] == "human_portal_deepening"
    assert payload["project_story"]["project_summary"]["accepted_baseline"]
    assert payload["project_story"]["current_limits"]
    assert payload["project_story"]["next_actions"]
    assert payload["risk_priority"]["risk_items"]
    for item in payload["risk_priority"]["risk_items"]:
        assert item["status"] in {"accepted_evidence", "needs_review", "structured_unavailable", "structured_blocker"}
        assert item.get("evidence_refs") or item["status"] != "accepted_evidence"
    assert payload["reading_path"]["ordered_items"]
    assert payload["chart_audit"]["raw_mermaid_visible"] is False
    assert "```mermaid" not in payload["html"]["content"]
    assert "graph TD" not in payload["html"]["content"]
    assert "Human Portal V2" in payload["html"]["content"]
    assert payload["artifact_refs"]
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v54_human_portal_deepening_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    service = HumanPortalDeepeningService(workspace, workspace_id=workspace_id)
    payload = service.build_portal(codebase_id)
    assert project_story_path(workspace, codebase_id).exists()
    assert risk_priority_path(workspace, codebase_id).exists()
    assert reading_path_path(workspace, codebase_id).exists()
    assert chart_audit_path(workspace, codebase_id).exists()
    assert portal_v2_html_path(workspace, codebase_id).exists()
    assert payload["summary"]["html_contains_portal_v2"] is True

    read_payload = service.read_portal(codebase_id)
    assert read_payload["summary"]["reading_path_count"] >= 1

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/portal/build")
    assert http_build.status_code == 200
    http_build_data = _v2(http_build.json())["data"]["human_agent_deepening_portal"]
    _assert_portal_deepening_payload(http_build_data, repo=repo, workspace_root=workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/portal")
    assert http_read.status_code == 200
    http_read_data = _v2(http_read.json())["data"]["human_agent_deepening_portal"]
    assert http_read_data["summary"]["risk_count"] == http_build_data["summary"]["risk_count"]

    http_view = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/portal/view")
    assert http_view.status_code == 200
    assert "Human Portal V2" in http_view.text
    _assert_no_absolute_path(http_view.text, repo, workspace_root)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_human_agent_deepening_portal_build", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    mcp_build_data = _v2(mcp_build)["data"]["human_agent_deepening_portal"]
    _assert_portal_deepening_payload(mcp_build_data, repo=repo, workspace_root=workspace_root)

    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_human_agent_deepening_portal_read", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_read)["data"]["human_agent_deepening_portal"]["summary"]["chart_count"] >= 1

    assert knowledge_main(["code", "human-agent-deepening", "portal-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    _assert_portal_deepening_payload(_v2(cli_build)["data"]["human_agent_deepening_portal"], repo=repo, workspace_root=workspace_root)

    assert knowledge_main(["code", "human-agent-deepening", "portal", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    assert _v2(cli_read)["data"]["human_agent_deepening_portal"]["schema_version"] == "v2.54-58"


def test_v54_human_portal_deepening_missing_inputs_are_unresolved(tmp_path, monkeypatch):
    repo = tmp_path / "portal_deepening_partial_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed_partial"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V54 Partial")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="PartialPortalDeepening")["asset"]

    payload = HumanPortalDeepeningService(workspace, workspace_id=workspace_id).build_portal(asset.codebase_id)
    assert payload["unresolved"]
    assert any(item["status"] == "structured_unavailable" for item in payload["unresolved"])
    assert not any(item.get("status") == "accepted" for item in payload["unresolved"])
    assert payload["summary"]["raw_mermaid_visible"] is False
