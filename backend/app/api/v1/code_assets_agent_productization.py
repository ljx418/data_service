"""HTTP routes for V2.46 Agent Productization artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService, public_mcp_productization_payload
from data_service.code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService, public_profile_onboarding_payload
from data_service.code_assets.agent_productization.human_portal import AgentHumanPortalService, public_human_portal_payload
from data_service.code_assets.agent_productization.task_navigation import AgentTaskNavigationService, public_task_navigation_payload
from data_service.code_assets.agent_productization.governance import AgentProductizationGovernanceService, public_governance_payload
from data_service.code_assets.agent_productization.playbooks import AgentProductizationPlaybookService, public_playbook_payload
from data_service.code_assets.agent_productization.closure import AgentProductizationClosureService, public_closure_payload
from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Agent Productization"], dependencies=[Depends(verify_knowledge_access)])


class TaskNavigationRequest(BaseModel):
    task: str


class GovernanceFeedbackRequest(BaseModel):
    target_type: str
    target_id: str
    action: str
    rule_type: str = "read_time_overlay"
    severity: str = "medium"
    reason: str = ""
    suggested_value: str = ""


class GovernanceRuleReviewRequest(BaseModel):
    status: str
    reviewer: str = ""
    note: str = ""


class PlaybookBuildRequest(BaseModel):
    role: str | None = None
    max_tokens: int = 4000


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-productization/mcp/build")
async def build_agent_productization_mcp(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentMCPProductizationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        from data_service.mcp_tool_registry import all_tool_specs

        payload = service.build_mcp_usage(codebase_id, all_tool_specs())
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc))
    data = {"agent_productization_mcp": public_mcp_productization_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_mcp_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-productization/mcp")
async def read_agent_productization_mcp(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentMCPProductizationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_mcp_usage(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc))
    data = {"agent_productization_mcp": public_mcp_productization_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-productization/profile/build")
async def build_agent_productization_profile(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentProfileOnboardingService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_profile_onboarding(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_profile_build")
    data = {"agent_productization_profile": public_profile_onboarding_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_profile_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-productization/profile")
async def read_agent_productization_profile(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentProfileOnboardingService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_profile_onboarding(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_profile_build")
    data = {"agent_productization_profile": public_profile_onboarding_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-productization/portal/build")
async def build_agent_productization_portal(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentHumanPortalService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_portal(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_portal_build")
    data = {"agent_productization_portal": public_human_portal_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_portal_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-productization/portal")
async def read_agent_productization_portal(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentHumanPortalService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_portal(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_portal_build")
    data = {"agent_productization_portal": public_human_portal_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-productization/portal/view")
async def view_agent_productization_portal(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentHumanPortalService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_portal(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_portal_build")
    return HTMLResponse(content=str(payload.get("html") or ""), status_code=200)


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-productization/tasks")
async def build_agent_productization_task_navigation(workspace_id: str, codebase_id: str, request: TaskNavigationRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentTaskNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_task_navigation(codebase_id, task=request.task)
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_task_navigation_build")
    data = {"agent_productization_task_navigation": public_task_navigation_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_task_navigation_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-productization/tasks/{task_id}")
async def read_agent_productization_task_navigation(workspace_id: str, codebase_id: str, task_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentTaskNavigationService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_task_navigation(codebase_id, task_id=task_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_task_navigation_build")
    data = {"agent_productization_task_navigation": public_task_navigation_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-productization/governance/feedback")
async def record_agent_productization_governance_feedback(workspace_id: str, codebase_id: str, request: GovernanceFeedbackRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentProductizationGovernanceService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.record_feedback(
            codebase_id,
            target_type=request.target_type,
            target_id=request.target_id,
            action=request.action,
            rule_type=request.rule_type,
            severity=request.severity,
            reason=request.reason,
            suggested_value=request.suggested_value,
        )
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_governance_feedback")
    data = {"agent_productization_governance": public_governance_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_governance_rules_build"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-productization/governance/rules/build")
async def build_agent_productization_governance_rules(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentProductizationGovernanceService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_rules(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_governance_feedback")
    data = {"agent_productization_governance": public_governance_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_governance_overlay"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-productization/governance/rules/{rule_id}/review")
async def review_agent_productization_governance_rule(workspace_id: str, codebase_id: str, rule_id: str, request: GovernanceRuleReviewRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentProductizationGovernanceService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.review_rule(codebase_id, rule_id, status=request.status, reviewer=request.reviewer, note=request.note)
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_governance_rules_build")
    data = {"agent_productization_governance": public_governance_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-productization/governance/overlay")
async def read_agent_productization_governance_overlay(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentProductizationGovernanceService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        overlay = service.read_overlay(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_governance_feedback")
    payload = {"overlay": overlay, "artifact_refs": overlay.get("artifact_refs", [])}
    data = {"agent_productization_governance": public_governance_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-productization/playbooks")
async def build_agent_productization_playbooks(workspace_id: str, codebase_id: str, request: PlaybookBuildRequest):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentProductizationPlaybookService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_playbooks(codebase_id, role=request.role, max_tokens=request.max_tokens)
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_playbook_build")
    data = {"agent_productization_playbooks": public_playbook_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_playbook_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-productization/playbooks/{role}")
async def read_agent_productization_playbook(workspace_id: str, codebase_id: str, role: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentProductizationPlaybookService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_playbook(codebase_id, role=role)
    except (FileNotFoundError, ValueError) as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_playbook_build")
    data = {"agent_productization_playbooks": public_playbook_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-productization/closure/build")
async def build_agent_productization_closure(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentProductizationClosureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.build_closure(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_closure_build")
    data = {"agent_productization_closure": public_closure_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_closure_read"], data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-productization/closure")
async def read_agent_productization_closure(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    service = AgentProductizationClosureService(workspace, workspace_id=str(meta["workspace_id"]))
    try:
        payload = service.read_closure(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), next_action="knowledge_code_agent_productization_closure_build")
    data = {"agent_productization_closure": public_closure_payload(payload)}
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=payload.get("artifact_refs", []), data=_with_v2(str(meta["workspace_id"]), codebase_id, data, payload))


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


def _error(status_code: int, workspace_id: str, codebase_id: str, error: str, *, next_action: str = "knowledge_code_agent_productization_mcp_build"):
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
