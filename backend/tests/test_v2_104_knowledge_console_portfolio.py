from fastapi.testclient import TestClient

from app.main import app
from data_service.mcp_workspace_runtime import WorkspaceRuntime
from data_service.workspace_portfolio import WorkspacePortfolioService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2104_http_read_model_supports_knowledge_console_panels(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.chdir(tmp_path)
    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    runtime.ensure_workspace_meta(managed)
    WorkspacePortfolioService(managed, workspace_id="v2104").build(root=root)

    response = TestClient(app).get("/api/workspaces/v2101/portfolio")

    assert response.status_code == 200
    portfolio = response.json()["data"]["workspace_portfolio"]
    model = portfolio["data"]["knowledge_portfolio_read_model"]
    assert model["status_header"]["implementation_status"] in {"accepted", "needs_review"}
    assert model["registry_summary"]["code_project_count"] >= 1
    assert model["media_summary"]["ocr_provider_status"] == "structured_unavailable"
    assert model["project_rows"]
