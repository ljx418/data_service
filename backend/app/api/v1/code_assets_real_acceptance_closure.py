"""HTTP routes for V2.91-V2.95 real acceptance closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.code_assets.real_acceptance_closure.external_project_validator import ExternalProjectPathE2EValidator, public_external_project_closure_payload
from data_service.code_assets.real_acceptance_closure.quality_decision import HumanQualityDecisionRecorder, public_quality_decision_payload
from data_service.code_assets.real_acceptance_closure.release_finalizer import FinalReleaseGateFinalizer, public_release_finalizer_payload
from data_service.code_assets.real_acceptance_closure.route_a_material import RouteAMaterialIntakeReview, public_route_a_closure_payload
from data_service.code_assets.real_acceptance_closure.runtime_restore import AcceptanceRuntimeRestorer, public_runtime_restore_payload
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Real Acceptance Closure"], dependencies=[Depends(verify_knowledge_access)])


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/runtime-restore/build")
async def build_runtime_restore(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "real_acceptance_runtime_restore", "knowledge_code_real_acceptance_closure_runtime_restore_read", lambda workspace, meta: AcceptanceRuntimeRestorer(workspace, workspace_id=str(meta["workspace_id"])).build_runtime_restore(codebase_id, runtime_state=dict((payload or {}).get("runtime_state") or {})), public_runtime_restore_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/runtime-restore")
async def read_runtime_restore(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_acceptance_runtime_restore", None, lambda workspace, meta: AcceptanceRuntimeRestorer(workspace, workspace_id=str(meta["workspace_id"])).read_runtime_restore(codebase_id), public_runtime_restore_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/route-a-closure/build")
async def build_route_a_closure(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "real_acceptance_route_a_closure", "knowledge_code_real_acceptance_closure_route_a_closure_read", lambda workspace, meta: RouteAMaterialIntakeReview(workspace, workspace_id=str(meta["workspace_id"])).build_route_a_closure(codebase_id, material_state=dict((payload or {}).get("material_state") or {})), public_route_a_closure_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/route-a-closure")
async def read_route_a_closure(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_acceptance_route_a_closure", None, lambda workspace, meta: RouteAMaterialIntakeReview(workspace, workspace_id=str(meta["workspace_id"])).read_route_a_closure(codebase_id), public_route_a_closure_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/quality-decision/build")
async def build_quality_decision(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "real_acceptance_quality_decision", "knowledge_code_real_acceptance_closure_quality_decision_read", lambda workspace, meta: HumanQualityDecisionRecorder(workspace, workspace_id=str(meta["workspace_id"])).build_quality_decision(codebase_id, decision_state=dict((payload or {}).get("decision_state") or {})), public_quality_decision_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/quality-decision")
async def read_quality_decision(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_acceptance_quality_decision", None, lambda workspace, meta: HumanQualityDecisionRecorder(workspace, workspace_id=str(meta["workspace_id"])).read_quality_decision(codebase_id), public_quality_decision_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/external-project-closure/build")
async def build_external_project_closure(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "real_acceptance_external_project_closure", "knowledge_code_real_acceptance_closure_external_project_closure_read", lambda workspace, meta: ExternalProjectPathE2EValidator(workspace, workspace_id=str(meta["workspace_id"])).build_external_project_closure(codebase_id, project_state=dict((payload or {}).get("project_state") or {})), public_external_project_closure_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/external-project-closure")
async def read_external_project_closure(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_acceptance_external_project_closure", None, lambda workspace, meta: ExternalProjectPathE2EValidator(workspace, workspace_id=str(meta["workspace_id"])).read_external_project_closure(codebase_id), public_external_project_closure_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/release-finalizer/build")
async def build_release_finalizer(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "real_acceptance_release_finalizer", "knowledge_code_real_acceptance_closure_release_finalizer_read", lambda workspace, meta: FinalReleaseGateFinalizer(workspace, workspace_id=str(meta["workspace_id"])).build_release_finalizer(codebase_id, gate_state=dict((payload or {}).get("gate_state") or {})), public_release_finalizer_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/release-finalizer")
async def read_release_finalizer(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_acceptance_release_finalizer", None, lambda workspace, meta: FinalReleaseGateFinalizer(workspace, workspace_id=str(meta["workspace_id"])).read_release_finalizer(codebase_id), public_release_finalizer_payload)


def _run(workspace_id: str, codebase_id: str, key: str, next_action: str | None, callback, public):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = callback(workspace, meta)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), _next_action_for(str(exc)))
    data = {key: public(result)}
    next_actions = [next_action] if next_action else None
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=next_actions, data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body


def _error(status_code: int, workspace_id: str, codebase_id: str, error: str, next_action: str):
    payload = {"v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=error, message=error, next_actions=[next_action])}
    return JSONResponse(status_code=status_code, content=payload)


def _next_action_for(message: str) -> str:
    if "RUNTIME" in message:
        return "knowledge_code_real_acceptance_closure_runtime_restore_build"
    if "ROUTE_A" in message:
        return "knowledge_code_real_acceptance_closure_route_a_closure_build"
    if "QUALITY" in message:
        return "knowledge_code_real_acceptance_closure_quality_decision_build"
    if "EXTERNAL" in message:
        return "knowledge_code_real_acceptance_closure_external_project_closure_build"
    return "knowledge_code_real_acceptance_closure_release_finalizer_build"
