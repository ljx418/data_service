from data_service.code_assets.real_document_acceptance.service import RealDocumentAcceptanceService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v284"):
    repo = tmp_path / "repo"
    docs = repo / "docs" / "V2.x"
    docs.mkdir(parents=True)
    (docs / "V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_PRD.md").write_text("# V2.84 PRD\n\n质量治理和纠错验收。\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V284")["asset"].codebase_id
    return workspace, codebase_id


def test_v284_quality_governance_keeps_human_review_needs_review(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = RealDocumentAcceptanceService(workspace, workspace_id="v284")
    service.build_sample_contract(codebase_id)
    service.build_real_e2e(codebase_id)
    service.build_retrieval_trace(codebase_id)

    payload = service.build_quality(codebase_id)
    review = payload["data"]["quality_governance_review"]

    assert payload["artifact_type"] == "quality_governance_acceptance"
    assert review["review_status"] == "needs_review"
    assert any(row["check_id"] == "human_quality_review" and row["status"] == "needs_review" for row in review["rows"])
    assert "Human quality review remains visible" in payload["data"]["correction_acceptance_report"]


def test_v284_quality_readback(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = RealDocumentAcceptanceService(workspace, workspace_id="v284")
    service.build_sample_contract(codebase_id)
    service.build_real_e2e(codebase_id)
    service.build_retrieval_trace(codebase_id)
    service.build_quality(codebase_id)

    assert service.read_quality(codebase_id)["data"]["quality_governance_review"]["artifact_type"] == "quality_governance_review"
