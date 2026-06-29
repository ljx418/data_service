"""MCP tools for V2.76-V2.80 project acceptance hardening stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.envelope import v2_error_envelope, v2_success_envelope
from .code_assets.project_acceptance_hardening.console_productization import MaintainerConsoleProductizationService, public_console_product_payload
from .code_assets.project_acceptance_hardening.external_project_binding import ExternalProjectRealBindingService, public_external_binding_payload
from .code_assets.project_acceptance_hardening.matrix_reconciliation import AcceptanceMatrixReconciliationService, public_matrix_reconciliation_payload
from .code_assets.project_acceptance_hardening.release_readiness import ReleaseReadinessClosureService, public_release_readiness_payload
from .code_assets.project_acceptance_hardening.warning_reduction import CIWarningReductionService, public_warning_reduction_payload


PROJECT_ACCEPTANCE_HARDENING_TOOL_NAMES = {
    "knowledge_code_project_acceptance_hardening_matrix_build",
    "knowledge_code_project_acceptance_hardening_matrix_read",
    "knowledge_code_project_acceptance_hardening_external_binding_build",
    "knowledge_code_project_acceptance_hardening_external_binding_read",
    "knowledge_code_project_acceptance_hardening_warning_reduction_build",
    "knowledge_code_project_acceptance_hardening_warning_reduction_read",
    "knowledge_code_project_acceptance_hardening_console_product_build",
    "knowledge_code_project_acceptance_hardening_console_product_read",
    "knowledge_code_project_acceptance_hardening_release_readiness_build",
    "knowledge_code_project_acceptance_hardening_release_readiness_read",
}


def _schema(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    props = {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}
    props.update(extra or {})
    return {"type": "object", "properties": props, "required": ["workspace_id", "codebase_id"]}


PROJECT_ACCEPTANCE_HARDENING_TOOL_SPECS = [
    {"name": "knowledge_code_project_acceptance_hardening_matrix_build", "description": "Build V2.76 acceptance matrix reconciliation artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_project_acceptance_hardening_matrix_read", "description": "Read V2.76 acceptance matrix reconciliation artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_project_acceptance_hardening_external_binding_build", "description": "Build V2.77 external project real binding artifacts", "inputSchema": _schema({"project_paths": {"type": "array"}})},
    {"name": "knowledge_code_project_acceptance_hardening_external_binding_read", "description": "Read V2.77 external project real binding artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_project_acceptance_hardening_warning_reduction_build", "description": "Build V2.78 CI warning reduction gate artifacts", "inputSchema": _schema({"command_results": {"type": "object"}})},
    {"name": "knowledge_code_project_acceptance_hardening_warning_reduction_read", "description": "Read V2.78 CI warning reduction gate artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_project_acceptance_hardening_console_product_build", "description": "Build V2.79 maintainer console productization artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_project_acceptance_hardening_console_product_read", "description": "Read V2.79 maintainer console productization artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_project_acceptance_hardening_release_readiness_build", "description": "Build V2.80 release readiness closure artifacts", "inputSchema": _schema({"approval_state": {"type": "object"}})},
    {"name": "knowledge_code_project_acceptance_hardening_release_readiness_read", "description": "Read V2.80 release readiness closure artifacts", "inputSchema": _schema()},
]


def handle_project_acceptance_hardening_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in PROJECT_ACCEPTANCE_HARDENING_TOOL_NAMES:
        raise ValueError(f"Unknown project acceptance hardening tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    try:
        if name == "knowledge_code_project_acceptance_hardening_matrix_build":
            payload = AcceptanceMatrixReconciliationService(workspace_path, workspace_id=workspace_id).build_reconciliation(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "project_acceptance_hardening_matrix", public_matrix_reconciliation_payload, "knowledge_code_project_acceptance_hardening_matrix_read")
        if name == "knowledge_code_project_acceptance_hardening_matrix_read":
            payload = AcceptanceMatrixReconciliationService(workspace_path, workspace_id=workspace_id).read_reconciliation(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "project_acceptance_hardening_matrix", public_matrix_reconciliation_payload)
        if name == "knowledge_code_project_acceptance_hardening_external_binding_build":
            payload = ExternalProjectRealBindingService(workspace_path, workspace_id=workspace_id).build_external_binding(codebase_id, project_paths=list(arguments.get("project_paths") or []))
            return _ok(envelope, workspace_id, codebase_id, payload, "project_acceptance_hardening_external_binding", public_external_binding_payload, "knowledge_code_project_acceptance_hardening_external_binding_read")
        if name == "knowledge_code_project_acceptance_hardening_external_binding_read":
            payload = ExternalProjectRealBindingService(workspace_path, workspace_id=workspace_id).read_external_binding(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "project_acceptance_hardening_external_binding", public_external_binding_payload)
        if name == "knowledge_code_project_acceptance_hardening_warning_reduction_build":
            payload = CIWarningReductionService(workspace_path, workspace_id=workspace_id).build_warning_reduction(codebase_id, command_results=dict(arguments.get("command_results") or {}))
            return _ok(envelope, workspace_id, codebase_id, payload, "project_acceptance_hardening_warning_reduction", public_warning_reduction_payload, "knowledge_code_project_acceptance_hardening_warning_reduction_read")
        if name == "knowledge_code_project_acceptance_hardening_warning_reduction_read":
            payload = CIWarningReductionService(workspace_path, workspace_id=workspace_id).read_warning_reduction(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "project_acceptance_hardening_warning_reduction", public_warning_reduction_payload)
        if name == "knowledge_code_project_acceptance_hardening_console_product_build":
            payload = MaintainerConsoleProductizationService(workspace_path, workspace_id=workspace_id).build_console_product(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "project_acceptance_hardening_console_product", public_console_product_payload, "knowledge_code_project_acceptance_hardening_console_product_read")
        if name == "knowledge_code_project_acceptance_hardening_console_product_read":
            payload = MaintainerConsoleProductizationService(workspace_path, workspace_id=workspace_id).read_console_product(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "project_acceptance_hardening_console_product", public_console_product_payload)
        if name == "knowledge_code_project_acceptance_hardening_release_readiness_build":
            payload = ReleaseReadinessClosureService(workspace_path, workspace_id=workspace_id).build_release_readiness(codebase_id, approval_state=dict(arguments.get("approval_state") or {}))
            return _ok(envelope, workspace_id, codebase_id, payload, "project_acceptance_hardening_release_readiness", public_release_readiness_payload, "knowledge_code_project_acceptance_hardening_release_readiness_read")
        payload = ReleaseReadinessClosureService(workspace_path, workspace_id=workspace_id).read_release_readiness(codebase_id)
        return _ok(envelope, workspace_id, codebase_id, payload, "project_acceptance_hardening_release_readiness", public_release_readiness_payload)
    except FileNotFoundError as exc:
        message = str(exc)
        next_action = _next_action_for(message)
        return envelope(workspace_id=workspace_id, status="blocked", warnings=[message], next_actions=[next_action], data={"error": {"code": message, "message": message, "retryable": False}, "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=message, message=message, next_actions=[next_action])})


def _ok(envelope, workspace_id: str, codebase_id: str, payload: dict[str, Any], key: str, public_payload, next_action: str | None = None) -> dict[str, Any]:
    data = {key: public_payload(payload)}
    next_actions = [next_action] if next_action else None
    return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=next_actions, data=_with_v2(workspace_id, codebase_id, data, payload))


def _next_action_for(message: str) -> str:
    if "EXTERNAL_PROJECT_REAL_BINDING" in message:
        return "knowledge_code_project_acceptance_hardening_external_binding_build"
    if "WARNING_REDUCTION" in message:
        return "knowledge_code_project_acceptance_hardening_warning_reduction_build"
    if "CONSOLE_PRODUCTIZATION" in message:
        return "knowledge_code_project_acceptance_hardening_console_product_build"
    if "RELEASE_READINESS" in message:
        return "knowledge_code_project_acceptance_hardening_release_readiness_build"
    return "knowledge_code_project_acceptance_hardening_matrix_build"


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body
