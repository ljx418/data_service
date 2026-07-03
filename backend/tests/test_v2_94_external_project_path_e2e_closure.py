from data_service.code_assets.real_acceptance_closure.external_project_validator import ExternalProjectPathE2EValidator
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v294"):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# real repo\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V294")["asset"].codebase_id
    return workspace, codebase_id, repo


def test_v294_external_projects_keep_missing_paths_unavailable(tmp_path, monkeypatch):
    workspace, codebase_id, _ = _prepare(tmp_path, monkeypatch)

    payload = ExternalProjectPathE2EValidator(workspace, workspace_id="v294").build_external_project_closure(codebase_id)

    assert payload["status"] != "accepted"
    matrix = payload["data"]["e2e_result_matrix"]
    assert any(row["project_id"] == "codexPat" and row["e2e_status"] == "structured_unavailable" for row in matrix["projects"])


def test_v294_external_projects_accept_only_readable_paths_with_smoke(tmp_path, monkeypatch):
    workspace, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    paths = {}
    commands = {}
    for project_id in ["data_service", "codexPat", "HarnessOS", "Navia"]:
        path = repo if project_id == "data_service" else tmp_path / project_id
        path.mkdir(exist_ok=True)
        paths[project_id] = str(path)
        commands[project_id] = "true"

    payload = ExternalProjectPathE2EValidator(workspace, workspace_id="v294").build_external_project_closure(
        codebase_id,
        {"project_paths": paths, "smoke_commands": commands},
    )

    assert payload["status"] == "accepted"
    assert all(row["e2e_status"] == "accepted" for row in payload["data"]["e2e_result_matrix"]["projects"])
