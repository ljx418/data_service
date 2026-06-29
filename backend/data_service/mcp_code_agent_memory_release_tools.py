"""MCP tools for V2.71-V2.75 agent memory release stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.agent_memory_release.agent_memory import AgentMemoryService, public_agent_memory_payload
from .code_assets.agent_memory_release.ci_warning_governance import CIWarningGovernanceService, public_ci_warning_governance_payload
from .code_assets.agent_memory_release.external_project_closure import ExternalProjectClosureService, public_external_project_closure_payload
from .code_assets.agent_memory_release.interactive_console import InteractiveMaintainerConsoleService, public_interactive_console_payload
from .code_assets.agent_memory_release.release_restore import ReleaseRestoreService, public_release_restore_payload
from .code_assets.envelope import v2_error_envelope, v2_success_envelope


AGENT_MEMORY_RELEASE_TOOL_NAMES = {
    "knowledge_code_agent_memory_release_external_closure_build",
    "knowledge_code_agent_memory_release_external_closure_read",
    "knowledge_code_agent_memory_release_ci_governance_build",
    "knowledge_code_agent_memory_release_ci_governance_read",
    "knowledge_code_agent_memory_release_memory_build",
    "knowledge_code_agent_memory_release_memory_read",
    "knowledge_code_agent_memory_release_console_build",
    "knowledge_code_agent_memory_release_console_read",
    "knowledge_code_agent_memory_release_release_restore_build",
    "knowledge_code_agent_memory_release_release_restore_read",
}


def _schema(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    props = {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}
    props.update(extra or {})
    return {"type": "object", "properties": props, "required": ["workspace_id", "codebase_id"]}


AGENT_MEMORY_RELEASE_TOOL_SPECS = [
    {"name": "knowledge_code_agent_memory_release_external_closure_build", "description": "Build V2.71 external project binding closure artifacts", "inputSchema": _schema({"projects": {"type": "array"}})},
    {"name": "knowledge_code_agent_memory_release_external_closure_read", "description": "Read V2.71 external project binding closure artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_agent_memory_release_ci_governance_build", "description": "Build V2.72 CI and warning governance artifacts", "inputSchema": _schema({"command_results": {"type": "object"}})},
    {"name": "knowledge_code_agent_memory_release_ci_governance_read", "description": "Read V2.72 CI and warning governance artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_agent_memory_release_memory_build", "description": "Build V2.73 Agent project memory artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_agent_memory_release_memory_read", "description": "Read V2.73 Agent project memory artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_agent_memory_release_console_build", "description": "Build V2.74 interactive maintainer console artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_agent_memory_release_console_read", "description": "Read V2.74 interactive maintainer console artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_agent_memory_release_release_restore_build", "description": "Build V2.75 release and restore packaging artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_agent_memory_release_release_restore_read", "description": "Read V2.75 release and restore packaging artifacts", "inputSchema": _schema()},
]


def handle_agent_memory_release_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in AGENT_MEMORY_RELEASE_TOOL_NAMES:
        raise ValueError(f"Unknown agent memory release tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    try:
        if name == "knowledge_code_agent_memory_release_external_closure_build":
            payload = ExternalProjectClosureService(workspace_path, workspace_id=workspace_id).build_external_project_closure(codebase_id, projects=list(arguments.get("projects") or []))
            return _ok(envelope, workspace_id, codebase_id, payload, "agent_memory_release_external_closure", public_external_project_closure_payload, "knowledge_code_agent_memory_release_external_closure_read")
        if name == "knowledge_code_agent_memory_release_external_closure_read":
            payload = ExternalProjectClosureService(workspace_path, workspace_id=workspace_id).read_external_project_closure(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "agent_memory_release_external_closure", public_external_project_closure_payload)
        if name == "knowledge_code_agent_memory_release_ci_governance_build":
            payload = CIWarningGovernanceService(workspace_path, workspace_id=workspace_id).build_ci_warning_governance(codebase_id, command_results=dict(arguments.get("command_results") or {}))
            return _ok(envelope, workspace_id, codebase_id, payload, "agent_memory_release_ci_governance", public_ci_warning_governance_payload, "knowledge_code_agent_memory_release_ci_governance_read")
        if name == "knowledge_code_agent_memory_release_ci_governance_read":
            payload = CIWarningGovernanceService(workspace_path, workspace_id=workspace_id).read_ci_warning_governance(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "agent_memory_release_ci_governance", public_ci_warning_governance_payload)
        if name == "knowledge_code_agent_memory_release_memory_build":
            payload = AgentMemoryService(workspace_path, workspace_id=workspace_id).build_agent_memory(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "agent_memory_release_memory", public_agent_memory_payload, "knowledge_code_agent_memory_release_memory_read")
        if name == "knowledge_code_agent_memory_release_memory_read":
            payload = AgentMemoryService(workspace_path, workspace_id=workspace_id).read_agent_memory(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "agent_memory_release_memory", public_agent_memory_payload)
        if name == "knowledge_code_agent_memory_release_console_build":
            payload = InteractiveMaintainerConsoleService(workspace_path, workspace_id=workspace_id).build_interactive_console(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "agent_memory_release_console", public_interactive_console_payload, "knowledge_code_agent_memory_release_console_read")
        if name == "knowledge_code_agent_memory_release_console_read":
            payload = InteractiveMaintainerConsoleService(workspace_path, workspace_id=workspace_id).read_interactive_console(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "agent_memory_release_console", public_interactive_console_payload)
        if name == "knowledge_code_agent_memory_release_release_restore_build":
            payload = ReleaseRestoreService(workspace_path, workspace_id=workspace_id).build_release_restore(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "agent_memory_release_release_restore", public_release_restore_payload, "knowledge_code_agent_memory_release_release_restore_read")
        payload = ReleaseRestoreService(workspace_path, workspace_id=workspace_id).read_release_restore(codebase_id)
        return _ok(envelope, workspace_id, codebase_id, payload, "agent_memory_release_release_restore", public_release_restore_payload)
    except FileNotFoundError as exc:
        message = str(exc)
        next_action = _next_action_for(message)
        return envelope(workspace_id=workspace_id, status="blocked", warnings=[message], next_actions=[next_action], data={"error": {"code": message, "message": message, "retryable": False}, "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=message, message=message, next_actions=[next_action])})


def _ok(envelope, workspace_id: str, codebase_id: str, payload: dict[str, Any], key: str, public_payload, next_action: str | None = None) -> dict[str, Any]:
    data = {key: public_payload(payload)}
    next_actions = [next_action] if next_action else None
    return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=next_actions, data=_with_v2(workspace_id, codebase_id, data, payload))


def _next_action_for(message: str) -> str:
    if "CI_WARNING" in message:
        return "knowledge_code_agent_memory_release_ci_governance_build"
    if "AGENT_MEMORY" in message:
        return "knowledge_code_agent_memory_release_memory_build"
    if "INTERACTIVE_CONSOLE" in message:
        return "knowledge_code_agent_memory_release_console_build"
    if "RELEASE_RESTORE" in message:
        return "knowledge_code_agent_memory_release_release_restore_build"
    return "knowledge_code_agent_memory_release_external_closure_build"


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body

