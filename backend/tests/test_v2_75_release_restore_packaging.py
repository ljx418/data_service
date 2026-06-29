from data_service.code_assets.agent_memory_release.agent_memory import AgentMemoryService
from data_service.code_assets.agent_memory_release.ci_warning_governance import CIWarningGovernanceService
from data_service.code_assets.agent_memory_release.external_project_closure import ExternalProjectClosureService
from data_service.code_assets.agent_memory_release.release_restore import ReleaseRestoreService
from data_service.code_assets.external_e2e_portal_delivery.path_binding import ExternalRepositoryPathBindingService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V275\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v275"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v275").import_codebase(path=str(repo), name="V275")["asset"].codebase_id
    return workspace, codebase_id


def test_v275_release_restore_redaction_and_smoke_commands(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    ExternalRepositoryPathBindingService(workspace, workspace_id="v275").build_path_binding(codebase_id)
    ExternalProjectClosureService(workspace, workspace_id="v275").build_external_project_closure(codebase_id)
    CIWarningGovernanceService(workspace, workspace_id="v275").build_ci_warning_governance(codebase_id)
    AgentMemoryService(workspace, workspace_id="v275").build_agent_memory(codebase_id)

    payload = ReleaseRestoreService(workspace, workspace_id="v275").build_release_restore(codebase_id)

    assert payload["release_manifest"]["redaction_status"] == "accepted"
    assert "pytest -q" in payload["smoke_commands"]
    assert "curl -s" in payload["smoke_commands"]
    assert "agent-memory-release" in payload["smoke_commands"]
    assert payload["release_manifest"]["readiness_status"] != "accepted"


def test_v275_release_restore_readback(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = ReleaseRestoreService(workspace, workspace_id="v275")
    service.build_release_restore(codebase_id)

    assert service.read_release_restore(codebase_id)["artifact_type"] == "release_restore_packaging"

