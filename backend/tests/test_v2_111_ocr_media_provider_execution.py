from data_service.workspace_portfolio_final_acceptance import WorkspacePortfolioFinalAcceptanceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2111_ocr_requires_real_sample_qualification_and_does_not_false_accept_text_extraction(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioFinalAcceptanceService(managed, workspace_id="v2111").build(root=root, max_code_projects=1)

    samples = payload["data"]["ocr_sample_qualification"]
    media = payload["data"]["media_execution_results"]

    assert samples["data"]["rows"]
    assert any(row["source_format"] == "png" for row in samples["data"]["rows"])
    assert all(row["acceptance_status"] != "accepted" for row in samples["data"]["rows"])
    assert all(row["acceptance_status"] != "accepted" for row in media["data"]["rows"] if row["execution_kind"] == "ocr")
    assert all(
        row["acceptance_status"] != "accepted"
        for row in media["data"]["rows"]
        if row["execution_kind"] == "direct_text_extraction"
    )
    assert payload["portfolio_final_status"] != "accepted"


def test_v2111_sidecar_anchor_qualifies_sample_but_missing_provider_still_blocks_ocr_acceptance(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)
    scan = root / "技术分享" / "scan.png"
    (root / "技术分享" / "scan.png.ocr-anchor.txt").write_text("Architecture", encoding="utf-8")

    payload = WorkspacePortfolioFinalAcceptanceService(managed, workspace_id="v2111").build(root=root, max_code_projects=1)

    samples = payload["data"]["ocr_sample_qualification"]
    media = payload["data"]["media_execution_results"]

    assert any(row["qualification_status"] == "qualified" for row in samples["data"]["rows"] if row["source_ref"].endswith("scan.png"))
    assert any(row["failure_category"] == "provider_missing" for row in media["data"]["rows"] if row["execution_kind"] == "ocr")
    assert payload["portfolio_final_status"] != "accepted"
