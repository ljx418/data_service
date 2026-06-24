from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.stabilization_e2e_portal.e2e_expansion import RealProjectE2EExpansionService
from data_service.code_assets.stabilization_e2e_portal.packaging import AcceptancePackagingService
from data_service.code_assets.stabilization_e2e_portal.portal_integration import PortalUXIntegrationService
from data_service.code_assets.stabilization_e2e_portal.public_surface import PublicSurfaceStabilizationService


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V262\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v262"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v262").import_codebase(path=str(repo), name="V262")["asset"].codebase_id
    return repo, workspace, codebase_id


def test_v262_portal_uses_persisted_artifacts_and_preserves_statuses(tmp_path, monkeypatch):
    repo, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    PublicSurfaceStabilizationService(workspace, workspace_id="v262").build_surface(codebase_id)
    RealProjectE2EExpansionService(workspace, workspace_id="v262").build_e2e(codebase_id, projects=[{"name": "Navia", "path": str(repo / "missing")}])
    AcceptancePackagingService(workspace, workspace_id="v262").build_package(codebase_id, repo_root=str(repo))
    payload = PortalUXIntegrationService(workspace, workspace_id="v262").build_portal(codebase_id)
    state = payload["portal_state_summary"]
    assert state["contract_stability"] in {"accepted", "needs_review"}
    assert state["e2e_coverage"] == "structured_unavailable"
    assert state["delivery_readiness"] == "accepted"
    assert payload["summary"]["raw_mermaid_visible"] is False
    statuses = {item["status"] for item in payload["portal_acceptance_panel"]["items"]}
    assert "structured_unavailable" in statuses
    assert "accepted" in statuses
    assert "structured_unavailable" in payload["project_portal_v3_html"]


def test_v262_portal_readback(tmp_path, monkeypatch):
    repo, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    PublicSurfaceStabilizationService(workspace, workspace_id="v262").build_surface(codebase_id)
    RealProjectE2EExpansionService(workspace, workspace_id="v262").build_e2e(codebase_id)
    AcceptancePackagingService(workspace, workspace_id="v262").build_package(codebase_id, repo_root=str(repo))
    service = PortalUXIntegrationService(workspace, workspace_id="v262")
    service.build_portal(codebase_id)
    assert service.read_portal(codebase_id)["summary"]["section_count"] == 4
