from data_service.code_assets.real_document_acceptance.service import RealDocumentAcceptanceService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v283"):
    repo = tmp_path / "repo"
    docs = repo / "docs" / "V2.x"
    docs.mkdir(parents=True)
    (docs / "V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_PRD.md").write_text("# V2.83 PRD\n\n检索、GraphRAG、Source trace。\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V283")["asset"].codebase_id
    return workspace, codebase_id


def test_v283_retrieval_trace_requires_source_refs_and_preserves_graphrag_boundary(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = RealDocumentAcceptanceService(workspace, workspace_id="v283")
    service.build_sample_contract(codebase_id)
    service.build_real_e2e(codebase_id)

    payload = service.build_retrieval_trace(codebase_id)
    query_review = payload["data"]["query_trace_review"]
    graph_review = payload["data"]["graphrag_review"]

    assert payload["artifact_type"] == "retrieval_graphrag_source_trace"
    assert query_review["status"] == "accepted"
    assert all(row["source_refs"] for row in query_review["rows"])
    assert all(row["trace_status"] == "accepted" for row in query_review["rows"])
    assert "does not claim full call graph" in graph_review["graph_claim_boundary"]
    assert "runtime topology" in graph_review["graph_claim_boundary"]


def test_v283_retrieval_trace_readback(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = RealDocumentAcceptanceService(workspace, workspace_id="v283")
    service.build_sample_contract(codebase_id)
    service.build_real_e2e(codebase_id)
    service.build_retrieval_trace(codebase_id)

    assert service.read_retrieval_trace(codebase_id)["data"]["query_trace_review"]["artifact_type"] == "query_trace_review"
