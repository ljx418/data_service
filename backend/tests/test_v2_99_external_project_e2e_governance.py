import json

from data_service.code_assets.automated_evidence_closure.external_path_registry import ExternalProjectPathRegistry
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v299"):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# external repo\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V299")["asset"].codebase_id
    return workspace, codebase_id


def test_v299_missing_external_paths_are_structured_unavailable_not_accepted(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    payload = ExternalProjectPathRegistry(workspace, workspace_id="v299").build_external_path(codebase_id, {})
    assert payload["status"] == "structured_unavailable"
    assert all(row["status"] == "structured_unavailable" for row in payload["data"]["project_paths"]["data"]["projects"])


def test_v299_readable_projects_with_real_smoke_commands_can_accept(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    projects = {}
    commands = {}
    for project_id in ["data_service", "codexPat", "HarnessOS", "Navia"]:
        path = tmp_path / project_id
        path.mkdir()
        projects[project_id] = str(path)
        commands[project_id] = "true"
    payload = ExternalProjectPathRegistry(workspace, workspace_id="v299").build_external_path(codebase_id, {"project_paths": projects, "smoke_commands": commands})

    assert payload["status"] == "accepted"
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(tmp_path) not in raw

