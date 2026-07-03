"""MCP tools for V2.91-V2.95 real acceptance closure."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.envelope import v2_error_envelope, v2_success_envelope
from .code_assets.real_acceptance_closure.external_project_validator import ExternalProjectPathE2EValidator, public_external_project_closure_payload
from .code_assets.real_acceptance_closure.quality_decision import HumanQualityDecisionRecorder, public_quality_decision_payload
from .code_assets.real_acceptance_closure.release_finalizer import FinalReleaseGateFinalizer, public_release_finalizer_payload
from .code_assets.real_acceptance_closure.route_a_material import RouteAMaterialIntakeReview, public_route_a_closure_payload
from .code_assets.real_acceptance_closure.runtime_restore import AcceptanceRuntimeRestorer, public_runtime_restore_payload


REAL_ACCEPTANCE_CLOSURE_TOOL_NAMES = {
    "knowledge_code_real_acceptance_closure_runtime_restore_build",
    "knowledge_code_real_acceptance_closure_runtime_restore_read",
    "knowledge_code_real_acceptance_closure_route_a_closure_build",
    "knowledge_code_real_acceptance_closure_route_a_closure_read",
    "knowledge_code_real_acceptance_closure_quality_decision_build",
    "knowledge_code_real_acceptance_closure_quality_decision_read",
    "knowledge_code_real_acceptance_closure_external_project_closure_build",
    "knowledge_code_real_acceptance_closure_external_project_closure_read",
    "knowledge_code_real_acceptance_closure_release_finalizer_build",
    "knowledge_code_real_acceptance_closure_release_finalizer_read",
}


def _schema(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    props = {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}
    props.update(extra or {})
    return {"type": "object", "properties": props, "required": ["workspace_id", "codebase_id"]}


REAL_ACCEPTANCE_CLOSURE_TOOL_SPECS = [
    {"name": "knowledge_code_real_acceptance_closure_runtime_restore_build", "description": "Build V2.91 restoreable acceptance runtime artifacts", "inputSchema": _schema({"runtime_state": {"type": "object"}})},
    {"name": "knowledge_code_real_acceptance_closure_runtime_restore_read", "description": "Read V2.91 restoreable acceptance runtime artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_acceptance_closure_route_a_closure_build", "description": "Build V2.92 Route A material closure artifacts", "inputSchema": _schema({"material_state": {"type": "object"}})},
    {"name": "knowledge_code_real_acceptance_closure_route_a_closure_read", "description": "Read V2.92 Route A material closure artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_acceptance_closure_quality_decision_build", "description": "Build V2.93 human quality decision artifacts", "inputSchema": _schema({"decision_state": {"type": "object"}})},
    {"name": "knowledge_code_real_acceptance_closure_quality_decision_read", "description": "Read V2.93 human quality decision artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_acceptance_closure_external_project_closure_build", "description": "Build V2.94 external project path E2E closure artifacts", "inputSchema": _schema({"project_state": {"type": "object"}})},
    {"name": "knowledge_code_real_acceptance_closure_external_project_closure_read", "description": "Read V2.94 external project path E2E closure artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_acceptance_closure_release_finalizer_build", "description": "Build V2.95 final release gate closure artifacts", "inputSchema": _schema({"gate_state": {"type": "object"}})},
    {"name": "knowledge_code_real_acceptance_closure_release_finalizer_read", "description": "Read V2.95 final release gate closure artifacts", "inputSchema": _schema()},
]


def handle_real_acceptance_closure_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in REAL_ACCEPTANCE_CLOSURE_TOOL_NAMES:
        raise ValueError(f"Unknown real acceptance closure tool: {name}")
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
    if name == "knowledge_code_real_acceptance_closure_runtime_restore_build":
        payload = AcceptanceRuntimeRestorer(workspace_path, workspace_id=workspace_id).build_runtime_restore(codebase_id, runtime_state=dict(arguments.get("runtime_state") or {}))
        return payload, "real_acceptance_runtime_restore", "knowledge_code_real_acceptance_closure_runtime_restore_read"
    if name == "knowledge_code_real_acceptance_closure_runtime_restore_read":
        return AcceptanceRuntimeRestorer(workspace_path, workspace_id=workspace_id).read_runtime_restore(codebase_id), "real_acceptance_runtime_restore", None
    if name == "knowledge_code_real_acceptance_closure_route_a_closure_build":
        payload = RouteAMaterialIntakeReview(workspace_path, workspace_id=workspace_id).build_route_a_closure(codebase_id, material_state=dict(arguments.get("material_state") or {}))
        return payload, "real_acceptance_route_a_closure", "knowledge_code_real_acceptance_closure_route_a_closure_read"
    if name == "knowledge_code_real_acceptance_closure_route_a_closure_read":
        return RouteAMaterialIntakeReview(workspace_path, workspace_id=workspace_id).read_route_a_closure(codebase_id), "real_acceptance_route_a_closure", None
    if name == "knowledge_code_real_acceptance_closure_quality_decision_build":
        payload = HumanQualityDecisionRecorder(workspace_path, workspace_id=workspace_id).build_quality_decision(codebase_id, decision_state=dict(arguments.get("decision_state") or {}))
        return payload, "real_acceptance_quality_decision", "knowledge_code_real_acceptance_closure_quality_decision_read"
    if name == "knowledge_code_real_acceptance_closure_quality_decision_read":
        return HumanQualityDecisionRecorder(workspace_path, workspace_id=workspace_id).read_quality_decision(codebase_id), "real_acceptance_quality_decision", None
    if name == "knowledge_code_real_acceptance_closure_external_project_closure_build":
        payload = ExternalProjectPathE2EValidator(workspace_path, workspace_id=workspace_id).build_external_project_closure(codebase_id, project_state=dict(arguments.get("project_state") or {}))
        return payload, "real_acceptance_external_project_closure", "knowledge_code_real_acceptance_closure_external_project_closure_read"
    if name == "knowledge_code_real_acceptance_closure_external_project_closure_read":
        return ExternalProjectPathE2EValidator(workspace_path, workspace_id=workspace_id).read_external_project_closure(codebase_id), "real_acceptance_external_project_closure", None
    if name == "knowledge_code_real_acceptance_closure_release_finalizer_build":
        payload = FinalReleaseGateFinalizer(workspace_path, workspace_id=workspace_id).build_release_finalizer(codebase_id, gate_state=dict(arguments.get("gate_state") or {}))
        return payload, "real_acceptance_release_finalizer", "knowledge_code_real_acceptance_closure_release_finalizer_read"
    return FinalReleaseGateFinalizer(workspace_path, workspace_id=workspace_id).read_release_finalizer(codebase_id), "real_acceptance_release_finalizer", None


def _ok(envelope, workspace_id: str, codebase_id: str, payload: dict[str, Any], key: str, next_action: str | None = None) -> dict[str, Any]:
    data = {key: _public_for(key, payload)}
    next_actions = [next_action] if next_action else None
    return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=next_actions, data=_with_v2(workspace_id, codebase_id, data, payload))


def _public_for(key: str, payload: dict[str, Any]) -> dict[str, Any]:
    if key == "real_acceptance_runtime_restore":
        return public_runtime_restore_payload(payload)
    if key == "real_acceptance_route_a_closure":
        return public_route_a_closure_payload(payload)
    if key == "real_acceptance_quality_decision":
        return public_quality_decision_payload(payload)
    if key == "real_acceptance_external_project_closure":
        return public_external_project_closure_payload(payload)
    return public_release_finalizer_payload(payload)


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


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body
