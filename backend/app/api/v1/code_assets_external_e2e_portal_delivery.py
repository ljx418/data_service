"""HTTP routes for V2.63-V2.70 external E2E portal delivery stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse

from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.code_assets.external_e2e_portal_delivery.contract_regression import PublicSurfaceContractRegressionService, public_contract_regression_payload
from data_service.code_assets.external_e2e_portal_delivery.delivery import DeliveryCleanupVersioningService, public_delivery_payload
from data_service.code_assets.external_e2e_portal_delivery.external_e2e import ExternalProjectFullE2EService, public_external_e2e_payload
from data_service.code_assets.external_e2e_portal_delivery.maintainer_dashboard import MaintainerHomeStatusDashboardService, public_dashboard_payload
from data_service.code_assets.external_e2e_portal_delivery.path_binding import ExternalRepositoryPathBindingService, public_path_binding_payload
from data_service.code_assets.external_e2e_portal_delivery.portal_v3 import PortalV3ExperienceService, public_portal_v3_payload
from data_service.code_assets.external_e2e_portal_delivery.surface_baseline import VersionedPublicSurfaceBaselineService, public_surface_baseline_payload
from data_service.code_assets.external_e2e_portal_delivery.worktree_delivery import WorktreeDeliveryConsolidationService, public_worktree_delivery_payload
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["External E2E Portal Delivery"], dependencies=[Depends(verify_knowledge_access)])


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/e2e/build")
async def build_external_e2e(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = ExternalProjectFullE2EService(workspace, workspace_id=str(meta["workspace_id"])).build_e2e(codebase_id, projects=list((payload or {}).get("projects") or []))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_e2e_build")
    data = {"external_e2e_portal_delivery_e2e": public_external_e2e_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_e2e_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/e2e")
async def read_external_e2e(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = ExternalProjectFullE2EService(workspace, workspace_id=str(meta["workspace_id"])).read_e2e(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_e2e_build")
    data = {"external_e2e_portal_delivery_e2e": public_external_e2e_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.post("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/portal/build")
async def build_portal_v3(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = PortalV3ExperienceService(workspace, workspace_id=str(meta["workspace_id"])).build_portal(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_portal_build")
    data = {"external_e2e_portal_delivery_portal": public_portal_v3_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_portal_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/portal")
async def read_portal_v3(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = PortalV3ExperienceService(workspace, workspace_id=str(meta["workspace_id"])).read_portal(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_portal_build")
    data = {"external_e2e_portal_delivery_portal": public_portal_v3_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/portal/view")
async def view_portal_v3(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = PortalV3ExperienceService(workspace, workspace_id=str(meta["workspace_id"])).read_portal(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_portal_build")
    return HTMLResponse(content=str(result.get("project_portal_v3_plus_html") or ""), status_code=200)


@router.post("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/delivery/build")
async def build_delivery(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = DeliveryCleanupVersioningService(workspace, workspace_id=str(meta["workspace_id"])).build_delivery(codebase_id, repo_root=(payload or {}).get("repo_root"))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_delivery_build")
    data = {"external_e2e_portal_delivery_delivery": public_delivery_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_delivery_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/delivery")
async def read_delivery(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = DeliveryCleanupVersioningService(workspace, workspace_id=str(meta["workspace_id"])).read_delivery(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_delivery_build")
    data = {"external_e2e_portal_delivery_delivery": public_delivery_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.post("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/contract/build")
async def build_contract(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = PublicSurfaceContractRegressionService(workspace, workspace_id=str(meta["workspace_id"])).build_contract(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_contract_build")
    data = {"external_e2e_portal_delivery_contract": public_contract_regression_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_contract_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/contract")
async def read_contract(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = PublicSurfaceContractRegressionService(workspace, workspace_id=str(meta["workspace_id"])).read_contract(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_contract_build")
    data = {"external_e2e_portal_delivery_contract": public_contract_regression_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.post("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/path-binding/build")
async def build_path_binding(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = ExternalRepositoryPathBindingService(workspace, workspace_id=str(meta["workspace_id"])).build_path_binding(
            codebase_id,
            projects=list((payload or {}).get("projects") or []),
            search_roots=list((payload or {}).get("search_roots") or []),
        )
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_path_binding_build")
    data = {"external_e2e_portal_delivery_path_binding": public_path_binding_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_path_binding_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/path-binding")
async def read_path_binding(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = ExternalRepositoryPathBindingService(workspace, workspace_id=str(meta["workspace_id"])).read_path_binding(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_path_binding_build")
    data = {"external_e2e_portal_delivery_path_binding": public_path_binding_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.post("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/worktree-delivery/build")
async def build_worktree_delivery(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = WorktreeDeliveryConsolidationService(workspace, workspace_id=str(meta["workspace_id"])).build_worktree_delivery(codebase_id, repo_root=(payload or {}).get("repo_root"))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_worktree_delivery_build")
    data = {"external_e2e_portal_delivery_worktree_delivery": public_worktree_delivery_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_worktree_delivery_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/worktree-delivery")
async def read_worktree_delivery(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = WorktreeDeliveryConsolidationService(workspace, workspace_id=str(meta["workspace_id"])).read_worktree_delivery(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_worktree_delivery_build")
    data = {"external_e2e_portal_delivery_worktree_delivery": public_worktree_delivery_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.post("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/surface-baseline/build")
async def build_surface_baseline(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = VersionedPublicSurfaceBaselineService(workspace, workspace_id=str(meta["workspace_id"])).build_surface_baseline(codebase_id, baseline_label=str((payload or {}).get("baseline_label") or "v2.67-70"))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_surface_baseline_build")
    data = {"external_e2e_portal_delivery_surface_baseline": public_surface_baseline_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_surface_baseline_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/surface-baseline")
async def read_surface_baseline(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = VersionedPublicSurfaceBaselineService(workspace, workspace_id=str(meta["workspace_id"])).read_surface_baseline(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_surface_baseline_build")
    data = {"external_e2e_portal_delivery_surface_baseline": public_surface_baseline_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.post("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/dashboard/build")
async def build_dashboard(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = MaintainerHomeStatusDashboardService(workspace, workspace_id=str(meta["workspace_id"])).build_dashboard(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_dashboard_build")
    data = {"external_e2e_portal_delivery_dashboard": public_dashboard_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_dashboard_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/dashboard")
async def read_dashboard(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = MaintainerHomeStatusDashboardService(workspace, workspace_id=str(meta["workspace_id"])).read_dashboard(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_dashboard_build")
    data = {"external_e2e_portal_delivery_dashboard": public_dashboard_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/dashboard/view")
async def view_dashboard(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = MaintainerHomeStatusDashboardService(workspace, workspace_id=str(meta["workspace_id"])).read_dashboard(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_external_e2e_portal_delivery_dashboard_build")
    return HTMLResponse(content=str(result.get("maintainer_home_html") or ""), status_code=200)


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body


def _error(status_code: int, workspace_id: str, codebase_id: str, error: str, next_action: str):
    payload = {"v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=error, message=error, next_actions=[next_action])}
    return JSONResponse(status_code=status_code, content=payload)
