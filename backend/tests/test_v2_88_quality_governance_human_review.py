from data_service.code_assets.real_document_acceptance.service import RealDocumentAcceptanceService
from data_service.code_assets.real_document_full_corpus_release.quality_review import QualityReviewClosureService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v288"):
    repo = tmp_path / "repo"
    docs = repo / "docs" / "V2.x"
    docs.mkdir(parents=True)
    (docs / "V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_PRD.md").write_text("# V2.81 PRD\n\n真实文档资料验收。\n", encoding="utf-8")
    (docs / "V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_TARGET_ARCHITECTURE.md").write_text("# V2.81 Architecture\n\nSource trace and quality governance.\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V288")["asset"].codebase_id
    service = RealDocumentAcceptanceService(workspace, workspace_id=workspace_id)
    service.build_sample_contract(codebase_id)
    service.build_real_e2e(codebase_id)
    service.build_retrieval_trace(codebase_id)
    service.build_quality(codebase_id)
    return workspace, codebase_id


def test_v288_quality_review_without_human_decisions_stays_needs_review(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)

    payload = QualityReviewClosureService(workspace, workspace_id="v288").build_quality_review(codebase_id)
    review = payload["data"]["human_quality_review"]

    assert payload["status"] == "needs_review"
    assert review["upstream_artifact_ref"].startswith("real_document_acceptance://")
    assert any(item["id"] == "quality_review_decisions" for item in payload["unresolved"])


def test_v288_quality_review_accepts_only_evidenced_human_decisions(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    decisions = [
        {"check_id": "source_trace_quality", "decision": "accepted", "evidence_refs": ["review://source_trace_quality"]},
        {"check_id": "human_quality_review", "decision": "accepted", "evidence_refs": ["review://human_quality_review"]},
    ]

    payload = QualityReviewClosureService(workspace, workspace_id="v288").build_quality_review(codebase_id, {"decisions": decisions})
    review = payload["data"]["human_quality_review"]
    effect = payload["data"]["rule_effect_review"]

    assert payload["status"] == "accepted"
    assert review["status"] == "accepted"
    assert effect["hash_unchanged"] is True
    assert "human_quality_review" in payload["data"]["correction_decision_history"]
