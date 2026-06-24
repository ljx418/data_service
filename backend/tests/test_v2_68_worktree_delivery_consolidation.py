from data_service.code_assets.external_e2e_portal_delivery.worktree_delivery import WorktreeDeliveryConsolidationService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V268\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v268"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v268").import_codebase(path=str(repo), name="V268")["asset"].codebase_id
    return repo, workspace, codebase_id


def test_v268_worktree_delivery_is_review_only_and_never_marks_safe_delete(tmp_path, monkeypatch):
    repo, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    (repo / "backend").mkdir()
    (repo / "backend" / "example.py").write_text("x = 1\n", encoding="utf-8")
    (repo / ".tmp").mkdir()
    (repo / ".tmp" / "cache.txt").write_text("cache\n", encoding="utf-8")
    payload = WorktreeDeliveryConsolidationService(workspace, workspace_id="v268").build_worktree_delivery(codebase_id, repo_root=str(repo))
    files = payload["delivery_review_manifest"]["files"]
    assert files
    assert payload["summary"]["safe_to_delete_true_count"] == 0
    assert all(item["safe_to_delete"] is False for item in files)
    assert "does not authorize deletion" in payload["delivery_review_plan"]


def test_v268_worktree_delivery_readback(tmp_path, monkeypatch):
    repo, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = WorktreeDeliveryConsolidationService(workspace, workspace_id="v268")
    service.build_worktree_delivery(codebase_id, repo_root=str(repo))
    assert "delivery_review_manifest" in service.read_worktree_delivery(codebase_id)
