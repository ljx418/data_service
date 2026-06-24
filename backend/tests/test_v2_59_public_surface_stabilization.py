import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.stabilization_e2e_portal.persistence import public_surface_snapshot_path
from data_service.code_assets.stabilization_e2e_portal.public_surface import PublicSurfaceStabilizationService
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V259\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = client.post("/api/workspaces", json={"name": "V259"}).json()["workspace_id"]
    workspace = workspace_root / workspace_id
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V259")["asset"].codebase_id
    return client, workspace_root, workspace, workspace_id, codebase_id


def _v2(payload):
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_surface(payload, workspace_root: Path):
    assert payload["schema_version"] == "v2.59-62"
    snapshot = payload["snapshot"]
    parity = payload["parity_matrix"]
    drift = payload["drift_report"]
    assert snapshot["discovery_mode"] == "registry_inspection"
    assert snapshot["hardcoded_expected_only"] is False
    assert any(item["name"] == "knowledge_code_stabilization_surface_build" for item in snapshot["mcp_tools"])
    assert any("stabilization-e2e-portal surface-build" in item["command"] for item in snapshot["cli_commands"])
    assert any("/stabilization-e2e-portal/surface/build" in (item.get("route_path") or item.get("path") or item.get("debug_paths", {}).get("path", "")) for item in snapshot["http_routes"])
    assert {item["capability"] for item in parity["capabilities"]} >= {"surface", "e2e", "package", "portal"}
    assert all(item["category"] in drift["allowed_categories"] for item in drift["drift_items"])
    assert "Public Surface Migration Notes" in payload["migration_notes"]["content"] if isinstance(payload["migration_notes"], dict) else payload["migration_notes"]
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(workspace_root) not in raw
    assert "Traceback (most recent call last)" not in raw


def test_v259_public_surface_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id = _prepare(tmp_path, monkeypatch)
    service = PublicSurfaceStabilizationService(workspace, workspace_id=workspace_id)
    payload = service.build_surface(codebase_id)
    assert public_surface_snapshot_path(workspace, codebase_id).exists()
    _assert_surface(payload, workspace_root)
    _assert_surface(service.read_surface(codebase_id), workspace_root)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/surface/build")
    assert http_build.status_code == 200
    _assert_surface(_v2(http_build.json())["data"]["stabilization_surface"], workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/surface")
    assert http_read.status_code == 200
    assert _v2(http_read.json())["data"]["stabilization_surface"]["summary"]["hardcoded_expected_only"] is False

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_stabilization_surface_build", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_surface(_v2(mcp_build)["data"]["stabilization_surface"], workspace_root)

    assert knowledge_main(["code", "stabilization-e2e-portal", "surface-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    _assert_surface(_v2(json.loads(capsys.readouterr().out))["data"]["stabilization_surface"], workspace_root)

    assert knowledge_main(["code", "stabilization-e2e-portal", "surface", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    assert _v2(json.loads(capsys.readouterr().out))["data"]["stabilization_surface"]["summary"]["capability_count"] == 4


def test_v259_surface_missing_read_is_blocked(tmp_path, monkeypatch):
    client, _workspace_root, _workspace, workspace_id, codebase_id = _prepare(tmp_path, monkeypatch)
    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/surface")
    assert response.status_code == 404
    assert _v2(response.json())["error"]["code"] == "PUBLIC_SURFACE_STABILIZATION_NOT_BUILT"
