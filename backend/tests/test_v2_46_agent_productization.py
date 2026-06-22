import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.agent_productization.persistence import (
    codex_mcp_usage_guide_path,
    mcp_agent_workflows_path,
    mcp_tool_catalog_readable_path,
    mcp_usage_guide_path,
)
from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService
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
        "README.md": "# Agent Productization Fixture\n\nThis repo is used for MCP guide validation.\n",
        "src/main.py": "def main():\n    return 'ok'\n",
        "docs/architecture.md": "# Architecture\n\n- MCP tools should be used before broad code reading.\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V46 Agent Productization")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo))["asset"]
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload: dict, repo: Path, workspace_root: Path) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw


def _assert_agent_payload(payload: dict, *, workspace_id: str, codebase_id: str, repo: Path, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.46-52"
    assert payload["artifact_type"] == "agent_productization_mcp_bundle"
    assert payload["tool_count"] == len(all_tool_specs())
    assert payload["workflow_count"] >= 4
    assert payload["validation_summary"]["registry_count"] == len(all_tool_specs())
    assert payload["validation_summary"]["catalog_count"] == len(all_tool_specs())
    assert "Codex CLI MCP Usage Guide" in payload["codex_mcp_usage_guide"]["content"]
    assert payload["artifact_refs"]
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v46_agent_productization_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    service = AgentMCPProductizationService(workspace, workspace_id=workspace_id)
    payload = service.build_mcp_usage(codebase_id, all_tool_specs())
    public_payload = payload["mcp_usage_guide"]
    assert public_payload["schema_version"] == "v2.46-52"
    assert public_payload["validation_summary"]["registry_count"] == len(all_tool_specs())
    assert mcp_usage_guide_path(workspace, codebase_id).exists()
    assert mcp_tool_catalog_readable_path(workspace, codebase_id).exists()
    assert mcp_agent_workflows_path(workspace, codebase_id).exists()
    assert codex_mcp_usage_guide_path(workspace, codebase_id).exists()

    read_payload = service.read_mcp_usage(codebase_id)
    assert read_payload["mcp_tool_catalog_readable"]["tool_count"] == len(all_tool_specs())

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/mcp/build")
    assert http_build.status_code == 200
    http_build_data = _v2(http_build.json())["data"]["agent_productization_mcp"]
    _assert_agent_payload(http_build_data, workspace_id=workspace_id, codebase_id=codebase_id, repo=repo, workspace_root=workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/mcp")
    assert http_read.status_code == 200
    http_read_data = _v2(http_read.json())["data"]["agent_productization_mcp"]
    assert http_read_data["tool_count"] == http_build_data["tool_count"]
    assert len(http_read_data["artifact_refs"]) == len(http_build_data["artifact_refs"])

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_mcp_build", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    mcp_build_data = _v2(mcp_build)["data"]["agent_productization_mcp"]
    assert mcp_build_data["tool_count"] == len(all_tool_specs())

    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_mcp_read", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    mcp_read_data = _v2(mcp_read)["data"]["agent_productization_mcp"]
    assert mcp_read_data["workflow_count"] == mcp_build_data["workflow_count"]

    assert knowledge_main(["code", "agent-productization", "mcp-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    cli_build_data = _v2(cli_build)["data"]["agent_productization_mcp"]
    assert cli_build_data["tool_count"] == len(all_tool_specs())

    assert knowledge_main(["code", "agent-productization", "mcp", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    cli_read_data = _v2(cli_read)["data"]["agent_productization_mcp"]
    assert cli_read_data["validation_summary"]["catalog_count"] == len(all_tool_specs())

    stable_counts = {
        http_read_data["tool_count"],
        mcp_read_data["tool_count"],
        cli_read_data["tool_count"],
    }
    assert stable_counts == {len(all_tool_specs())}


def test_v46_agent_productization_missing_returns_structured_error(tmp_path, monkeypatch):
    client, _workspace_root, _workspace, workspace_id, codebase_id, _repo = _prepare(tmp_path, monkeypatch)
    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/mcp")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "MCP_PRODUCTIZATION_NOT_BUILT"

