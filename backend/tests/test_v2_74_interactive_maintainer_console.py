from data_service.code_assets.agent_memory_release.agent_memory import AgentMemoryService
from data_service.code_assets.agent_memory_release.ci_warning_governance import CIWarningGovernanceService
from data_service.code_assets.agent_memory_release.external_project_closure import ExternalProjectClosureService
from data_service.code_assets.agent_memory_release.interactive_console import InteractiveMaintainerConsoleService
from data_service.code_assets.external_e2e_portal_delivery.path_binding import ExternalRepositoryPathBindingService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V274\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v274"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v274").import_codebase(path=str(repo), name="V274")["asset"].codebase_id
    return workspace, codebase_id


def test_v274_console_preserves_non_accepted_statuses(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    ExternalRepositoryPathBindingService(workspace, workspace_id="v274").build_path_binding(codebase_id)
    ExternalProjectClosureService(workspace, workspace_id="v274").build_external_project_closure(codebase_id)
    CIWarningGovernanceService(workspace, workspace_id="v274").build_ci_warning_governance(codebase_id, command_results={"observed_warning_count": 500, "warning_budget": 100})
    AgentMemoryService(workspace, workspace_id="v274").build_agent_memory(codebase_id)

    payload = InteractiveMaintainerConsoleService(workspace, workspace_id="v274").build_interactive_console(codebase_id)
    panels = payload["status_panels"]["sections"]

    assert all(item["status"] for item in panels)
    assert all(item["artifact_refs"] or item["evidence_refs"] or item["unresolved"] for item in panels)
    assert payload["summary"]["panel_count"] == 5
    assert payload["summary"]["stage_status"] != "accepted"
    assert "structured_unavailable" in payload["maintainer_console_html"] or "needs_review" in payload["maintainer_console_html"]


def test_v274_console_readback(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = InteractiveMaintainerConsoleService(workspace, workspace_id="v274")
    service.build_interactive_console(codebase_id)

    assert service.read_interactive_console(codebase_id)["artifact_type"] == "interactive_maintainer_console"

