from data_service.code_assets.project_acceptance_hardening.console_productization import MaintainerConsoleProductizationService
from data_service.code_assets.project_acceptance_hardening.external_project_binding import ExternalProjectRealBindingService
from data_service.code_assets.project_acceptance_hardening.matrix_reconciliation import AcceptanceMatrixReconciliationService
from data_service.code_assets.project_acceptance_hardening.warning_reduction import CIWarningReductionService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V279\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v279"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v279").import_codebase(path=str(repo), name="V279")["asset"].codebase_id
    return workspace, codebase_id


def test_v279_console_panels_preserve_non_accepted_states(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    AcceptanceMatrixReconciliationService(workspace, workspace_id="v279").build_reconciliation(codebase_id)
    ExternalProjectRealBindingService(workspace, workspace_id="v279").build_external_binding(codebase_id)
    CIWarningReductionService(workspace, workspace_id="v279").build_warning_reduction(codebase_id, command_results={"observed_warning_count": 5, "warning_budget": 1})

    payload = MaintainerConsoleProductizationService(workspace, workspace_id="v279").build_console_product(codebase_id)
    panels = payload["experience_model"]["panels"]

    assert payload["summary"]["panel_count"] == 5
    assert all(panel["status"] for panel in panels)
    assert all(panel["source_artifact_ref"] for panel in panels)
    assert all(panel["evidence_refs"] or panel["unresolved"] for panel in panels)
    assert payload["summary"]["stage_status"] != "accepted"
    assert any(panel["status"] in {"needs_review", "structured_unavailable", "structured_blocker"} for panel in panels)
