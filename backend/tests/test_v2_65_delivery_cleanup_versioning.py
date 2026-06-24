from data_service.code_assets.external_e2e_portal_delivery.delivery import DeliveryCleanupVersioningService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V265\n", encoding="utf-8")
    (repo / ".tmp").mkdir()
    (repo / "backend").mkdir()
    (repo / "backend" / "tests").mkdir()
    (repo / "backend" / "tests" / "test_sample.py").write_text("def test_sample():\n    assert True\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v265"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v265").import_codebase(path=str(repo), name="V265")["asset"].codebase_id
    return repo, workspace, codebase_id


def test_v265_delivery_manifest_never_authorizes_deletion(tmp_path, monkeypatch):
    repo, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    payload = DeliveryCleanupVersioningService(workspace, workspace_id="v265").build_delivery(codebase_id, repo_root=str(repo))
    files = payload["version_manifest"]["files"]
    assert files
    assert all(item["safe_to_delete"] is False for item in files)
    assert "does not authorize deletion" in payload["cleanup_execution_plan"]
    assert payload["summary"]["safe_to_delete_true_count"] == 0


def test_v265_delivery_readback(tmp_path, monkeypatch):
    repo, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = DeliveryCleanupVersioningService(workspace, workspace_id="v265")
    service.build_delivery(codebase_id, repo_root=str(repo))
    assert service.read_delivery(codebase_id)["summary"]["file_count"] >= 1
