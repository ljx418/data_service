from data_service.code_assets.external_e2e_portal_delivery.external_e2e import ExternalProjectFullE2EService
from data_service.code_assets.external_e2e_portal_delivery.maintainer_dashboard import MaintainerHomeStatusDashboardService
from data_service.code_assets.external_e2e_portal_delivery.path_binding import ExternalRepositoryPathBindingService
from data_service.code_assets.external_e2e_portal_delivery.portal_v3 import PortalV3ExperienceService
from data_service.code_assets.external_e2e_portal_delivery.surface_baseline import VersionedPublicSurfaceBaselineService
from data_service.code_assets.external_e2e_portal_delivery.worktree_delivery import WorktreeDeliveryConsolidationService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V270\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v270"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v270").import_codebase(path=str(repo), name="V270")["asset"].codebase_id
    return repo, workspace, codebase_id


def test_v270_dashboard_preserves_non_accepted_statuses(tmp_path, monkeypatch):
    repo, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    ExternalProjectFullE2EService(workspace, workspace_id="v270").build_e2e(codebase_id)
    ExternalRepositoryPathBindingService(workspace, workspace_id="v270").build_path_binding(codebase_id)
    WorktreeDeliveryConsolidationService(workspace, workspace_id="v270").build_worktree_delivery(codebase_id, repo_root=str(repo))
    VersionedPublicSurfaceBaselineService(workspace, workspace_id="v270").build_surface_baseline(codebase_id)
    PortalV3ExperienceService(workspace, workspace_id="v270").build_portal(codebase_id)
    payload = MaintainerHomeStatusDashboardService(workspace, workspace_id="v270").build_dashboard(codebase_id)
    panels = payload["maintainer_status_panels"]["sections"]
    assert payload["summary"]["panel_count"] == 5
    assert payload["summary"]["non_accepted_panel_count"] >= 1
    assert any(item["status"] in {"structured_unavailable", "needs_review"} for item in panels)
    assert "非 accepted 状态不会被隐藏" in payload["maintainer_home_html"]


def test_v270_dashboard_readback(tmp_path, monkeypatch):
    _repo, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = MaintainerHomeStatusDashboardService(workspace, workspace_id="v270")
    service.build_dashboard(codebase_id)
    assert service.read_dashboard(codebase_id)["artifact_type"] == "maintainer_home_status_dashboard"
