from data_service.workspace_portfolio_final_evidence import WorkspacePortfolioFinalEvidenceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2107_ocr_and_media_rows_do_not_false_accept_missing_provider_evidence(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioFinalEvidenceService(managed, workspace_id="v2107").build(root=root, max_code_projects=1)

    ocr = payload["data"]["ocr_provider_health"]
    media = payload["data"]["media_evidence_matrix"]

    assert ocr["data"]["providers"]
    assert media["data"]["rows"]
    assert all(row["acceptance_status"] != "accepted" for row in media["data"]["rows"] if row["requires_ocr"])
    assert any(row["acceptance_status"] in {"structured_unavailable", "needs_review"} for row in media["data"]["rows"])
    assert payload["portfolio_final_status"] != "accepted"
