from data_service.workspace_portfolio_final_acceptance import WorkspacePortfolioFinalAcceptanceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2112_source_trace_requires_import_query_and_source_trace_links(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioFinalAcceptanceService(managed, workspace_id="v2112").build(root=root, max_code_projects=1)
    source_trace = payload["data"]["source_trace_execution"]

    assert source_trace["data"]["rows"]
    assert all(row["acceptance_status"] != "accepted" for row in source_trace["data"]["rows"])
    assert all(set(row["missing_links"]) == {"import", "query", "source_trace"} for row in source_trace["data"]["rows"])
    assert payload["portfolio_final_status"] != "accepted"
