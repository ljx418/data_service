import json

from data_service.code_assets.external_e2e_portal_delivery.path_binding import ExternalRepositoryPathBindingService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V267\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v267"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v267").import_codebase(path=str(repo), name="V267")["asset"].codebase_id
    return tmp_path, workspace, codebase_id


def test_v267_path_binding_accepts_only_real_paths_without_leaking_absolute_paths(tmp_path, monkeypatch):
    root, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    codex = root / "codexPat"
    codex.mkdir()
    payload = ExternalRepositoryPathBindingService(workspace, workspace_id="v267").build_path_binding(
        codebase_id,
        projects=[{"name": "codexPat", "path": str(codex)}, {"name": "HarnessOS", "path": str(root / "missing")}],
    )
    rows = {item["project_id"]: item for item in payload["path_binding_matrix"]["projects"]}
    assert rows["codexPat"]["status"] == "accepted"
    assert rows["HarnessOS"]["status"] == "structured_unavailable"
    assert rows["HarnessOS"]["evidence_refs"] == []
    assert payload["summary"]["accepted_count"] >= 1
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(codex) not in raw
    assert str(workspace) not in raw


def test_v267_path_binding_readback(tmp_path, monkeypatch):
    _root, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = ExternalRepositoryPathBindingService(workspace, workspace_id="v267")
    service.build_path_binding(codebase_id)
    assert service.read_path_binding(codebase_id)["summary"]["project_count"] == 4
