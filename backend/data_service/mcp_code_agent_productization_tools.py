"""MCP tools for V2.46 Agent Productization."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.agent_productization.mcp_usage import AgentMCPProductizationService, public_mcp_productization_payload
from .code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService, public_profile_onboarding_payload
from .code_assets.agent_productization.human_portal import AgentHumanPortalService, public_human_portal_payload
from .code_assets.agent_productization.task_navigation import AgentTaskNavigationService, public_task_navigation_payload
from .code_assets.agent_productization.governance import AgentProductizationGovernanceService, public_governance_payload
from .code_assets.agent_productization.playbooks import AgentProductizationPlaybookService, public_playbook_payload
from .code_assets.agent_productization.closure import AgentProductizationClosureService, public_closure_payload
from .code_assets.envelope import v2_error_envelope, v2_success_envelope


AGENT_PRODUCTIZATION_TOOL_NAMES = {
    "knowledge_code_agent_productization_mcp_build",
    "knowledge_code_agent_productization_mcp_read",
    "knowledge_code_agent_productization_profile_build",
    "knowledge_code_agent_productization_profile_read",
    "knowledge_code_agent_productization_portal_build",
    "knowledge_code_agent_productization_portal_read",
    "knowledge_code_agent_productization_task_navigation_build",
    "knowledge_code_agent_productization_task_navigation_read",
    "knowledge_code_agent_productization_governance_feedback",
    "knowledge_code_agent_productization_governance_rules_build",
    "knowledge_code_agent_productization_governance_rule_review",
    "knowledge_code_agent_productization_governance_overlay",
    "knowledge_code_agent_productization_playbook_build",
    "knowledge_code_agent_productization_playbook_read",
    "knowledge_code_agent_productization_closure_build",
    "knowledge_code_agent_productization_closure_read",
}


AGENT_PRODUCTIZATION_TOOL_SPECS = [
    {
        "name": "knowledge_code_agent_productization_mcp_build",
        "description": "Build V2.46 Codex/Agent MCP usage guide, readable tool catalog, and workflows",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_agent_productization_mcp_read",
        "description": "Read V2.46 Codex/Agent MCP usage guide, readable tool catalog, and workflows",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_agent_productization_profile_build",
        "description": "Build V2.47 project profile onboarding draft, taxonomy suggestions, authority rules, and no-hardcode audit",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_agent_productization_profile_read",
        "description": "Read V2.47 project profile onboarding draft, taxonomy suggestions, authority rules, and no-hardcode audit",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_agent_productization_portal_build",
        "description": "Build V2.48 human-readable architecture portal model, SVG chart, and HTML report",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_agent_productization_portal_read",
        "description": "Read V2.48 human-readable architecture portal model, SVG chart, and HTML report",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_agent_productization_task_navigation_build",
        "description": "Build V2.49 task reading order, impact candidates, and suggested tests",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "task": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "task"]},
    },
    {
        "name": "knowledge_code_agent_productization_task_navigation_read",
        "description": "Read V2.49 task reading order, impact candidates, and suggested tests",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "task_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "task_id"]},
    },
    {
        "name": "knowledge_code_agent_productization_governance_feedback",
        "description": "Record V2.50 Agent Productization governance feedback for a portal/profile/task/MCP target",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "target_type": {"type": "string"}, "target_id": {"type": "string"}, "action": {"type": "string"}, "rule_type": {"type": "string"}, "severity": {"type": "string"}, "reason": {"type": "string"}, "suggested_value": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "target_type", "target_id", "action"]},
    },
    {
        "name": "knowledge_code_agent_productization_governance_rules_build",
        "description": "Build V2.50 Agent Productization governance rules from recorded feedback",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_agent_productization_governance_rule_review",
        "description": "Approve, reject, or revoke a V2.50 Agent Productization governance rule",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "rule_id": {"type": "string"}, "status": {"type": "string"}, "reviewer": {"type": "string"}, "note": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "rule_id", "status"]},
    },
    {
        "name": "knowledge_code_agent_productization_governance_overlay",
        "description": "Read V2.50 Agent Productization governance read-time overlay report",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_agent_productization_playbook_build",
        "description": "Build V2.51 role-scoped Agent Context Playbooks for maintainers, coding agents, documentation agents, and architecture reviewers",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "role": {"type": "string"}, "max_tokens": {"type": "integer"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_agent_productization_playbook_read",
        "description": "Read a V2.51 role-scoped Agent Context Playbook",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "role": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "role"]},
    },
    {
        "name": "knowledge_code_agent_productization_closure_build",
        "description": "Build V2.52 Agent Productization continuous acceptance closure artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_agent_productization_closure_read",
        "description": "Read V2.52 Agent Productization continuous acceptance closure artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
]


def handle_agent_productization_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
    tool_specs_provider: Callable[[], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    if name not in AGENT_PRODUCTIZATION_TOOL_NAMES:
        raise ValueError(f"Unknown agent productization tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    try:
        if name == "knowledge_code_agent_productization_mcp_build":
            service = AgentMCPProductizationService(workspace_path, workspace_id=workspace_id)
            if tool_specs_provider is None:
                from .mcp_tool_registry import all_tool_specs

                tool_specs_provider = all_tool_specs
            payload = service.build_mcp_usage(codebase_id, tool_specs_provider())
            data = {"agent_productization_mcp": public_mcp_productization_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_mcp_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_agent_productization_mcp_read":
            service = AgentMCPProductizationService(workspace_path, workspace_id=workspace_id)
            payload = service.read_mcp_usage(codebase_id)
            data = {"agent_productization_mcp": public_mcp_productization_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_agent_productization_profile_build":
            profile_service = AgentProfileOnboardingService(workspace_path, workspace_id=workspace_id)
            payload = profile_service.build_profile_onboarding(codebase_id)
            data = {"agent_productization_profile": public_profile_onboarding_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_profile_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_agent_productization_profile_read":
            profile_service = AgentProfileOnboardingService(workspace_path, workspace_id=workspace_id)
            payload = profile_service.read_profile_onboarding(codebase_id)
            data = {"agent_productization_profile": public_profile_onboarding_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        portal_service = AgentHumanPortalService(workspace_path, workspace_id=workspace_id)
        if name == "knowledge_code_agent_productization_portal_build":
            payload = portal_service.build_portal(codebase_id)
            data = {"agent_productization_portal": public_human_portal_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_portal_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_agent_productization_portal_read":
            payload = portal_service.read_portal(codebase_id)
            data = {"agent_productization_portal": public_human_portal_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        task_service = AgentTaskNavigationService(workspace_path, workspace_id=workspace_id)
        if name == "knowledge_code_agent_productization_task_navigation_build":
            payload = task_service.build_task_navigation(codebase_id, task=str(arguments.get("task") or ""))
            data = {"agent_productization_task_navigation": public_task_navigation_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_task_navigation_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_agent_productization_task_navigation_read":
            payload = task_service.read_task_navigation(codebase_id, task_id=str(arguments.get("task_id") or ""))
            data = {"agent_productization_task_navigation": public_task_navigation_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        governance_service = AgentProductizationGovernanceService(workspace_path, workspace_id=workspace_id)
        if name == "knowledge_code_agent_productization_governance_feedback":
            payload = governance_service.record_feedback(
                codebase_id,
                target_type=str(arguments.get("target_type") or ""),
                target_id=str(arguments.get("target_id") or ""),
                action=str(arguments.get("action") or ""),
                rule_type=str(arguments.get("rule_type") or "read_time_overlay"),
                severity=str(arguments.get("severity") or "medium"),
                reason=str(arguments.get("reason") or ""),
                suggested_value=str(arguments.get("suggested_value") or ""),
            )
            data = {"agent_productization_governance": public_governance_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_governance_rules_build"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_agent_productization_governance_rules_build":
            payload = governance_service.build_rules(codebase_id)
            data = {"agent_productization_governance": public_governance_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_governance_overlay"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_agent_productization_governance_rule_review":
            payload = governance_service.review_rule(
                codebase_id,
                str(arguments.get("rule_id") or ""),
                status=str(arguments.get("status") or ""),
                reviewer=str(arguments.get("reviewer") or ""),
                note=str(arguments.get("note") or ""),
            )
            data = {"agent_productization_governance": public_governance_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_agent_productization_governance_overlay":
            overlay = governance_service.read_overlay(codebase_id)
            payload = {"overlay": overlay, "artifact_refs": overlay.get("artifact_refs", [])}
            data = {"agent_productization_governance": public_governance_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_agent_productization_playbook_build":
            playbook_service = AgentProductizationPlaybookService(workspace_path, workspace_id=workspace_id)
            role_value = str(arguments.get("role") or "").strip() or None
            payload = playbook_service.build_playbooks(codebase_id, role=role_value, max_tokens=int(arguments.get("max_tokens") or 4000))
            data = {"agent_productization_playbooks": public_playbook_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_playbook_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_agent_productization_playbook_read":
            playbook_service = AgentProductizationPlaybookService(workspace_path, workspace_id=workspace_id)
            payload = playbook_service.read_playbook(codebase_id, role=str(arguments.get("role") or ""))
            data = {"agent_productization_playbooks": public_playbook_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        closure_service = AgentProductizationClosureService(workspace_path, workspace_id=workspace_id)
        if name == "knowledge_code_agent_productization_closure_build":
            payload = closure_service.build_closure(codebase_id)
            data = {"agent_productization_closure": public_closure_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_agent_productization_closure_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        payload = closure_service.read_closure(codebase_id)
        data = {"agent_productization_closure": public_closure_payload(payload)}
        return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
    except FileNotFoundError as exc:
        message = str(exc)
        if "HUMAN_PORTAL" in message:
            next_actions = ["knowledge_code_agent_productization_portal_build"]
        elif "TASK_NAVIGATION" in message:
            next_actions = ["knowledge_code_agent_productization_task_navigation_build"]
        elif "GOVERNANCE" in message:
            next_actions = ["knowledge_code_agent_productization_governance_feedback"]
        elif "PLAYBOOK" in message:
            next_actions = ["knowledge_code_agent_productization_playbook_build"]
        elif "CLOSURE" in message:
            next_actions = ["knowledge_code_agent_productization_closure_build"]
        elif "PROFILE" in message:
            next_actions = ["knowledge_code_agent_productization_profile_build"]
        else:
            next_actions = ["knowledge_code_agent_productization_mcp_build"]
        return envelope(
            workspace_id=workspace_id,
            status="blocked",
            warnings=[message],
            next_actions=next_actions,
            data={
                "error": {"code": message, "message": message, "retryable": False},
                "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=message, message=message, next_actions=next_actions),
            },
        )
    except ValueError as exc:
        message = str(exc)
        next_actions = ["knowledge_code_agent_productization_playbook_build"] if "PLAYBOOK" in message else ["knowledge_code_agent_productization_task_navigation_build"]
        return envelope(
            workspace_id=workspace_id,
            status="blocked",
            warnings=[message],
            next_actions=next_actions,
            data={
                "error": {"code": message, "message": message, "retryable": False},
                "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=message, message=message, next_actions=next_actions),
            },
        )


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
