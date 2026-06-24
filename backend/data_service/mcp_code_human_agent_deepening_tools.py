"""MCP tools for V2.54-V2.58 Human / Agent Deepening."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.envelope import v2_error_envelope, v2_success_envelope
from .code_assets.human_agent_deepening.evidence_loop import DocCodeEvidenceLoopService, public_doc_code_evidence_loop_payload
from .code_assets.human_agent_deepening.human_portal import HumanPortalDeepeningService, public_human_portal_deepening_payload
from .code_assets.human_agent_deepening.regression import MultiProjectRegressionService, public_regression_payload
from .code_assets.human_agent_deepening.restore_ux import RestoreUXService, public_restore_ux_payload
from .code_assets.human_agent_deepening.task_workflow import AgentTaskWorkflowService, public_agent_task_workflow_payload


HUMAN_AGENT_DEEPENING_TOOL_NAMES = {
    "knowledge_code_human_agent_deepening_portal_build",
    "knowledge_code_human_agent_deepening_portal_read",
    "knowledge_code_human_agent_deepening_task_workflow_build",
    "knowledge_code_human_agent_deepening_task_workflow_read",
    "knowledge_code_human_agent_deepening_evidence_loop_build",
    "knowledge_code_human_agent_deepening_evidence_loop_read",
    "knowledge_code_human_agent_deepening_regression_build",
    "knowledge_code_human_agent_deepening_regression_read",
    "knowledge_code_human_agent_deepening_restore_build",
    "knowledge_code_human_agent_deepening_restore_read",
}


HUMAN_AGENT_DEEPENING_TOOL_SPECS = [
    {
        "name": "knowledge_code_human_agent_deepening_portal_build",
        "description": "Build V2.54 Human Portal Deepening artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_human_agent_deepening_portal_read",
        "description": "Read V2.54 Human Portal Deepening artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_human_agent_deepening_task_workflow_build",
        "description": "Build V2.55 Agent Task Workflow artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "task": {"type": "string"}, "max_tokens": {"type": "integer"}}, "required": ["workspace_id", "codebase_id", "task"]},
    },
    {
        "name": "knowledge_code_human_agent_deepening_task_workflow_read",
        "description": "Read V2.55 Agent Task Workflow artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "task_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id", "task_id"]},
    },
    {
        "name": "knowledge_code_human_agent_deepening_evidence_loop_build",
        "description": "Build V2.56 Doc-Code Governance Evidence Loop artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_human_agent_deepening_evidence_loop_read",
        "description": "Read V2.56 Doc-Code Governance Evidence Loop artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_human_agent_deepening_regression_build",
        "description": "Build V2.57 Multi-project Regression Expansion artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}, "projects": {"type": "array"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_human_agent_deepening_regression_read",
        "description": "Read V2.57 Multi-project Regression Expansion artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_human_agent_deepening_restore_build",
        "description": "Build V2.58 Developer Onboarding Restore UX artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
    {
        "name": "knowledge_code_human_agent_deepening_restore_read",
        "description": "Read V2.58 Developer Onboarding Restore UX artifacts",
        "inputSchema": {"type": "object", "properties": {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}, "required": ["workspace_id", "codebase_id"]},
    },
]


def handle_human_agent_deepening_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in HUMAN_AGENT_DEEPENING_TOOL_NAMES:
        raise ValueError(f"Unknown human agent deepening tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    try:
        if name == "knowledge_code_human_agent_deepening_portal_build":
            service = HumanPortalDeepeningService(workspace_path, workspace_id=workspace_id)
            payload = service.build_portal(codebase_id)
            data = {"human_agent_deepening_portal": public_human_portal_deepening_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_human_agent_deepening_portal_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_human_agent_deepening_portal_read":
            service = HumanPortalDeepeningService(workspace_path, workspace_id=workspace_id)
            payload = service.read_portal(codebase_id)
            data = {"human_agent_deepening_portal": public_human_portal_deepening_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_human_agent_deepening_task_workflow_build":
            service = AgentTaskWorkflowService(workspace_path, workspace_id=workspace_id)
            payload = service.build_task_workflow(codebase_id, task=str(arguments.get("task") or ""), max_tokens=int(arguments.get("max_tokens") or 4000))
            data = {"human_agent_deepening_task_workflow": public_agent_task_workflow_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_human_agent_deepening_task_workflow_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_human_agent_deepening_task_workflow_read":
            service = AgentTaskWorkflowService(workspace_path, workspace_id=workspace_id)
            payload = service.read_task_workflow(codebase_id, task_id=str(arguments.get("task_id") or ""))
            data = {"human_agent_deepening_task_workflow": public_agent_task_workflow_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_human_agent_deepening_evidence_loop_build":
            service = DocCodeEvidenceLoopService(workspace_path, workspace_id=workspace_id)
            payload = service.build_evidence_loop(codebase_id)
            data = {"human_agent_deepening_evidence_loop": public_doc_code_evidence_loop_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_human_agent_deepening_evidence_loop_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_human_agent_deepening_evidence_loop_read":
            service = DocCodeEvidenceLoopService(workspace_path, workspace_id=workspace_id)
            payload = service.read_evidence_loop(codebase_id)
            data = {"human_agent_deepening_evidence_loop": public_doc_code_evidence_loop_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_human_agent_deepening_regression_build":
            service = MultiProjectRegressionService(workspace_path, workspace_id=workspace_id)
            payload = service.build_regression(codebase_id, projects=list(arguments.get("projects") or []))
            data = {"human_agent_deepening_regression": public_regression_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_human_agent_deepening_regression_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_human_agent_deepening_regression_read":
            service = MultiProjectRegressionService(workspace_path, workspace_id=workspace_id)
            payload = service.read_regression(codebase_id)
            data = {"human_agent_deepening_regression": public_regression_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_human_agent_deepening_restore_build":
            service = RestoreUXService(workspace_path, workspace_id=workspace_id)
            payload = service.build_restore_ux(codebase_id)
            data = {"human_agent_deepening_restore": public_restore_ux_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_human_agent_deepening_restore_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        service = RestoreUXService(workspace_path, workspace_id=workspace_id)
        payload = service.read_restore_ux(codebase_id)
        data = {"human_agent_deepening_restore": public_restore_ux_payload(payload)}
        return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
    except FileNotFoundError as exc:
        message = str(exc)
        if "TASK_WORKFLOW" in message:
            next_actions = ["knowledge_code_human_agent_deepening_task_workflow_build"]
        elif "EVIDENCE_LOOP" in message:
            next_actions = ["knowledge_code_human_agent_deepening_evidence_loop_build"]
        elif "REGRESSION_EXPANSION" in message:
            next_actions = ["knowledge_code_human_agent_deepening_regression_build"]
        elif "RESTORE_UX" in message:
            next_actions = ["knowledge_code_human_agent_deepening_restore_build"]
        else:
            next_actions = ["knowledge_code_human_agent_deepening_portal_build"]
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
