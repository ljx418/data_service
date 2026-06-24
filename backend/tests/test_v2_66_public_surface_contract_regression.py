from data_service.code_assets.external_e2e_portal_delivery.contract_regression import PublicSurfaceContractRegressionService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V266\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v266"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v266").import_codebase(path=str(repo), name="V266")["asset"].codebase_id
    return workspace, codebase_id


def test_v266_contract_regression_uses_real_surface_registries(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    payload = PublicSurfaceContractRegressionService(workspace, workspace_id="v266").build_contract(codebase_id)
    baseline = payload["contract_baseline"]
    assert baseline["source"] == "adapter_registry_inspection"
    assert baseline["surfaces"]["mcp"]
    assert baseline["surfaces"]["cli"]
    assert baseline["surfaces"]["http"]
    assert payload["summary"]["breaking_count"] == 0
    assert payload["compatibility_report"]["items"]


def test_v266_contract_readback(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = PublicSurfaceContractRegressionService(workspace, workspace_id="v266")
    service.build_contract(codebase_id)
    assert service.read_contract(codebase_id)["summary"]["item_count"] == 16
