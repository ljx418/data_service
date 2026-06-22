import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.agent_productization.human_portal import AgentHumanPortalService
from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService
from data_service.code_assets.agent_productization.persistence import portal_html_path, portal_model_path, portal_svg_path
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
        "README.md": "# Portal Fixture\n\nThis repo is used for human portal validation.\n",
        "docs/V2_TARGET_ARCHITECTURE.md": "# Target Architecture\n\n- Human portal renders persisted artifacts.\n",
        "docs/V2_SERVICE_PRD.md": "# PRD\n\n- Agent workflows must be visible.\n",
        "src/main.py": "def main():\n    return 'ok'\n",
        "tests/test_main.py": "def test_main():\n    assert True\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "portal_fixture_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V48 Human Portal")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="PortalFixture")["asset"]
    AgentMCPProductizationService(workspace, workspace_id=workspace_id).build_mcp_usage(asset.codebase_id, all_tool_specs())
    AgentProfileOnboardingService(workspace, workspace_id=workspace_id).build_profile_onboarding(asset.codebase_id)
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload, repo: Path, workspace_root: Path) -> None:
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw


def _assert_portal_payload(payload: dict, *, repo: Path, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.46-52"
    assert payload["artifact_type"] == "human_architecture_portal"
    assert payload["summary"]["section_count"] >= 3
    assert payload["summary"]["chart_node_count"] >= 4
    assert payload["summary"]["html_contains_svg"] is True
    assert payload["summary"]["contains_mermaid_source"] is False
    assert "<svg" in payload["html"]["content"]
    assert "```mermaid" not in payload["html"]["content"]
    assert "graph TD" not in payload["html"]["content"]
    node_ids = {node["node_id"] for node in payload["portal_model"]["chart"]["nodes"]}
    for edge in payload["portal_model"]["chart"]["edges"]:
        assert edge["from"] in node_ids
        assert edge["to"] in node_ids
    assert payload["artifact_refs"]
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v48_human_portal_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    service = AgentHumanPortalService(workspace, workspace_id=workspace_id)
    payload = service.build_portal(codebase_id)
    assert payload["summary"]["html_contains_svg"] is True
    assert portal_model_path(workspace, codebase_id).exists()
    assert portal_svg_path(workspace, codebase_id).exists()
    assert portal_html_path(workspace, codebase_id).exists()

    read_payload = service.read_portal(codebase_id)
    assert read_payload["summary"]["chart_node_count"] >= 4

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/portal/build")
    assert http_build.status_code == 200
    http_build_data = _v2(http_build.json())["data"]["agent_productization_portal"]
    _assert_portal_payload(http_build_data, repo=repo, workspace_root=workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/portal")
    assert http_read.status_code == 200
    http_read_data = _v2(http_read.json())["data"]["agent_productization_portal"]
    assert http_read_data["summary"]["section_count"] == http_build_data["summary"]["section_count"]

    http_view = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/portal/view")
    assert http_view.status_code == 200
    assert "<svg" in http_view.text
    assert "```mermaid" not in http_view.text
    _assert_no_absolute_path(http_view.text, repo, workspace_root)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_portal_build", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    mcp_build_data = _v2(mcp_build)["data"]["agent_productization_portal"]
    _assert_portal_payload(mcp_build_data, repo=repo, workspace_root=workspace_root)

    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_portal_read", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    mcp_read_data = _v2(mcp_read)["data"]["agent_productization_portal"]
    assert mcp_read_data["summary"]["chart_node_count"] == mcp_build_data["summary"]["chart_node_count"]

    assert knowledge_main(["code", "agent-productization", "portal-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    cli_build_data = _v2(cli_build)["data"]["agent_productization_portal"]
    _assert_portal_payload(cli_build_data, repo=repo, workspace_root=workspace_root)

    assert knowledge_main(["code", "agent-productization", "portal", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    cli_read_data = _v2(cli_read)["data"]["agent_productization_portal"]
    assert cli_read_data["summary"]["section_count"] == http_read_data["summary"]["section_count"]


def test_v48_human_portal_missing_returns_structured_error(tmp_path, monkeypatch):
    client, workspace_root, workspace, workspace_id, codebase_id, _repo = _prepare(tmp_path, monkeypatch)
    portal_html_path(workspace, codebase_id).unlink(missing_ok=True)
    portal_model_path(workspace, codebase_id).unlink(missing_ok=True)
    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/portal")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "HUMAN_PORTAL_NOT_BUILT"
    _assert_no_absolute_path(response.json(), workspace, workspace_root)
