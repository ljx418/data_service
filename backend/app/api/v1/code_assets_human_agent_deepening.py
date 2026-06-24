"""HTTP routes for V2.54-V2.58 Human / Agent Deepening artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse

from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.code_assets.human_agent_deepening.evidence_loop import DocCodeEvidenceLoopService, public_doc_code_evidence_loop_payload
from data_service.code_assets.human_agent_deepening.human_portal import HumanPortalDeepeningService, public_human_portal_deepening_payload
from data_service.code_assets.human_agent_deepening.regression import MultiProjectRegressionService, public_regression_payload
from data_service.code_assets.human_agent_deepening.restore_ux import RestoreUXService, public_restore_ux_payload
from data_service.code_assets.human_agent_deepening.task_workflow import AgentTaskWorkflowService, public_agent_task_workflow_payload
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Human Agent Deepening"], dependencies=[Depends(verify_knowledge_access)])


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/portal/build")
async def build_human_agent_deepening_portal(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = HumanPortalDeepeningService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_portal(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc))
    data = {"human_agent_deepening_portal": public_human_portal_deepening_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_human_agent_deepening_portal_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.get("/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/portal")
async def read_human_agent_deepening_portal(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = HumanPortalDeepeningService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_portal(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc))
    data = {"human_agent_deepening_portal": public_human_portal_deepening_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.get("/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/portal/view")
async def view_human_agent_deepening_portal(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = HumanPortalDeepeningService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_portal(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc))
    return HTMLResponse(content=str(payload.get("html") or ""), status_code=200)


@router.post("/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/task-workflow/build")
async def build_human_agent_deepening_task_workflow(workspace_id: str, codebase_id: str, payload: dict[str, Any]):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentTaskWorkflowService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.build_task_workflow(codebase_id, task=str(payload.get("task") or ""), max_tokens=int(payload.get("max_tokens") or 4000))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_human_agent_deepening_task_workflow_build")
    except ValueError as exc:
        return _error(400, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_human_agent_deepening_task_workflow_build")
    data = {"human_agent_deepening_task_workflow": public_agent_task_workflow_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_human_agent_deepening_task_workflow_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/task-workflow/{task_id}")
async def read_human_agent_deepening_task_workflow(workspace_id: str, codebase_id: str, task_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentTaskWorkflowService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.read_task_workflow(codebase_id, task_id=task_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_human_agent_deepening_task_workflow_build")
    data = {"human_agent_deepening_task_workflow": public_agent_task_workflow_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.post("/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/evidence-loop/build")
async def build_human_agent_deepening_evidence_loop(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = DocCodeEvidenceLoopService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.build_evidence_loop(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_human_agent_deepening_evidence_loop_build")
    data = {"human_agent_deepening_evidence_loop": public_doc_code_evidence_loop_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_human_agent_deepening_evidence_loop_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/evidence-loop")
async def read_human_agent_deepening_evidence_loop(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = DocCodeEvidenceLoopService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.read_evidence_loop(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_human_agent_deepening_evidence_loop_build")
    data = {"human_agent_deepening_evidence_loop": public_doc_code_evidence_loop_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.post("/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/regression/build")
async def build_human_agent_deepening_regression(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    service = MultiProjectRegressionService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.build_regression(codebase_id, projects=list((payload or {}).get("projects") or []))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_human_agent_deepening_regression_build")
    data = {"human_agent_deepening_regression": public_regression_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_human_agent_deepening_regression_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/regression")
async def read_human_agent_deepening_regression(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = MultiProjectRegressionService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.read_regression(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_human_agent_deepening_regression_build")
    data = {"human_agent_deepening_regression": public_regression_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.post("/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/restore/build")
async def build_human_agent_deepening_restore(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = RestoreUXService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.build_restore_ux(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_human_agent_deepening_restore_build")
    data = {"human_agent_deepening_restore": public_restore_ux_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=["knowledge_code_human_agent_deepening_restore_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


@router.get("/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/restore")
async def read_human_agent_deepening_restore(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = RestoreUXService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        result = service.read_restore_ux(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_human_agent_deepening_restore_build")
    data = {"human_agent_deepening_restore": public_restore_ux_payload(result)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        snapshot_id=None,
        data=data,
        artifact_refs=payload.get("artifact_refs", []),
        warnings=payload.get("warnings", []),
        unresolved=payload.get("unresolved", []),
        next_actions=payload.get("next_actions", []),
    )
    return body


def _error(status_code: int, workspace_id: str, codebase_id: str, error: str, *, next_action: str = "knowledge_code_human_agent_deepening_portal_build"):
    payload = {
        "v2": v2_error_envelope(
            workspace_id=workspace_id,
            codebase_id=codebase_id,
            snapshot_id=None,
            code=error,
            message=error,
            next_actions=[next_action],
        )
    }
    return JSONResponse(status_code=status_code, content=payload)
