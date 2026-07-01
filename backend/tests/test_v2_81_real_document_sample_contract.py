import json

from data_service.code_assets.real_document_acceptance.service import RealDocumentAcceptanceService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v281"):
    repo = tmp_path / "repo"
    docs = repo / "docs" / "V2.x"
    docs.mkdir(parents=True)
    (docs / "V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_PRD.md").write_text("# V2.81 PRD\n\n真实文档资料验收。\n", encoding="utf-8")
    (docs / "V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_TARGET_ARCHITECTURE.md").write_text("# V2.81 Architecture\n\nSource trace and quality governance.\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V281")["asset"].codebase_id
    return workspace, codebase_id


def test_v281_sample_contract_uses_repo_docs_as_real_route_b_without_final_human_acceptance(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)

    payload = RealDocumentAcceptanceService(workspace, workspace_id="v281").build_sample_contract(codebase_id)
    contract = payload["data"]["sample_contract"]

    assert payload["artifact_type"] == "real_document_sample_contract"
    assert contract["status"] == "accepted"
    assert contract["route"] == "Route B"
    assert contract["samples"]
    assert all(sample["source_ref"].startswith("repo://docs/") for sample in contract["samples"])
    assert contract["user_representative_acceptance_status"] == "needs_review"
    assert any(item["id"] == "route_a_user_documents" for item in contract["unresolved"])
    assert str(tmp_path) not in json.dumps(payload, ensure_ascii=False)


def test_v281_sample_contract_readback(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = RealDocumentAcceptanceService(workspace, workspace_id="v281")
    service.build_sample_contract(codebase_id)

    assert service.read_sample_contract(codebase_id)["data"]["sample_contract"]["artifact_type"] == "real_document_sample_contract"
