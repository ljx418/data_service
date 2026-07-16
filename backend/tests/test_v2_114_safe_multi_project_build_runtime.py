from data_service.workspace_portfolio_final_acceptance import WorkspacePortfolioFinalAcceptanceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2114_safe_build_queue_preserves_projects_and_rejects_unapproved_commands(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioFinalAcceptanceService(managed, workspace_id="v2114").build(root=root, max_code_projects=1)
    queue = payload["data"]["safe_build_queue"]
    execution = payload["data"]["safe_build_execution"]

    assert queue["data"]["rows"]
    assert any(row["classification"] == "code_project" for row in queue["data"]["rows"])
    assert all(row["allowlist_status"] == "needs_review" for row in queue["data"]["rows"])
    assert all(row["execution_status"] == "skipped" for row in execution["data"]["rows"])
    assert all(row["acceptance_status"] != "accepted" for row in execution["data"]["rows"])
    assert payload["portfolio_final_status"] != "accepted"
