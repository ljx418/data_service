from data_service.code_assets.external_e2e_portal_delivery.external_e2e import ExternalProjectFullE2EService
from data_service.code_assets.external_e2e_portal_delivery.portal_v3 import PortalV3ExperienceService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V264\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v264"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v264").import_codebase(path=str(repo), name="V264")["asset"].codebase_id
    return tmp_path, workspace, codebase_id


def test_v264_portal_preserves_non_accepted_statuses(tmp_path, monkeypatch):
    root, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    ExternalProjectFullE2EService(workspace, workspace_id="v264").build_e2e(codebase_id, projects=[{"name": "Navia", "path": str(root / "missing")}])
    payload = PortalV3ExperienceService(workspace, workspace_id="v264").build_portal(codebase_id)
    panels = payload["status_panels"]["sections"]
    assert {panel["id"] for panel in panels} >= {"stage_overview", "external_e2e", "contract", "delivery", "risk", "exit_status"}
    external = next(panel for panel in panels if panel["id"] == "external_e2e")
    assert external["status"] == "structured_unavailable"
    assert external["unresolved"]
    assert "structured_unavailable" in payload["project_portal_v3_plus_html"]
    assert payload["summary"]["raw_mermaid_visible"] is False


def test_v264_portal_readback(tmp_path, monkeypatch):
    _root, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    ExternalProjectFullE2EService(workspace, workspace_id="v264").build_e2e(codebase_id)
    service = PortalV3ExperienceService(workspace, workspace_id="v264")
    service.build_portal(codebase_id)
    assert service.read_portal(codebase_id)["summary"]["panel_count"] == 6
