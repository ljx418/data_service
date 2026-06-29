from data_service.code_assets.project_acceptance_hardening.external_project_binding import ExternalProjectRealBindingService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V277\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v277"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v277").import_codebase(path=str(repo), name="V277")["asset"].codebase_id
    return workspace, codebase_id


def test_v277_real_binding_keeps_unavailable_projects_structured(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    payload = ExternalProjectRealBindingService(workspace, workspace_id="v277").build_external_binding(codebase_id)
    preflight = {row["project_id"]: row for row in payload["project_preflight"]["projects"]}
    rerun = {row["project_id"]: row for row in payload["e2e_rerun_records"]["projects"]}

    assert preflight["data_service"]["status"] == "accepted"
    assert rerun["data_service"]["status"] == "accepted"
    assert preflight["codexPat"]["status"] == "structured_unavailable"
    assert preflight["HarnessOS"]["status"] == "structured_unavailable"
    assert preflight["Navia"]["status"] == "structured_unavailable"
    assert payload["e2e_rerun_records"]["summary"]["unavailable_accepted_count"] == 0


def test_v277_readable_external_path_requires_e2e_evidence_before_acceptance(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    external = tmp_path / "codexPat"
    external.mkdir()
    payload = ExternalProjectRealBindingService(workspace, workspace_id="v277").build_external_binding(codebase_id, project_paths=[{"name": "codexPat", "path": str(external)}])
    rerun = {row["project_id"]: row for row in payload["e2e_rerun_records"]["projects"]}

    assert rerun["codexPat"]["status"] == "needs_review"
    assert rerun["codexPat"]["unresolved"]
