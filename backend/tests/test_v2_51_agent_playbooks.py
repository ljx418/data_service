import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.agent_productization.human_portal import AgentHumanPortalService
from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService
from data_service.code_assets.agent_productization.persistence import playbook_json_path, playbook_markdown_path
from data_service.code_assets.agent_productization.playbooks import AgentProductizationPlaybookService, PLAYBOOK_ROLES
from data_service.code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService
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
        "README.md": "# Playbook Fixture\n\nA project used for role playbook validation.\n",
        "docs/V2_TARGET_ARCHITECTURE.md": "# Target Architecture\n\n- Agents should read portal and profile before editing code.\n",
        "src/main.py": "def main():\n    return 'ok'\n",
        "tests/test_main.py": "def test_main():\n    assert True\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "playbook_fixture_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V51 Playbooks")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="PlaybookFixture")["asset"]
    AgentMCPProductizationService(workspace, workspace_id=workspace_id).build_mcp_usage(asset.codebase_id, all_tool_specs())
    AgentProfileOnboardingService(workspace, workspace_id=workspace_id).build_profile_onboarding(asset.codebase_id)
    AgentHumanPortalService(workspace, workspace_id=workspace_id).build_portal(asset.codebase_id)
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload: dict, repo: Path, workspace_root: Path) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw


def _assert_recommendation_policy(playbook: dict) -> None:
    for item in playbook["recommendations"]:
        assert item.get("evidence_refs") or item.get("needs_review") is True


def test_v51_playbooks_service_http_mcp_cli_and_token_budget(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    service = AgentProductizationPlaybookService(workspace, workspace_id=workspace_id)
    build = service.build_playbooks(codebase_id)
    assert set(build["roles"]) == PLAYBOOK_ROLES
    for role in PLAYBOOK_ROLES:
        assert playbook_json_path(workspace, codebase_id, role).exists()
        assert playbook_markdown_path(workspace, codebase_id, role).exists()
        read = service.read_playbook(codebase_id, role=role)
        _assert_recommendation_policy(read["playbook"])
        assert read["markdown"]["content"].startswith("# ")
        _assert_no_absolute_path(read, repo, workspace_root)

    small = service.build_playbooks(codebase_id, role="coding_agent", max_tokens=120)
    small_playbook = small["playbooks"][0]
    assert small_playbook["omitted_items"]
    _assert_recommendation_policy(small_playbook)

    http_build = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/playbooks",
        json={"role": "maintainer", "max_tokens": 4000},
    )
    assert http_build.status_code == 200
    http_build_data = _v2(http_build.json())["data"]["agent_productization_playbooks"]
    assert http_build_data["roles"] == ["maintainer"]
    _assert_recommendation_policy(http_build_data["playbooks"][0])

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/playbooks/maintainer")
    assert http_read.status_code == 200
    http_read_data = _v2(http_read.json())["data"]["agent_productization_playbooks"]
    assert http_read_data["playbook"]["role"] == "maintainer"
    _assert_no_absolute_path(http_read_data, repo, workspace_root)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_playbook_build", {"workspace_id": workspace_id, "codebase_id": codebase_id, "role": "coding_agent"}))
    mcp_build_data = _v2(mcp_build)["data"]["agent_productization_playbooks"]
    assert mcp_build_data["roles"] == ["coding_agent"]
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_playbook_read", {"workspace_id": workspace_id, "codebase_id": codebase_id, "role": "coding_agent"}))
    mcp_read_data = _v2(mcp_read)["data"]["agent_productization_playbooks"]
    assert mcp_read_data["playbook"]["role"] == "coding_agent"
    _assert_recommendation_policy(mcp_read_data["playbook"])

    assert knowledge_main(["code", "agent-productization", "playbook-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--role", "documentation_agent"]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    assert _v2(cli_build)["data"]["agent_productization_playbooks"]["roles"] == ["documentation_agent"]

    assert knowledge_main(["code", "agent-productization", "playbook", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--role", "documentation_agent"]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    cli_read_data = _v2(cli_read)["data"]["agent_productization_playbooks"]
    assert cli_read_data["playbook"]["role"] == "documentation_agent"
    _assert_recommendation_policy(cli_read_data["playbook"])

    stable_roles = {
        http_read_data["playbook"]["role"],
        mcp_read_data["playbook"]["role"],
        cli_read_data["playbook"]["role"],
    }
    assert stable_roles == {"maintainer", "coding_agent", "documentation_agent"}


def test_v51_invalid_role_rejected(tmp_path, monkeypatch):
    client, _workspace_root, _workspace, workspace_id, codebase_id, _repo = _prepare(tmp_path, monkeypatch)
    response = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/playbooks",
        json={"role": "unsupported"},
    )
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "INVALID_AGENT_PRODUCTIZATION_PLAYBOOK_ROLE"
