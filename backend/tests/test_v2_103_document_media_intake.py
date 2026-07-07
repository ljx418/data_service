from data_service.workspace_portfolio import WorkspacePortfolioService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2103_document_media_intake_keeps_ocr_missing_media_non_accepted(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioService(managed, workspace_id="v2103").build(root=root)

    media = payload["data"]["media_readiness"]
    assert media["ocr_provider_health"]["status"] == "structured_unavailable"
    assert media["ocr_required_rows"]
    assert media["status"] == "structured_unavailable"
    assert all(row["status"] != "accepted" for row in media["ocr_required_rows"])
