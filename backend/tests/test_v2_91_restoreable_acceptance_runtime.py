from data_service.code_assets.real_acceptance_closure.runtime_restore import AcceptanceRuntimeRestorer
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v291"):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# real repo\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V291")["asset"].codebase_id
    return workspace, codebase_id


def _fake_python(tmp_path):
    script = tmp_path / "fake_python"
    script.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = \"-m\" ] && [ \"$2\" = \"pytest\" ]; then exit 0; fi\n"
        "if [ \"$1\" = \"-m\" ] && [ \"$2\" = \"venv\" ]; then mkdir -p \"$3/bin\"; exit 0; fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return str(script)


def test_v291_runtime_restore_accepts_only_real_passing_command(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)

    payload = AcceptanceRuntimeRestorer(workspace, workspace_id="v291").build_runtime_restore(
        codebase_id,
        {"python_command": _fake_python(tmp_path), "focused_command": "true", "focused_timeout_seconds": 10},
    )

    assert payload["status"] == "accepted"
    diagnosis = payload["data"]["runtime_diagnosis"]
    assert diagnosis["python_runtime"]["pytest_available"] is True
    assert diagnosis["python_runtime"]["venv_create_available"] is True
    assert diagnosis["commands"][2]["command"] == "true"
    assert diagnosis["commands"][2]["exit_code"] == 0


def test_v291_runtime_restore_keeps_broken_runtime_structured(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)

    payload = AcceptanceRuntimeRestorer(workspace, workspace_id="v291").build_runtime_restore(
        codebase_id,
        {"python_command": "definitely_missing_python_for_v291", "focused_command": "false", "focused_timeout_seconds": 10},
    )

    assert payload["status"] == "structured_blocker"
    assert any(item["id"] == "pytest_runtime" for item in payload["unresolved"])
    assert any(item["id"] == "focused_regression" for item in payload["unresolved"])
