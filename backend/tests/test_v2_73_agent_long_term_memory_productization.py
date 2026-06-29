from data_service.code_assets.agent_memory_release.agent_memory import AgentMemoryService
from data_service.code_assets.agent_memory_release.ci_warning_governance import CIWarningGovernanceService
from data_service.code_assets.agent_memory_release.external_project_closure import ExternalProjectClosureService
from data_service.code_assets.external_e2e_portal_delivery.path_binding import ExternalRepositoryPathBindingService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V273\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v273"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v273").import_codebase(path=str(repo), name="V273")["asset"].codebase_id
    return workspace, codebase_id


def test_v273_agent_memory_has_source_artifacts_and_evidence(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    ExternalRepositoryPathBindingService(workspace, workspace_id="v273").build_path_binding(codebase_id)
    ExternalProjectClosureService(workspace, workspace_id="v273").build_external_project_closure(codebase_id)
    CIWarningGovernanceService(workspace, workspace_id="v273").build_ci_warning_governance(codebase_id)

    payload = AgentMemoryService(workspace, workspace_id="v273").build_agent_memory(codebase_id)

    assert all(item["source_artifact_ref"] for item in payload["memory_index"]["items"])
    assert all(item["evidence_refs"] or item["status"] == "needs_review" for item in payload["task_briefing"]["recommendations"])
    assert "not generic chat memory" in payload["retention_policy"] or "not generic chat" in payload["retention_policy"].lower()


def test_v273_agent_memory_readback(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = AgentMemoryService(workspace, workspace_id="v273")
    service.build_agent_memory(codebase_id)

    assert service.read_agent_memory(codebase_id)["artifact_type"] == "agent_long_term_memory"

