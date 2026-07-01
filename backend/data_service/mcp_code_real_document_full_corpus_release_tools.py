"""MCP tools for V2.86-V2.90 full corpus release hardening."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.envelope import v2_error_envelope, v2_success_envelope
from .code_assets.real_document_full_corpus_release.external_project_closure import ExternalProjectE2EClosureService, public_external_project_payload
from .code_assets.real_document_full_corpus_release.full_corpus import FullCorpusE2EHardeningService, public_full_corpus_payload
from .code_assets.real_document_full_corpus_release.quality_review import QualityReviewClosureService, public_quality_review_payload
from .code_assets.real_document_full_corpus_release.release_gate import ReleaseGateRestoreHygieneService, public_release_gate_payload
from .code_assets.real_document_full_corpus_release.route_a_acceptance import RouteAAcceptanceService, public_route_a_payload


REAL_DOCUMENT_FULL_CORPUS_RELEASE_TOOL_NAMES = {
    "knowledge_code_real_document_full_corpus_release_full_corpus_build",
    "knowledge_code_real_document_full_corpus_release_full_corpus_read",
    "knowledge_code_real_document_full_corpus_release_route_a_build",
    "knowledge_code_real_document_full_corpus_release_route_a_read",
    "knowledge_code_real_document_full_corpus_release_quality_review_build",
    "knowledge_code_real_document_full_corpus_release_quality_review_read",
    "knowledge_code_real_document_full_corpus_release_external_project_build",
    "knowledge_code_real_document_full_corpus_release_external_project_read",
    "knowledge_code_real_document_full_corpus_release_release_gate_build",
    "knowledge_code_real_document_full_corpus_release_release_gate_read",
}


def _schema(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    props = {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}
    props.update(extra or {})
    return {"type": "object", "properties": props, "required": ["workspace_id", "codebase_id"]}


REAL_DOCUMENT_FULL_CORPUS_RELEASE_TOOL_SPECS = [
    {"name": "knowledge_code_real_document_full_corpus_release_full_corpus_build", "description": "Build V2.86 full corpus E2E artifacts", "inputSchema": _schema({"options": {"type": "object"}})},
    {"name": "knowledge_code_real_document_full_corpus_release_full_corpus_read", "description": "Read V2.86 full corpus E2E artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_document_full_corpus_release_route_a_build", "description": "Build V2.87 Route A representative acceptance artifacts", "inputSchema": _schema({"acceptance_state": {"type": "object"}})},
    {"name": "knowledge_code_real_document_full_corpus_release_route_a_read", "description": "Read V2.87 Route A representative acceptance artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_document_full_corpus_release_quality_review_build", "description": "Build V2.88 quality review closure artifacts", "inputSchema": _schema({"review_state": {"type": "object"}})},
    {"name": "knowledge_code_real_document_full_corpus_release_quality_review_read", "description": "Read V2.88 quality review closure artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_document_full_corpus_release_external_project_build", "description": "Build V2.89 external project E2E closure artifacts", "inputSchema": _schema({"project_paths": {"type": "object"}})},
    {"name": "knowledge_code_real_document_full_corpus_release_external_project_read", "description": "Read V2.89 external project E2E closure artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_real_document_full_corpus_release_release_gate_build", "description": "Build V2.90 release gate artifacts", "inputSchema": _schema({"gate_state": {"type": "object"}})},
    {"name": "knowledge_code_real_document_full_corpus_release_release_gate_read", "description": "Read V2.90 release gate artifacts", "inputSchema": _schema()},
]


def handle_real_document_full_corpus_release_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in REAL_DOCUMENT_FULL_CORPUS_RELEASE_TOOL_NAMES:
        raise ValueError(f"Unknown real document full corpus release tool: {name}")
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
    if name == "knowledge_code_real_document_full_corpus_release_full_corpus_build":
        payload = FullCorpusE2EHardeningService(workspace_path, workspace_id=workspace_id).build_full_corpus(codebase_id, options=dict(arguments.get("options") or {}))
        return payload, "real_document_full_corpus", "knowledge_code_real_document_full_corpus_release_full_corpus_read"
    if name == "knowledge_code_real_document_full_corpus_release_full_corpus_read":
        return FullCorpusE2EHardeningService(workspace_path, workspace_id=workspace_id).read_full_corpus(codebase_id), "real_document_full_corpus", None
    if name == "knowledge_code_real_document_full_corpus_release_route_a_build":
        payload = RouteAAcceptanceService(workspace_path, workspace_id=workspace_id).build_route_a(codebase_id, acceptance_state=dict(arguments.get("acceptance_state") or {}))
        return payload, "real_document_route_a_acceptance", "knowledge_code_real_document_full_corpus_release_route_a_read"
    if name == "knowledge_code_real_document_full_corpus_release_route_a_read":
        return RouteAAcceptanceService(workspace_path, workspace_id=workspace_id).read_route_a(codebase_id), "real_document_route_a_acceptance", None
    if name == "knowledge_code_real_document_full_corpus_release_quality_review_build":
        payload = QualityReviewClosureService(workspace_path, workspace_id=workspace_id).build_quality_review(codebase_id, review_state=dict(arguments.get("review_state") or {}))
        return payload, "real_document_quality_review", "knowledge_code_real_document_full_corpus_release_quality_review_read"
    if name == "knowledge_code_real_document_full_corpus_release_quality_review_read":
        return QualityReviewClosureService(workspace_path, workspace_id=workspace_id).read_quality_review(codebase_id), "real_document_quality_review", None
    if name == "knowledge_code_real_document_full_corpus_release_external_project_build":
        payload = ExternalProjectE2EClosureService(workspace_path, workspace_id=workspace_id).build_external_project(codebase_id, project_paths=dict(arguments.get("project_paths") or {}))
        return payload, "real_document_external_project", "knowledge_code_real_document_full_corpus_release_external_project_read"
    if name == "knowledge_code_real_document_full_corpus_release_external_project_read":
        return ExternalProjectE2EClosureService(workspace_path, workspace_id=workspace_id).read_external_project(codebase_id), "real_document_external_project", None
    if name == "knowledge_code_real_document_full_corpus_release_release_gate_build":
        payload = ReleaseGateRestoreHygieneService(workspace_path, workspace_id=workspace_id).build_release_gate(codebase_id, gate_state=dict(arguments.get("gate_state") or {}))
        return payload, "real_document_release_gate", "knowledge_code_real_document_full_corpus_release_release_gate_read"
    return ReleaseGateRestoreHygieneService(workspace_path, workspace_id=workspace_id).read_release_gate(codebase_id), "real_document_release_gate", None


def _ok(envelope, workspace_id: str, codebase_id: str, payload: dict[str, Any], key: str, next_action: str | None = None) -> dict[str, Any]:
    data = {key: _public_for(key, payload)}
    next_actions = [next_action] if next_action else None
    return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=next_actions, data=_with_v2(workspace_id, codebase_id, data, payload))


def _public_for(key: str, payload: dict[str, Any]) -> dict[str, Any]:
    if key == "real_document_full_corpus":
        return public_full_corpus_payload(payload)
    if key == "real_document_route_a_acceptance":
        return public_route_a_payload(payload)
    if key == "real_document_quality_review":
        return public_quality_review_payload(payload)
    if key == "real_document_external_project":
        return public_external_project_payload(payload)
    return public_release_gate_payload(payload)


def _next_action_for(message: str) -> str:
    if "FULL_CORPUS" in message:
        return "knowledge_code_real_document_full_corpus_release_full_corpus_build"
    if "ROUTE_A" in message:
        return "knowledge_code_real_document_full_corpus_release_route_a_build"
    if "QUALITY_REVIEW" in message:
        return "knowledge_code_real_document_full_corpus_release_quality_review_build"
    if "EXTERNAL_PROJECT" in message:
        return "knowledge_code_real_document_full_corpus_release_external_project_build"
    return "knowledge_code_real_document_full_corpus_release_release_gate_build"


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body
