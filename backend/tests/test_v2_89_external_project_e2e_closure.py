import json

from data_service.code_assets.real_document_full_corpus_release.external_project_closure import ExternalProjectE2EClosureService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v289"):
    repo = tmp_path / "repo"
    (repo / "docs" / "V2.x").mkdir(parents=True)
    (repo / "docs" / "V2.x" / "V2_89.md").write_text("# V2.89\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V289")["asset"].codebase_id
    return workspace, codebase_id


def test_v289_missing_external_projects_are_structured_unavailable(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)

    payload = ExternalProjectE2EClosureService(workspace, workspace_id="v289").build_external_project(codebase_id)
    records = payload["data"]["project_e2e_records"]["project_rows"]

    assert payload["status"] == "structured_unavailable"
    assert next(row for row in records if row["project_id"] == "data_service")["status"] == "accepted"
    assert all(row["status"] == "structured_unavailable" for row in records if row["project_id"] != "data_service")
    assert str(tmp_path) not in json.dumps(payload, ensure_ascii=False)


def test_v289_all_projects_accept_only_when_paths_are_bound(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    project_paths = {"codexPat": "bound", "HarnessOS": "bound", "Navia": "bound"}

    payload = ExternalProjectE2EClosureService(workspace, workspace_id="v289").build_external_project(codebase_id, project_paths)
    records = payload["data"]["project_e2e_records"]["project_rows"]

    assert payload["status"] == "accepted"
    assert {row["project_id"]: row["status"] for row in records} == {
        "data_service": "accepted",
        "codexPat": "accepted",
        "HarnessOS": "accepted",
        "Navia": "accepted",
    }
    assert all(row["evidence_refs"] for row in records)
