"""HTTP routes for V2.96-V2.100 automated evidence closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from data_service.code_assets.automated_evidence_closure.cli_gap import DefaultCliGapClosure, public_cli_gap_payload
from data_service.code_assets.automated_evidence_closure.external_path_registry import ExternalProjectPathRegistry, public_external_path_payload
from data_service.code_assets.automated_evidence_closure.quality_workbench import QualityDecisionWorkbench, public_quality_workbench_payload
from data_service.code_assets.automated_evidence_closure.release_evidence_gate import AutomatedReleaseEvidenceGate, public_release_gate_payload
from data_service.code_assets.automated_evidence_closure.route_a_evidence import RouteAEvidenceAutomator, public_route_a_evidence_payload
from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Automated Evidence Closure"], dependencies=[Depends(verify_knowledge_access)])


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/automated-evidence-closure/cli-gap/build")
async def build_cli_gap(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "automated_evidence_cli_gap", "knowledge_code_automated_evidence_closure_cli_gap_read", lambda workspace, meta: DefaultCliGapClosure(workspace, workspace_id=str(meta["workspace_id"])).build_cli_gap(codebase_id, cli_state=dict((payload or {}).get("cli_state") or {})), public_cli_gap_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/automated-evidence-closure/cli-gap")
async def read_cli_gap(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "automated_evidence_cli_gap", None, lambda workspace, meta: DefaultCliGapClosure(workspace, workspace_id=str(meta["workspace_id"])).read_cli_gap(codebase_id), public_cli_gap_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/automated-evidence-closure/route-a-evidence/build")
async def build_route_a_evidence(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "automated_evidence_route_a", "knowledge_code_automated_evidence_closure_route_a_evidence_read", lambda workspace, meta: RouteAEvidenceAutomator(workspace, workspace_id=str(meta["workspace_id"])).build_route_a_evidence(codebase_id, material_state=dict((payload or {}).get("material_state") or {})), public_route_a_evidence_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/automated-evidence-closure/route-a-evidence")
async def read_route_a_evidence(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "automated_evidence_route_a", None, lambda workspace, meta: RouteAEvidenceAutomator(workspace, workspace_id=str(meta["workspace_id"])).read_route_a_evidence(codebase_id), public_route_a_evidence_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/automated-evidence-closure/quality-workbench/build")
async def build_quality_workbench(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "automated_evidence_quality_workbench", "knowledge_code_automated_evidence_closure_quality_workbench_read", lambda workspace, meta: QualityDecisionWorkbench(workspace, workspace_id=str(meta["workspace_id"])).build_quality_workbench(codebase_id, decision_state=dict((payload or {}).get("decision_state") or {})), public_quality_workbench_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/automated-evidence-closure/quality-workbench")
async def read_quality_workbench(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "automated_evidence_quality_workbench", None, lambda workspace, meta: QualityDecisionWorkbench(workspace, workspace_id=str(meta["workspace_id"])).read_quality_workbench(codebase_id), public_quality_workbench_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/automated-evidence-closure/external-path/build")
async def build_external_path(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "automated_evidence_external_path", "knowledge_code_automated_evidence_closure_external_path_read", lambda workspace, meta: ExternalProjectPathRegistry(workspace, workspace_id=str(meta["workspace_id"])).build_external_path(codebase_id, project_state=dict((payload or {}).get("project_state") or {})), public_external_path_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/automated-evidence-closure/external-path")
async def read_external_path(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "automated_evidence_external_path", None, lambda workspace, meta: ExternalProjectPathRegistry(workspace, workspace_id=str(meta["workspace_id"])).read_external_path(codebase_id), public_external_path_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/automated-evidence-closure/release-gate/build")
async def build_release_gate(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "automated_evidence_release_gate", "knowledge_code_automated_evidence_closure_release_gate_read", lambda workspace, meta: AutomatedReleaseEvidenceGate(workspace, workspace_id=str(meta["workspace_id"])).build_release_gate(codebase_id, gate_state=dict((payload or {}).get("gate_state") or {})), public_release_gate_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/automated-evidence-closure/release-gate")
async def read_release_gate(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "automated_evidence_release_gate", None, lambda workspace, meta: AutomatedReleaseEvidenceGate(workspace, workspace_id=str(meta["workspace_id"])).read_release_gate(codebase_id), public_release_gate_payload)


def _run(workspace_id: str, codebase_id: str, key: str, next_action: str | None, callback: Callable[[Path, dict[str, Any]], dict[str, Any]], public: Callable[[dict[str, Any]], dict[str, Any]]):
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
    if "CLI_GAP" in message:
        return "knowledge_code_automated_evidence_closure_cli_gap_build"
    if "ROUTE_A" in message:
        return "knowledge_code_automated_evidence_closure_route_a_evidence_build"
    if "QUALITY" in message:
        return "knowledge_code_automated_evidence_closure_quality_workbench_build"
    if "EXTERNAL" in message:
        return "knowledge_code_automated_evidence_closure_external_path_build"
    return "knowledge_code_automated_evidence_closure_release_gate_build"

