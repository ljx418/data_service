from data_service.code_assets.agent_memory_release.agent_memory import AgentMemoryService
from data_service.code_assets.agent_memory_release.ci_warning_governance import CIWarningGovernanceService
from data_service.code_assets.agent_memory_release.external_project_closure import ExternalProjectClosureService
from data_service.code_assets.agent_memory_release.interactive_console import InteractiveMaintainerConsoleService
from data_service.code_assets.agent_memory_release.release_restore import ReleaseRestoreService
from data_service.code_assets.external_e2e_portal_delivery.path_binding import ExternalRepositoryPathBindingService
from data_service.code_assets.project_acceptance_hardening.matrix_reconciliation import AcceptanceMatrixReconciliationService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V276\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v276"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v276").import_codebase(path=str(repo), name="V276")["asset"].codebase_id
    return workspace, codebase_id


def test_v276_reconciles_from_persisted_artifacts_not_document_claims(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    ExternalRepositoryPathBindingService(workspace, workspace_id="v276").build_path_binding(codebase_id)
    ExternalProjectClosureService(workspace, workspace_id="v276").build_external_project_closure(codebase_id)
    CIWarningGovernanceService(workspace, workspace_id="v276").build_ci_warning_governance(codebase_id)
    AgentMemoryService(workspace, workspace_id="v276").build_agent_memory(codebase_id)
    InteractiveMaintainerConsoleService(workspace, workspace_id="v276").build_interactive_console(codebase_id)
    ReleaseRestoreService(workspace, workspace_id="v276").build_release_restore(codebase_id)

    payload = AcceptanceMatrixReconciliationService(workspace, workspace_id="v276").build_reconciliation(codebase_id)
    rows = payload["reconciled_matrix"]["rows"]

    assert payload["artifact_type"] == "acceptance_matrix_reconciliation"
    assert rows
    assert all(row["decision_basis"] != "documentation claim" for row in rows)
    assert all(row["status"] != "accepted" or row["evidence_refs"] for row in rows)
    assert payload["status_diff"]["summary"]["docs_only_accepted_count"] == 0


def test_v276_reconciliation_readback(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = AcceptanceMatrixReconciliationService(workspace, workspace_id="v276")
    service.build_reconciliation(codebase_id)

    assert service.read_reconciliation(codebase_id)["artifact_type"] == "acceptance_matrix_reconciliation"
