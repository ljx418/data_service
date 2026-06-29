"""HTTP routes for V2.76-V2.80 project acceptance hardening stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.code_assets.project_acceptance_hardening.console_productization import MaintainerConsoleProductizationService, public_console_product_payload
from data_service.code_assets.project_acceptance_hardening.external_project_binding import ExternalProjectRealBindingService, public_external_binding_payload
from data_service.code_assets.project_acceptance_hardening.matrix_reconciliation import AcceptanceMatrixReconciliationService, public_matrix_reconciliation_payload
from data_service.code_assets.project_acceptance_hardening.release_readiness import ReleaseReadinessClosureService, public_release_readiness_payload
from data_service.code_assets.project_acceptance_hardening.warning_reduction import CIWarningReductionService, public_warning_reduction_payload
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Project Acceptance Hardening"], dependencies=[Depends(verify_knowledge_access)])


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/matrix/build")
async def build_matrix(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = AcceptanceMatrixReconciliationService(workspace, workspace_id=str(meta["workspace_id"])).build_reconciliation(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_project_acceptance_hardening_matrix_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "project_acceptance_hardening_matrix", public_matrix_reconciliation_payload, "knowledge_code_project_acceptance_hardening_matrix_read")


@router.get("/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/matrix")
async def read_matrix(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = AcceptanceMatrixReconciliationService(workspace, workspace_id=str(meta["workspace_id"])).read_reconciliation(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_project_acceptance_hardening_matrix_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "project_acceptance_hardening_matrix", public_matrix_reconciliation_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/external-binding/build")
async def build_external_binding(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = ExternalProjectRealBindingService(workspace, workspace_id=str(meta["workspace_id"])).build_external_binding(codebase_id, project_paths=list((payload or {}).get("project_paths") or []))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_project_acceptance_hardening_external_binding_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "project_acceptance_hardening_external_binding", public_external_binding_payload, "knowledge_code_project_acceptance_hardening_external_binding_read")


@router.get("/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/external-binding")
async def read_external_binding(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = ExternalProjectRealBindingService(workspace, workspace_id=str(meta["workspace_id"])).read_external_binding(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_project_acceptance_hardening_external_binding_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "project_acceptance_hardening_external_binding", public_external_binding_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/warning-reduction/build")
async def build_warning_reduction(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = CIWarningReductionService(workspace, workspace_id=str(meta["workspace_id"])).build_warning_reduction(codebase_id, command_results=dict((payload or {}).get("command_results") or {}))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_project_acceptance_hardening_warning_reduction_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "project_acceptance_hardening_warning_reduction", public_warning_reduction_payload, "knowledge_code_project_acceptance_hardening_warning_reduction_read")


@router.get("/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/warning-reduction")
async def read_warning_reduction(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = CIWarningReductionService(workspace, workspace_id=str(meta["workspace_id"])).read_warning_reduction(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_project_acceptance_hardening_warning_reduction_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "project_acceptance_hardening_warning_reduction", public_warning_reduction_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/console-product/build")
async def build_console_product(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = MaintainerConsoleProductizationService(workspace, workspace_id=str(meta["workspace_id"])).build_console_product(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_project_acceptance_hardening_console_product_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "project_acceptance_hardening_console_product", public_console_product_payload, "knowledge_code_project_acceptance_hardening_console_product_read")


@router.get("/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/console-product")
async def read_console_product(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = MaintainerConsoleProductizationService(workspace, workspace_id=str(meta["workspace_id"])).read_console_product(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_project_acceptance_hardening_console_product_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "project_acceptance_hardening_console_product", public_console_product_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/release-readiness/build")
async def build_release_readiness(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = ReleaseReadinessClosureService(workspace, workspace_id=str(meta["workspace_id"])).build_release_readiness(codebase_id, approval_state=dict((payload or {}).get("approval_state") or {}))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_project_acceptance_hardening_release_readiness_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "project_acceptance_hardening_release_readiness", public_release_readiness_payload, "knowledge_code_project_acceptance_hardening_release_readiness_read")


@router.get("/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/release-readiness")
async def read_release_readiness(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = ReleaseReadinessClosureService(workspace, workspace_id=str(meta["workspace_id"])).read_release_readiness(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_project_acceptance_hardening_release_readiness_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "project_acceptance_hardening_release_readiness", public_release_readiness_payload)


def _ok(workspace_id: str, codebase_id: str, result: dict[str, Any], key: str, public_payload, next_action: str | None = None):
    data = {key: public_payload(result)}
    next_actions = [next_action] if next_action else None
    return envelope(workspace_id=workspace_id, artifact_refs=result.get("artifact_refs", []), next_actions=next_actions, data=_with_v2(workspace_id, codebase_id, data, result))


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body


def _error(status_code: int, workspace_id: str, codebase_id: str, error: str, next_action: str):
    payload = {"v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=error, message=error, next_actions=[next_action])}
    return JSONResponse(status_code=status_code, content=payload)
