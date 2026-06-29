from data_service.code_assets.agent_memory_release.agent_memory import AgentMemoryService
from data_service.code_assets.agent_memory_release.ci_warning_governance import CIWarningGovernanceService
from data_service.code_assets.agent_memory_release.external_project_closure import ExternalProjectClosureService
from data_service.code_assets.agent_memory_release.release_restore import ReleaseRestoreService
from data_service.code_assets.external_e2e_portal_delivery.path_binding import ExternalRepositoryPathBindingService
from data_service.code_assets.project_acceptance_hardening.console_productization import MaintainerConsoleProductizationService
from data_service.code_assets.project_acceptance_hardening.external_project_binding import ExternalProjectRealBindingService
from data_service.code_assets.project_acceptance_hardening.matrix_reconciliation import AcceptanceMatrixReconciliationService
from data_service.code_assets.project_acceptance_hardening.release_readiness import ReleaseReadinessClosureService
from data_service.code_assets.project_acceptance_hardening.warning_reduction import CIWarningReductionService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V280\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v280"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v280").import_codebase(path=str(repo), name="V280")["asset"].codebase_id
    return workspace, codebase_id


def test_v280_release_readiness_keeps_human_approval_open(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    ExternalRepositoryPathBindingService(workspace, workspace_id="v280").build_path_binding(codebase_id)
    ExternalProjectClosureService(workspace, workspace_id="v280").build_external_project_closure(codebase_id)
    CIWarningGovernanceService(workspace, workspace_id="v280").build_ci_warning_governance(codebase_id)
    AgentMemoryService(workspace, workspace_id="v280").build_agent_memory(codebase_id)
    ReleaseRestoreService(workspace, workspace_id="v280").build_release_restore(codebase_id)
    AcceptanceMatrixReconciliationService(workspace, workspace_id="v280").build_reconciliation(codebase_id)
    ExternalProjectRealBindingService(workspace, workspace_id="v280").build_external_binding(codebase_id)
    CIWarningReductionService(workspace, workspace_id="v280").build_warning_reduction(codebase_id, command_results={"observed_warning_count": 0, "warning_budget": 1})
    MaintainerConsoleProductizationService(workspace, workspace_id="v280").build_console_product(codebase_id)

    payload = ReleaseReadinessClosureService(workspace, workspace_id="v280").build_release_readiness(codebase_id)
    checks = {check["id"]: check for check in payload["readiness_gate"]["checks"]}

    assert payload["artifact_type"] == "release_readiness_closure"
    assert checks["human_approval"]["status"] == "needs_review"
    assert payload["readiness_gate"]["readiness_status"] != "accepted"
    assert "pytest -q" in payload["smoke_run_records"]["commands"]
    assert payload["unresolved"]


def test_v280_release_readiness_readback(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = ReleaseReadinessClosureService(workspace, workspace_id="v280")
    service.build_release_readiness(codebase_id)

    assert service.read_release_readiness(codebase_id)["artifact_type"] == "release_readiness_closure"
