import json

from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.stabilization_e2e_portal.packaging import CANONICAL_RUNNER, FOCUSED_COMMAND, AcceptancePackagingService


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V261\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v261"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v261").import_codebase(path=str(repo), name="V261")["asset"].codebase_id
    return repo, workspace, codebase_id


def test_v261_packaging_is_advisory_and_redacted(tmp_path, monkeypatch):
    repo, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    (repo / ".tmp").mkdir()
    payload = AcceptancePackagingService(workspace, workspace_id="v261").build_package(codebase_id, repo_root=str(repo))
    manifest = payload["package_manifest"]
    assert manifest["destructive_action_required"] is False
    assert any(item["classification"] == "local_tmp" and item["recommended_action"] == "do_not_delete" for item in manifest["entries"])
    assert "This plan is advisory" in payload["cleanup_plan"]
    assert CANONICAL_RUNNER in payload["handoff_checklist"]
    assert FOCUSED_COMMAND in payload["handoff_checklist"]
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(workspace) not in raw
    assert "Traceback (most recent call last)" not in raw


def test_v261_packaging_readback(tmp_path, monkeypatch):
    repo, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = AcceptancePackagingService(workspace, workspace_id="v261")
    service.build_package(codebase_id, repo_root=str(repo))
    read_back = service.read_package(codebase_id)
    assert read_back["summary"]["destructive_action_required"] is False
