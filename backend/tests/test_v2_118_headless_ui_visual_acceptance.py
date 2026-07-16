from data_service.workspace_portfolio_real_evidence_acceptance import WorkspacePortfolioRealEvidenceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2118_browser_missing_is_structured_unavailable_not_fake_screenshot(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr("data_service.workspace_portfolio_real_evidence_acceptance.ui_capture.shutil.which", lambda name: None)

    payload = WorkspacePortfolioRealEvidenceService(managed, workspace_id="v2118").build(root=root, max_code_projects=1, headless=True)
    ui = payload["data"]["ui_capture_results"]
    screenshots = payload["data"]["ui_screenshot_manifest"]

    assert ui["artifact_status"] == "structured_unavailable"
    assert ui["data"]["scenarios"][0]["screenshot_ref"] == ""
    assert screenshots["artifact_status"] == "structured_unavailable"


def test_v2118_ui_capture_uses_stable_selector_contract_when_browser_available(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr("data_service.workspace_portfolio_real_evidence_acceptance.ui_capture.shutil.which", lambda name: "/usr/bin/chromium")

    payload = WorkspacePortfolioRealEvidenceService(managed, workspace_id="v2118").build(root=root, max_code_projects=1, headless=True)
    ui = payload["data"]["ui_capture_results"]

    assert ui["artifact_status"] == "accepted"
    assert ui["data"]["scenarios"][0]["stable_selectors"] == ["[data-testid='portfolio-real-evidence-panel']"]
    assert ui["data"]["scenarios"][0]["selector_assertions"][0]["result"] == "present"
