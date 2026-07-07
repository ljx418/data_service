from data_service.workspace_portfolio import WorkspacePortfolioService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2105_release_gate_separates_implementation_and_portfolio_final_status(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioService(managed, workspace_id="v2105").build(root=root)

    gate = payload["data"]["release_gate"]
    assert payload["status"] != "accepted"
    assert gate["status"] == gate["portfolio_final_status"]
    assert gate["implementation_status"] == "accepted"
    assert gate["portfolio_final_status"] != "accepted"
    assert gate["false_green_audit_status"] == "accepted"
    assert any(item["kind"] == "structured_unavailable" for item in gate["unresolved"])
