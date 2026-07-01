from data_service.code_assets.real_document_acceptance.service import RealDocumentAcceptanceService
from data_service.code_assets.real_document_full_corpus_release.external_project_closure import ExternalProjectE2EClosureService
from data_service.code_assets.real_document_full_corpus_release.full_corpus import FullCorpusE2EHardeningService
from data_service.code_assets.real_document_full_corpus_release.quality_review import QualityReviewClosureService
from data_service.code_assets.real_document_full_corpus_release.release_gate import ReleaseGateRestoreHygieneService
from data_service.code_assets.real_document_full_corpus_release.route_a_acceptance import RouteAAcceptanceService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v290"):
    repo = tmp_path / "repo"
    docs = repo / "docs" / "V2.x"
    docs.mkdir(parents=True)
    (docs / "V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_PRD.md").write_text("# V2.81 PRD\n\n真实文档资料验收。\n", encoding="utf-8")
    (docs / "V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_TARGET_ARCHITECTURE.md").write_text("# V2.81 Architecture\n\nSource trace and quality governance.\n", encoding="utf-8")
    (docs / "route_a.md").write_text("# 用户代表性资料\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V290")["asset"].codebase_id
    return workspace, codebase_id


def _build_all_inputs(workspace, codebase_id):
    service = RealDocumentAcceptanceService(workspace, workspace_id="v290")
    service.build_sample_contract(codebase_id)
    service.build_real_e2e(codebase_id)
    service.build_retrieval_trace(codebase_id)
    service.build_quality(codebase_id)
    FullCorpusE2EHardeningService(workspace, workspace_id="v290").build_full_corpus(codebase_id)
    RouteAAcceptanceService(workspace, workspace_id="v290").build_route_a(
        codebase_id,
        {
            "sample_pack_ref": "repo://docs/V2.x/route_a.md",
            "manual_review_state": "accepted",
            "evidence_refs": ["repo://docs/V2.x/route_a.md", "manual://route-a-review"],
        },
    )
    QualityReviewClosureService(workspace, workspace_id="v290").build_quality_review(
        codebase_id,
        {
            "decisions": [
                {"check_id": "source_trace_quality", "decision": "accepted", "evidence_refs": ["review://source_trace_quality"]},
                {"check_id": "human_quality_review", "decision": "accepted", "evidence_refs": ["review://human_quality_review"]},
            ]
        },
    )
    ExternalProjectE2EClosureService(workspace, workspace_id="v290").build_external_project(codebase_id, {"codexPat": "bound", "HarnessOS": "bound", "Navia": "bound"})


def test_v290_release_gate_accepts_only_when_all_required_evidence_is_present(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    _build_all_inputs(workspace, codebase_id)

    payload = ReleaseGateRestoreHygieneService(workspace, workspace_id="v290").build_release_gate(
        codebase_id,
        {
            "human_approval_state": {"status": "accepted", "evidence_refs": ["manual://release-approval"]},
            "restore_smoke_state": {"status": "accepted", "evidence_refs": ["pytest://restore-smoke"]},
            "dependency_hygiene_state": {"status": "accepted", "evidence_refs": ["audit://dependency-hygiene"]},
        },
    )
    summary = payload["data"]["release_gate_summary"]

    assert payload["status"] == "accepted"
    assert summary["final_release_status"] == "accepted"
    assert all(check["status"] == "accepted" for check in summary["checks"])


def test_v290_release_gate_keeps_missing_inputs_visible(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)

    payload = ReleaseGateRestoreHygieneService(workspace, workspace_id="v290").build_release_gate(codebase_id)
    summary = payload["data"]["release_gate_summary"]

    assert payload["status"] != "accepted"
    assert summary["human_approval_status"] == "needs_review"
    assert summary["external_project_status"] == "structured_unavailable"
    assert payload["unresolved"]
