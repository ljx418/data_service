from data_service.code_assets.real_document_acceptance.service import RealDocumentAcceptanceService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.mcp_tool_registry import all_tool_specs


def _prepare(tmp_path, monkeypatch, workspace_id="v285"):
    repo = tmp_path / "repo"
    docs = repo / "docs" / "V2.x"
    docs.mkdir(parents=True)
    (docs / "V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_PRD.md").write_text("# V2.85 PRD\n\n发布闭环和人工签核。\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V285")["asset"].codebase_id
    return workspace, codebase_id


def test_v285_release_closure_preserves_external_and_human_blockers(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = RealDocumentAcceptanceService(workspace, workspace_id="v285")
    service.build_sample_contract(codebase_id)
    service.build_real_e2e(codebase_id)
    service.build_retrieval_trace(codebase_id)
    service.build_quality(codebase_id)

    payload = service.build_release_closure(codebase_id)
    rerun = payload["data"]["release_closure_rerun"]
    checks = {check["id"]: check for check in rerun["checks"]}

    assert payload["artifact_type"] == "release_closure_rerun"
    assert rerun["final_release_status"] != "accepted"
    assert checks["human_approval"]["status"] == "needs_review"
    assert checks["external_projects"]["status"] == "structured_unavailable"
    assert "Final release accepted is blocked" in payload["data"]["final_manual_acceptance_report"]


def test_v285_release_closure_readback_and_mcp_specs(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = RealDocumentAcceptanceService(workspace, workspace_id="v285")
    service.build_sample_contract(codebase_id)
    service.build_real_e2e(codebase_id)
    service.build_retrieval_trace(codebase_id)
    service.build_quality(codebase_id)
    service.build_release_closure(codebase_id)

    assert service.read_release_closure(codebase_id)["data"]["release_closure_rerun"]["artifact_type"] == "release_closure_rerun"
    tools = {spec["name"] for spec in all_tool_specs()}
    assert "knowledge_code_real_document_acceptance_release_closure_build" in tools
