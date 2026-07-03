"""MCP tools for V2.96-V2.100 automated evidence closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.automated_evidence_closure.cli_gap import DefaultCliGapClosure, public_cli_gap_payload
from .code_assets.automated_evidence_closure.external_path_registry import ExternalProjectPathRegistry, public_external_path_payload
from .code_assets.automated_evidence_closure.quality_workbench import QualityDecisionWorkbench, public_quality_workbench_payload
from .code_assets.automated_evidence_closure.release_evidence_gate import AutomatedReleaseEvidenceGate, public_release_gate_payload
from .code_assets.automated_evidence_closure.route_a_evidence import RouteAEvidenceAutomator, public_route_a_evidence_payload
from .code_assets.envelope import v2_error_envelope, v2_success_envelope


AUTOMATED_EVIDENCE_CLOSURE_TOOL_NAMES = {
    "knowledge_code_automated_evidence_closure_cli_gap_build",
    "knowledge_code_automated_evidence_closure_cli_gap_read",
    "knowledge_code_automated_evidence_closure_route_a_evidence_build",
    "knowledge_code_automated_evidence_closure_route_a_evidence_read",
    "knowledge_code_automated_evidence_closure_quality_workbench_build",
    "knowledge_code_automated_evidence_closure_quality_workbench_read",
    "knowledge_code_automated_evidence_closure_external_path_build",
    "knowledge_code_automated_evidence_closure_external_path_read",
    "knowledge_code_automated_evidence_closure_release_gate_build",
    "knowledge_code_automated_evidence_closure_release_gate_read",
}


def _schema(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    props = {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}
    props.update(extra or {})
    return {"type": "object", "properties": props, "required": ["workspace_id", "codebase_id"]}


AUTOMATED_EVIDENCE_CLOSURE_TOOL_SPECS = [
    {"name": "knowledge_code_automated_evidence_closure_cli_gap_build", "description": "Build V2.96 default CLI gap closure artifacts", "inputSchema": _schema({"cli_state": {"type": "object"}})},
    {"name": "knowledge_code_automated_evidence_closure_cli_gap_read", "description": "Read V2.96 default CLI gap closure artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_automated_evidence_closure_route_a_evidence_build", "description": "Build V2.97 Route A automated evidence artifacts", "inputSchema": _schema({"material_state": {"type": "object"}})},
    {"name": "knowledge_code_automated_evidence_closure_route_a_evidence_read", "description": "Read V2.97 Route A automated evidence artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_automated_evidence_closure_quality_workbench_build", "description": "Build V2.98 quality decision workbench artifacts", "inputSchema": _schema({"decision_state": {"type": "object"}})},
    {"name": "knowledge_code_automated_evidence_closure_quality_workbench_read", "description": "Read V2.98 quality decision workbench artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_automated_evidence_closure_external_path_build", "description": "Build V2.99 external project path governance artifacts", "inputSchema": _schema({"project_state": {"type": "object"}})},
    {"name": "knowledge_code_automated_evidence_closure_external_path_read", "description": "Read V2.99 external project path governance artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_automated_evidence_closure_release_gate_build", "description": "Build V2.100 automated release evidence gate artifacts", "inputSchema": _schema({"gate_state": {"type": "object"}})},
    {"name": "knowledge_code_automated_evidence_closure_release_gate_read", "description": "Read V2.100 automated release evidence gate artifacts", "inputSchema": _schema()},
]


def handle_automated_evidence_closure_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in AUTOMATED_EVIDENCE_CLOSURE_TOOL_NAMES:
        raise ValueError(f"Unknown automated evidence closure tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    try:
        payload, key, next_action = _dispatch(name, arguments, workspace_path, workspace_id, codebase_id)
        return _ok(envelope, workspace_id, codebase_id, payload, key, next_action)
    except FileNotFoundError as exc:
        message = str(exc)
        next_action = _next_action_for(message)
        return envelope(
            workspace_id=workspace_id,
            status="blocked",
            warnings=[message],
            next_actions=[next_action],
            data={"error": {"code": message, "message": message, "retryable": False}, "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=message, message=message, next_actions=[next_action])},
        )


def _dispatch(name: str, arguments: dict[str, Any], workspace_path: Path, workspace_id: str, codebase_id: str):
    if name == "knowledge_code_automated_evidence_closure_cli_gap_build":
        payload = DefaultCliGapClosure(workspace_path, workspace_id=workspace_id).build_cli_gap(codebase_id, cli_state=dict(arguments.get("cli_state") or {}))
        return payload, "automated_evidence_cli_gap", "knowledge_code_automated_evidence_closure_cli_gap_read"
    if name == "knowledge_code_automated_evidence_closure_cli_gap_read":
        return DefaultCliGapClosure(workspace_path, workspace_id=workspace_id).read_cli_gap(codebase_id), "automated_evidence_cli_gap", None
    if name == "knowledge_code_automated_evidence_closure_route_a_evidence_build":
        payload = RouteAEvidenceAutomator(workspace_path, workspace_id=workspace_id).build_route_a_evidence(codebase_id, material_state=dict(arguments.get("material_state") or {}))
        return payload, "automated_evidence_route_a", "knowledge_code_automated_evidence_closure_route_a_evidence_read"
    if name == "knowledge_code_automated_evidence_closure_route_a_evidence_read":
        return RouteAEvidenceAutomator(workspace_path, workspace_id=workspace_id).read_route_a_evidence(codebase_id), "automated_evidence_route_a", None
    if name == "knowledge_code_automated_evidence_closure_quality_workbench_build":
        payload = QualityDecisionWorkbench(workspace_path, workspace_id=workspace_id).build_quality_workbench(codebase_id, decision_state=dict(arguments.get("decision_state") or {}))
        return payload, "automated_evidence_quality_workbench", "knowledge_code_automated_evidence_closure_quality_workbench_read"
    if name == "knowledge_code_automated_evidence_closure_quality_workbench_read":
        return QualityDecisionWorkbench(workspace_path, workspace_id=workspace_id).read_quality_workbench(codebase_id), "automated_evidence_quality_workbench", None
    if name == "knowledge_code_automated_evidence_closure_external_path_build":
        payload = ExternalProjectPathRegistry(workspace_path, workspace_id=workspace_id).build_external_path(codebase_id, project_state=dict(arguments.get("project_state") or {}))
        return payload, "automated_evidence_external_path", "knowledge_code_automated_evidence_closure_external_path_read"
    if name == "knowledge_code_automated_evidence_closure_external_path_read":
        return ExternalProjectPathRegistry(workspace_path, workspace_id=workspace_id).read_external_path(codebase_id), "automated_evidence_external_path", None
    if name == "knowledge_code_automated_evidence_closure_release_gate_build":
        payload = AutomatedReleaseEvidenceGate(workspace_path, workspace_id=workspace_id).build_release_gate(codebase_id, gate_state=dict(arguments.get("gate_state") or {}))
        return payload, "automated_evidence_release_gate", "knowledge_code_automated_evidence_closure_release_gate_read"
    return AutomatedReleaseEvidenceGate(workspace_path, workspace_id=workspace_id).read_release_gate(codebase_id), "automated_evidence_release_gate", None


def _ok(envelope, workspace_id: str, codebase_id: str, payload: dict[str, Any], key: str, next_action: str | None = None) -> dict[str, Any]:
    data = {key: _public_for(key, payload)}
    next_actions = [next_action] if next_action else None
    return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=next_actions, data=_with_v2(workspace_id, codebase_id, data, payload))


def _public_for(key: str, payload: dict[str, Any]) -> dict[str, Any]:
    if key == "automated_evidence_cli_gap":
        return public_cli_gap_payload(payload)
    if key == "automated_evidence_route_a":
        return public_route_a_evidence_payload(payload)
    if key == "automated_evidence_quality_workbench":
        return public_quality_workbench_payload(payload)
    if key == "automated_evidence_external_path":
        return public_external_path_payload(payload)
    return public_release_gate_payload(payload)


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


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body

