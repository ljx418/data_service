from data_service.workspace_portfolio import WorkspacePortfolioService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2102_project_knowledge_builder_generates_code_artifacts_and_index(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)
    service = WorkspacePortfolioService(managed, workspace_id="v2102")

    payload = service.build(root=root)

    runs = payload["data"]["project_build_runs"]["runs"]
    data_service_run = next(item for item in runs if item["project_id"] == "data_service")
    assert data_service_run["status"] == "accepted"
    assert {"import", "snapshot", "inventory", "symbols", "portfolio_brief"}.issubset(set(data_service_run["build_steps"]))
    index = payload["data"]["portfolio_index"]
    assert index["accepted_project_count"] >= 1
    assert index["portfolio_brief_refs"]
