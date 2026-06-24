from data_service.code_assets.external_e2e_portal_delivery.surface_baseline import VersionedPublicSurfaceBaselineService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V269\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v269"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v269").import_codebase(path=str(repo), name="V269")["asset"].codebase_id
    return workspace, codebase_id


def test_v269_surface_baseline_uses_real_adapter_registry_sources(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    payload = VersionedPublicSurfaceBaselineService(workspace, workspace_id="v269").build_surface_baseline(codebase_id)
    baseline = payload["surface_baseline_version"]
    assert baseline["source"] == "adapter_registry_inspection"
    assert baseline["surfaces"]["mcp"]
    assert baseline["surfaces"]["cli"]
    assert baseline["surfaces"]["http"]
    assert payload["summary"]["breaking_count"] == 0
    assert payload["surface_baseline_diff"]["items"]


def test_v269_surface_baseline_readback(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = VersionedPublicSurfaceBaselineService(workspace, workspace_id="v269")
    service.build_surface_baseline(codebase_id, baseline_label="v2.69-test")
    assert service.read_surface_baseline(codebase_id)["surface_baseline_version"]["baseline_label"] == "v2.69-test"
