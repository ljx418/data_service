"""MCP tools for V2.81-V2.85 real document acceptance stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.envelope import v2_error_envelope, v2_success_envelope
from .code_assets.real_document_acceptance.service import RealDocumentAcceptanceService, public_real_document_payload


REAL_DOCUMENT_ACCEPTANCE_TOOL_NAMES = {
    "knowledge_code_real_document_acceptance_sample_contract_build",
    "knowledge_code_real_document_acceptance_sample_contract_read",
    "knowledge_code_real_document_acceptance_real_e2e_build",
    "knowledge_code_real_document_acceptance_real_e2e_read",
    "knowledge_code_real_document_acceptance_retrieval_trace_build",
    "knowledge_code_real_document_acceptance_retrieval_trace_read",
    "knowledge_code_real_document_acceptance_quality_build",
    "knowledge_code_real_document_acceptance_quality_read",
    "knowledge_code_real_document_acceptance_release_closure_build",
    "knowledge_code_real_document_acceptance_release_closure_read",
}


def _schema(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    props = {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}
    props.update(extra or {})
    return {"type": "object", "properties": props, "required": ["workspace_id", "codebase_id"]}


REAL_DOCUMENT_ACCEPTANCE_TOOL_SPECS = [
    {"name": "knowledge_code_real_document_acceptance_sample_contract_build", "description": "Build V2.81 real document sample contract artifacts", "inputSchema": _schema({"sample_config": {"type": "object"}})},
    {"name": "knowledge_code_real_document_acceptance_sample_contract_read", "description": "Read V2.81 real document sample contract artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_document_acceptance_real_e2e_build", "description": "Build V2.82 real document import and wiki acceptance artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_document_acceptance_real_e2e_read", "description": "Read V2.82 real document import and wiki acceptance artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_document_acceptance_retrieval_trace_build", "description": "Build V2.83 retrieval, GraphRAG, and source trace acceptance artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_document_acceptance_retrieval_trace_read", "description": "Read V2.83 retrieval, GraphRAG, and source trace acceptance artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_document_acceptance_quality_build", "description": "Build V2.84 real document quality governance acceptance artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_document_acceptance_quality_read", "description": "Read V2.84 real document quality governance acceptance artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_document_acceptance_release_closure_build", "description": "Build V2.85 real document release closure rerun artifacts", "inputSchema": _schema({"approval_state": {"type": "object"}})},
    {"name": "knowledge_code_real_document_acceptance_release_closure_read", "description": "Read V2.85 real document release closure rerun artifacts", "inputSchema": _schema()},
]


def handle_real_document_acceptance_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in REAL_DOCUMENT_ACCEPTANCE_TOOL_NAMES:
        raise ValueError(f"Unknown real document acceptance tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    service = RealDocumentAcceptanceService(workspace_path, workspace_id=workspace_id)
    try:
        if name == "knowledge_code_real_document_acceptance_sample_contract_build":
            payload = service.build_sample_contract(codebase_id, sample_config=dict(arguments.get("sample_config") or {}))
            return _ok(envelope, workspace_id, codebase_id, payload, "real_document_acceptance_sample_contract", "knowledge_code_real_document_acceptance_sample_contract_read")
        if name == "knowledge_code_real_document_acceptance_sample_contract_read":
            payload = service.read_sample_contract(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "real_document_acceptance_sample_contract")
        if name == "knowledge_code_real_document_acceptance_real_e2e_build":
            payload = service.build_real_e2e(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "real_document_acceptance_real_e2e", "knowledge_code_real_document_acceptance_real_e2e_read")
        if name == "knowledge_code_real_document_acceptance_real_e2e_read":
            payload = service.read_real_e2e(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "real_document_acceptance_real_e2e")
        if name == "knowledge_code_real_document_acceptance_retrieval_trace_build":
            payload = service.build_retrieval_trace(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "real_document_acceptance_retrieval_trace", "knowledge_code_real_document_acceptance_retrieval_trace_read")
        if name == "knowledge_code_real_document_acceptance_retrieval_trace_read":
            payload = service.read_retrieval_trace(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "real_document_acceptance_retrieval_trace")
        if name == "knowledge_code_real_document_acceptance_quality_build":
            payload = service.build_quality(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "real_document_acceptance_quality", "knowledge_code_real_document_acceptance_quality_read")
        if name == "knowledge_code_real_document_acceptance_quality_read":
            payload = service.read_quality(codebase_id)
            return _ok(envelope, workspace_id, codebase_id, payload, "real_document_acceptance_quality")
        if name == "knowledge_code_real_document_acceptance_release_closure_build":
            payload = service.build_release_closure(codebase_id, approval_state=dict(arguments.get("approval_state") or {}))
            return _ok(envelope, workspace_id, codebase_id, payload, "real_document_acceptance_release_closure", "knowledge_code_real_document_acceptance_release_closure_read")
        payload = service.read_release_closure(codebase_id)
        return _ok(envelope, workspace_id, codebase_id, payload, "real_document_acceptance_release_closure")
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


def _ok(envelope, workspace_id: str, codebase_id: str, payload: dict[str, Any], key: str, next_action: str | None = None) -> dict[str, Any]:
    data = {key: public_real_document_payload(payload)}
    next_actions = [next_action] if next_action else None
    return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=next_actions, data=_with_v2(workspace_id, codebase_id, data, payload))


def _next_action_for(message: str) -> str:
    if "REAL_DOCUMENT_SAMPLE" in message:
        return "knowledge_code_real_document_acceptance_sample_contract_build"
    if "REAL_DOCUMENT_E2E" in message:
        return "knowledge_code_real_document_acceptance_real_e2e_build"
    if "RETRIEVAL_TRACE" in message:
        return "knowledge_code_real_document_acceptance_retrieval_trace_build"
    if "QUALITY_ACCEPTANCE" in message:
        return "knowledge_code_real_document_acceptance_quality_build"
    if "RELEASE_CLOSURE" in message:
        return "knowledge_code_real_document_acceptance_release_closure_build"
    return "knowledge_code_real_document_acceptance_sample_contract_build"


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body
