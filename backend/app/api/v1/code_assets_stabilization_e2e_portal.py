"""HTTP routes for V2.59-V2.62 stabilization stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse

from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.code_assets.stabilization_e2e_portal.e2e_expansion import RealProjectE2EExpansionService, public_e2e_payload
from data_service.code_assets.stabilization_e2e_portal.packaging import AcceptancePackagingService, public_package_payload
from data_service.code_assets.stabilization_e2e_portal.portal_integration import PortalUXIntegrationService, public_portal_payload
from data_service.code_assets.stabilization_e2e_portal.public_surface import PublicSurfaceStabilizationService, public_surface_payload
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Stabilization E2E Portal"], dependencies=[Depends(verify_knowledge_access)])


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/surface/build")
async def build_surface(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        payload = PublicSurfaceStabilizationService(workspace, workspace_id=str(meta["workspace_id"])).build_surface(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_stabilization_surface_build")
    data = {"stabilization_surface": public_surface_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_stabilization_surface_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.get("/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/surface")
async def read_surface(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        payload = PublicSurfaceStabilizationService(workspace, workspace_id=str(meta["workspace_id"])).read_surface(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_stabilization_surface_build")
    data = {"stabilization_surface": public_surface_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.post("/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/e2e/build")
async def build_e2e(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = RealProjectE2EExpansionService(workspace, workspace_id=str(meta["workspace_id"])).build_e2e(codebase_id, projects=list((payload or {}).get("projects") or []))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_stabilization_e2e_build")
    data = {"stabilization_e2e": public_e2e_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_stabilization_e2e_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/e2e")
async def read_e2e(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = RealProjectE2EExpansionService(workspace, workspace_id=str(meta["workspace_id"])).read_e2e(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_stabilization_e2e_build")
    data = {"stabilization_e2e": public_e2e_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.post("/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/package/build")
async def build_package(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = AcceptancePackagingService(workspace, workspace_id=str(meta["workspace_id"])).build_package(codebase_id, repo_root=(payload or {}).get("repo_root"))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_stabilization_package_build")
    data = {"stabilization_package": public_package_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_stabilization_package_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/package")
async def read_package(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = AcceptancePackagingService(workspace, workspace_id=str(meta["workspace_id"])).read_package(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_stabilization_package_build")
    data = {"stabilization_package": public_package_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.post("/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/portal/build")
async def build_portal(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = PortalUXIntegrationService(workspace, workspace_id=str(meta["workspace_id"])).build_portal(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_stabilization_portal_build")
    data = {"stabilization_portal": public_portal_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_stabilization_portal_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/portal")
async def read_portal(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = PortalUXIntegrationService(workspace, workspace_id=str(meta["workspace_id"])).read_portal(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_stabilization_portal_build")
    data = {"stabilization_portal": public_portal_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/portal/view")
async def view_portal(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = PortalUXIntegrationService(workspace, workspace_id=str(meta["workspace_id"])).read_portal(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_stabilization_portal_build")
    return HTMLResponse(content=str(result.get("project_portal_v3_html") or ""), status_code=200)


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body


def _error(status_code: int, workspace_id: str, codebase_id: str, error: str, next_action: str):
    payload = {"v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=error, message=error, next_actions=[next_action])}
    return JSONResponse(status_code=status_code, content=payload)
