"""MCP tools for V2.59-V2.62 stabilization stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.envelope import v2_error_envelope, v2_success_envelope
from .code_assets.stabilization_e2e_portal.e2e_expansion import RealProjectE2EExpansionService, public_e2e_payload
from .code_assets.stabilization_e2e_portal.packaging import AcceptancePackagingService, public_package_payload
from .code_assets.stabilization_e2e_portal.portal_integration import PortalUXIntegrationService, public_portal_payload
from .code_assets.stabilization_e2e_portal.public_surface import PublicSurfaceStabilizationService, public_surface_payload


STABILIZATION_E2E_PORTAL_TOOL_NAMES = {
    "knowledge_code_stabilization_surface_build",
    "knowledge_code_stabilization_surface_read",
    "knowledge_code_stabilization_e2e_build",
    "knowledge_code_stabilization_e2e_read",
    "knowledge_code_stabilization_package_build",
    "knowledge_code_stabilization_package_read",
    "knowledge_code_stabilization_portal_build",
    "knowledge_code_stabilization_portal_read",
}


def _schema(extra: dict[str, Any] | None = None, required_extra: list[str] | None = None) -> dict[str, Any]:
    props = {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}
    props.update(extra or {})
    return {"type": "object", "properties": props, "required": ["workspace_id", "codebase_id"] + list(required_extra or [])}


STABILIZATION_E2E_PORTAL_TOOL_SPECS = [
    {"name": "knowledge_code_stabilization_surface_build", "description": "Build V2.59 public surface stabilization artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_stabilization_surface_read", "description": "Read V2.59 public surface stabilization artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_stabilization_e2e_build", "description": "Build V2.60 real project E2E expansion artifacts", "inputSchema": _schema({"projects": {"type": "array"}})},
    {"name": "knowledge_code_stabilization_e2e_read", "description": "Read V2.60 real project E2E expansion artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_stabilization_package_build", "description": "Build V2.61 acceptance packaging artifacts", "inputSchema": _schema({"repo_root": {"type": "string"}})},
    {"name": "knowledge_code_stabilization_package_read", "description": "Read V2.61 acceptance packaging artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_stabilization_portal_build", "description": "Build V2.62 portal UX integration artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_stabilization_portal_read", "description": "Read V2.62 portal UX integration artifacts", "inputSchema": _schema()},
]


def handle_stabilization_e2e_portal_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in STABILIZATION_E2E_PORTAL_TOOL_NAMES:
        raise ValueError(f"Unknown stabilization tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    try:
        if name == "knowledge_code_stabilization_surface_build":
            payload = PublicSurfaceStabilizationService(workspace_path, workspace_id=workspace_id).build_surface(codebase_id)
            data = {"stabilization_surface": public_surface_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_stabilization_surface_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_stabilization_surface_read":
            payload = PublicSurfaceStabilizationService(workspace_path, workspace_id=workspace_id).read_surface(codebase_id)
            data = {"stabilization_surface": public_surface_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_stabilization_e2e_build":
            payload = RealProjectE2EExpansionService(workspace_path, workspace_id=workspace_id).build_e2e(codebase_id, projects=list(arguments.get("projects") or []))
            data = {"stabilization_e2e": public_e2e_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_stabilization_e2e_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_stabilization_e2e_read":
            payload = RealProjectE2EExpansionService(workspace_path, workspace_id=workspace_id).read_e2e(codebase_id)
            data = {"stabilization_e2e": public_e2e_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_stabilization_package_build":
            payload = AcceptancePackagingService(workspace_path, workspace_id=workspace_id).build_package(codebase_id, repo_root=arguments.get("repo_root"))
            data = {"stabilization_package": public_package_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_stabilization_package_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_stabilization_package_read":
            payload = AcceptancePackagingService(workspace_path, workspace_id=workspace_id).read_package(codebase_id)
            data = {"stabilization_package": public_package_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_stabilization_portal_build":
            payload = PortalUXIntegrationService(workspace_path, workspace_id=workspace_id).build_portal(codebase_id)
            data = {"stabilization_portal": public_portal_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_stabilization_portal_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        payload = PortalUXIntegrationService(workspace_path, workspace_id=workspace_id).read_portal(codebase_id)
        data = {"stabilization_portal": public_portal_payload(payload)}
        return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
    except FileNotFoundError as exc:
        message = str(exc)
        if "E2E" in message:
            next_actions = ["knowledge_code_stabilization_e2e_build"]
        elif "PACKAGING" in message:
            next_actions = ["knowledge_code_stabilization_package_build"]
        elif "PORTAL" in message:
            next_actions = ["knowledge_code_stabilization_portal_build"]
        else:
            next_actions = ["knowledge_code_stabilization_surface_build"]
        return envelope(
            workspace_id=workspace_id,
            status="blocked",
            warnings=[message],
            next_actions=next_actions,
            data={"error": {"code": message, "message": message, "retryable": False}, "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=message, message=message, next_actions=next_actions)},
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
