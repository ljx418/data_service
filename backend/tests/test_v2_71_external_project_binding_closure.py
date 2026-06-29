from data_service.code_assets.agent_memory_release.external_project_closure import ExternalProjectClosureService
from data_service.code_assets.external_e2e_portal_delivery.external_e2e import ExternalProjectFullE2EService
from data_service.code_assets.external_e2e_portal_delivery.path_binding import ExternalRepositoryPathBindingService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V271\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v271"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v271").import_codebase(path=str(repo), name="V271")["asset"].codebase_id
    return repo, workspace, codebase_id


def test_v271_external_project_closure_preserves_unavailable(tmp_path, monkeypatch):
    _repo, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    ExternalProjectFullE2EService(workspace, workspace_id="v271").build_e2e(codebase_id)
    ExternalRepositoryPathBindingService(workspace, workspace_id="v271").build_path_binding(codebase_id)

    payload = ExternalProjectClosureService(workspace, workspace_id="v271").build_external_project_closure(codebase_id)
    rows = {row["project_id"]: row for row in payload["project_binding_closure"]["projects"]}

    assert rows["data_service"]["status"] == "accepted"
    assert rows["codexPat"]["status"] == "structured_unavailable"
    assert rows["HarnessOS"]["status"] == "structured_unavailable"
    assert rows["Navia"]["status"] == "structured_unavailable"
    assert payload["summary"]["unavailable_accepted_count"] == 0


def test_v271_external_project_closure_readback(tmp_path, monkeypatch):
    _repo, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    ExternalRepositoryPathBindingService(workspace, workspace_id="v271").build_path_binding(codebase_id)
    service = ExternalProjectClosureService(workspace, workspace_id="v271")
    service.build_external_project_closure(codebase_id)

    assert service.read_external_project_closure(codebase_id)["artifact_type"] == "external_project_binding_closure"

