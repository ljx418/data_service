from data_service.workspace_portfolio_final_acceptance import WorkspacePortfolioFinalAcceptanceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2113_headless_ui_does_not_claim_screenshot_without_real_capture(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioFinalAcceptanceService(managed, workspace_id="v2113").build(root=root, max_code_projects=1, headless=True)
    ui = payload["data"]["ui_evidence_capture"]
    manifest = payload["data"]["ui_screenshot_manifest"]

    assert ui["data"]["rows"]
    assert ui["data"]["rows"][0]["screenshot_ref"] == ""
    assert ui["data"]["rows"][0]["acceptance_status"] == "structured_unavailable"
    assert manifest["data"]["rows"][0]["non_accepted_visible"] is True
    assert payload["portfolio_final_status"] != "accepted"
