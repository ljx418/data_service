from data_service.code_assets.project_acceptance_hardening.warning_reduction import CIWarningReductionService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V278\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v278"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v278").import_codebase(path=str(repo), name="V278")["asset"].codebase_id
    return workspace, codebase_id


def test_v278_over_budget_warning_gate_blocks_release(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    payload = CIWarningReductionService(workspace, workspace_id="v278").build_warning_reduction(
        codebase_id,
        command_results={"observed_warning_count": 12, "warning_budget": 2, "failure_category": "dependency_drift"},
    )

    assert payload["release_warning_gate"]["status"] == "structured_blocker"
    assert payload["release_warning_gate"]["unresolved"]
    assert payload["summary"]["observed_warning_count"] > payload["summary"]["warning_budget"]


def test_v278_zero_warning_gate_is_accepted(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    payload = CIWarningReductionService(workspace, workspace_id="v278").build_warning_reduction(codebase_id, command_results={"observed_warning_count": 0, "warning_budget": 2, "warnings": []})

    assert payload["release_warning_gate"]["status"] == "accepted"
    assert payload["summary"]["observed_warning_count"] <= payload["summary"]["warning_budget"]
