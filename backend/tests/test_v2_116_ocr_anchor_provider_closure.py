from data_service.workspace_portfolio_real_evidence_acceptance import WorkspacePortfolioRealEvidenceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2116_ocr_anchor_registry_uses_real_media_and_keeps_missing_provider_structured(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)
    scan = root / "技术分享" / "scan.png"
    (root / "技术分享" / "scan.png.ocr-anchor.txt").write_text("architecture anchor", encoding="utf-8")

    monkeypatch.setattr("data_service.workspace_portfolio_real_evidence_acceptance.ocr_provider.shutil.which", lambda name: None)
    payload = WorkspacePortfolioRealEvidenceService(managed, workspace_id="v2116").build(root=root, max_code_projects=1)

    anchor = payload["data"]["ocr_anchor_registry"]
    provider = payload["data"]["ocr_provider_execution"]
    rows = {row["source_ref"]: row for row in anchor["data"]["rows"]}

    assert any("scan.png" in source_ref for source_ref in rows)
    assert anchor["artifact_status"] in {"accepted", "needs_review"}
    assert provider["artifact_status"] == "structured_unavailable"
    assert any(item["provider_name"] == "tesseract" and not item["available"] for item in provider["data"]["provider_health"])
    assert scan.exists()


def test_v2116_schema_validation_rejects_business_fields_outside_data(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)
    service = WorkspacePortfolioRealEvidenceService(managed, workspace_id="v2116")
    payload = service.build(root=root, max_code_projects=1)
    artifact = dict(payload["data"]["ocr_anchor_registry"])
    artifact["rows"] = []

    errors = service.validate_artifact("ocr_anchor_registry.json", artifact)

    assert any("Additional properties" in item for item in errors)
