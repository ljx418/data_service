from data_service.code_assets.real_document_acceptance.service import RealDocumentAcceptanceService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v282"):
    repo = tmp_path / "repo"
    docs = repo / "docs" / "V2.x"
    docs.mkdir(parents=True)
    (docs / "V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_PRD.md").write_text("# V2.82 PRD\n\n真实资料导入和 Wiki artifact 验收。\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V282")["asset"].codebase_id
    return workspace, codebase_id


def test_v282_real_e2e_builds_import_and_wiki_artifact_review(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = RealDocumentAcceptanceService(workspace, workspace_id="v282")
    service.build_sample_contract(codebase_id)

    payload = service.build_real_e2e(codebase_id)
    import_run = payload["data"]["import_run"]
    wiki_review = payload["data"]["wiki_artifact_review"]

    assert payload["artifact_type"] == "real_document_e2e"
    assert import_run["status"] == "accepted"
    assert import_run["rows"]
    assert all(row["source_ref"].startswith("repo://docs/") for row in import_run["rows"])
    assert wiki_review["status"] == "accepted"
    assert wiki_review["wiki_artifact_refs"]
    assert "screenshots alone are not treated as evidence" in payload["data"]["real_document_e2e_report"]


def test_v282_real_e2e_readback(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = RealDocumentAcceptanceService(workspace, workspace_id="v282")
    service.build_sample_contract(codebase_id)
    service.build_real_e2e(codebase_id)

    assert service.read_real_e2e(codebase_id)["data"]["import_run"]["artifact_type"] == "real_document_import_run"
