"""MCP tools for V2.63-V2.70 external E2E portal delivery stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .code_assets.envelope import v2_error_envelope, v2_success_envelope
from .code_assets.external_e2e_portal_delivery.contract_regression import PublicSurfaceContractRegressionService, public_contract_regression_payload
from .code_assets.external_e2e_portal_delivery.delivery import DeliveryCleanupVersioningService, public_delivery_payload
from .code_assets.external_e2e_portal_delivery.external_e2e import ExternalProjectFullE2EService, public_external_e2e_payload
from .code_assets.external_e2e_portal_delivery.maintainer_dashboard import MaintainerHomeStatusDashboardService, public_dashboard_payload
from .code_assets.external_e2e_portal_delivery.path_binding import ExternalRepositoryPathBindingService, public_path_binding_payload
from .code_assets.external_e2e_portal_delivery.portal_v3 import PortalV3ExperienceService, public_portal_v3_payload
from .code_assets.external_e2e_portal_delivery.surface_baseline import VersionedPublicSurfaceBaselineService, public_surface_baseline_payload
from .code_assets.external_e2e_portal_delivery.worktree_delivery import WorktreeDeliveryConsolidationService, public_worktree_delivery_payload


EXTERNAL_E2E_PORTAL_DELIVERY_TOOL_NAMES = {
    "knowledge_code_external_e2e_portal_delivery_e2e_build",
    "knowledge_code_external_e2e_portal_delivery_e2e_read",
    "knowledge_code_external_e2e_portal_delivery_portal_build",
    "knowledge_code_external_e2e_portal_delivery_portal_read",
    "knowledge_code_external_e2e_portal_delivery_delivery_build",
    "knowledge_code_external_e2e_portal_delivery_delivery_read",
    "knowledge_code_external_e2e_portal_delivery_contract_build",
    "knowledge_code_external_e2e_portal_delivery_contract_read",
    "knowledge_code_external_e2e_portal_delivery_path_binding_build",
    "knowledge_code_external_e2e_portal_delivery_path_binding_read",
    "knowledge_code_external_e2e_portal_delivery_worktree_delivery_build",
    "knowledge_code_external_e2e_portal_delivery_worktree_delivery_read",
    "knowledge_code_external_e2e_portal_delivery_surface_baseline_build",
    "knowledge_code_external_e2e_portal_delivery_surface_baseline_read",
    "knowledge_code_external_e2e_portal_delivery_dashboard_build",
    "knowledge_code_external_e2e_portal_delivery_dashboard_read",
}


def _schema(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    props = {"workspace_id": {"type": "string"}, "codebase_id": {"type": "string"}}
    props.update(extra or {})
    return {"type": "object", "properties": props, "required": ["workspace_id", "codebase_id"]}


EXTERNAL_E2E_PORTAL_DELIVERY_TOOL_SPECS = [
    {"name": "knowledge_code_external_e2e_portal_delivery_e2e_build", "description": "Build V2.63 external project full E2E artifacts", "inputSchema": _schema({"projects": {"type": "array"}})},
    {"name": "knowledge_code_external_e2e_portal_delivery_e2e_read", "description": "Read V2.63 external project full E2E artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_external_e2e_portal_delivery_portal_build", "description": "Build V2.64 Portal V3+ experience artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_external_e2e_portal_delivery_portal_read", "description": "Read V2.64 Portal V3+ experience artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_external_e2e_portal_delivery_delivery_build", "description": "Build V2.65 delivery cleanup and versioning artifacts", "inputSchema": _schema({"repo_root": {"type": "string"}})},
    {"name": "knowledge_code_external_e2e_portal_delivery_delivery_read", "description": "Read V2.65 delivery cleanup and versioning artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_external_e2e_portal_delivery_contract_build", "description": "Build V2.66 public surface contract regression artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_external_e2e_portal_delivery_contract_read", "description": "Read V2.66 public surface contract regression artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_external_e2e_portal_delivery_path_binding_build", "description": "Build V2.67 external repository path binding artifacts", "inputSchema": _schema({"projects": {"type": "array"}, "search_roots": {"type": "array"}})},
    {"name": "knowledge_code_external_e2e_portal_delivery_path_binding_read", "description": "Read V2.67 external repository path binding artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_external_e2e_portal_delivery_worktree_delivery_build", "description": "Build V2.68 worktree delivery consolidation artifacts", "inputSchema": _schema({"repo_root": {"type": "string"}})},
    {"name": "knowledge_code_external_e2e_portal_delivery_worktree_delivery_read", "description": "Read V2.68 worktree delivery consolidation artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_external_e2e_portal_delivery_surface_baseline_build", "description": "Build V2.69 versioned public surface baseline artifacts", "inputSchema": _schema({"baseline_label": {"type": "string"}})},
    {"name": "knowledge_code_external_e2e_portal_delivery_surface_baseline_read", "description": "Read V2.69 versioned public surface baseline artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_external_e2e_portal_delivery_dashboard_build", "description": "Build V2.70 maintainer home and status dashboard artifacts", "inputSchema": _schema()},
    {"name": "knowledge_code_external_e2e_portal_delivery_dashboard_read", "description": "Read V2.70 maintainer home and status dashboard artifacts", "inputSchema": _schema()},
]


def handle_external_e2e_portal_delivery_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in EXTERNAL_E2E_PORTAL_DELIVERY_TOOL_NAMES:
        raise ValueError(f"Unknown external E2E portal delivery tool: {name}")
    workspace_path = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace_path)
    workspace_id = str(meta["workspace_id"])
    codebase_id = str(arguments.get("codebase_id") or "").strip()
    if not codebase_id:
        return blocked(workspace_id=workspace_id, message="codebase_id is required", next_actions=["knowledge_codebase_list"], code="invalid_codebase_id")
    try:
        if name == "knowledge_code_external_e2e_portal_delivery_e2e_build":
            payload = ExternalProjectFullE2EService(workspace_path, workspace_id=workspace_id).build_e2e(codebase_id, projects=list(arguments.get("projects") or []))
            data = {"external_e2e_portal_delivery_e2e": public_external_e2e_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_e2e_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_e2e_read":
            payload = ExternalProjectFullE2EService(workspace_path, workspace_id=workspace_id).read_e2e(codebase_id)
            data = {"external_e2e_portal_delivery_e2e": public_external_e2e_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_portal_build":
            payload = PortalV3ExperienceService(workspace_path, workspace_id=workspace_id).build_portal(codebase_id)
            data = {"external_e2e_portal_delivery_portal": public_portal_v3_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_portal_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_portal_read":
            payload = PortalV3ExperienceService(workspace_path, workspace_id=workspace_id).read_portal(codebase_id)
            data = {"external_e2e_portal_delivery_portal": public_portal_v3_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_delivery_build":
            payload = DeliveryCleanupVersioningService(workspace_path, workspace_id=workspace_id).build_delivery(codebase_id, repo_root=arguments.get("repo_root"))
            data = {"external_e2e_portal_delivery_delivery": public_delivery_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_delivery_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_delivery_read":
            payload = DeliveryCleanupVersioningService(workspace_path, workspace_id=workspace_id).read_delivery(codebase_id)
            data = {"external_e2e_portal_delivery_delivery": public_delivery_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_contract_build":
            payload = PublicSurfaceContractRegressionService(workspace_path, workspace_id=workspace_id).build_contract(codebase_id)
            data = {"external_e2e_portal_delivery_contract": public_contract_regression_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_contract_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_contract_read":
            payload = PublicSurfaceContractRegressionService(workspace_path, workspace_id=workspace_id).read_contract(codebase_id)
            data = {"external_e2e_portal_delivery_contract": public_contract_regression_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_path_binding_build":
            payload = ExternalRepositoryPathBindingService(workspace_path, workspace_id=workspace_id).build_path_binding(codebase_id, projects=list(arguments.get("projects") or []), search_roots=list(arguments.get("search_roots") or []))
            data = {"external_e2e_portal_delivery_path_binding": public_path_binding_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_path_binding_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_path_binding_read":
            payload = ExternalRepositoryPathBindingService(workspace_path, workspace_id=workspace_id).read_path_binding(codebase_id)
            data = {"external_e2e_portal_delivery_path_binding": public_path_binding_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_worktree_delivery_build":
            payload = WorktreeDeliveryConsolidationService(workspace_path, workspace_id=workspace_id).build_worktree_delivery(codebase_id, repo_root=arguments.get("repo_root"))
            data = {"external_e2e_portal_delivery_worktree_delivery": public_worktree_delivery_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_worktree_delivery_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_worktree_delivery_read":
            payload = WorktreeDeliveryConsolidationService(workspace_path, workspace_id=workspace_id).read_worktree_delivery(codebase_id)
            data = {"external_e2e_portal_delivery_worktree_delivery": public_worktree_delivery_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_surface_baseline_build":
            payload = VersionedPublicSurfaceBaselineService(workspace_path, workspace_id=workspace_id).build_surface_baseline(codebase_id, baseline_label=str(arguments.get("baseline_label") or "v2.67-70"))
            data = {"external_e2e_portal_delivery_surface_baseline": public_surface_baseline_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_surface_baseline_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_surface_baseline_read":
            payload = VersionedPublicSurfaceBaselineService(workspace_path, workspace_id=workspace_id).read_surface_baseline(codebase_id)
            data = {"external_e2e_portal_delivery_surface_baseline": public_surface_baseline_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
        if name == "knowledge_code_external_e2e_portal_delivery_dashboard_build":
            payload = MaintainerHomeStatusDashboardService(workspace_path, workspace_id=workspace_id).build_dashboard(codebase_id)
            data = {"external_e2e_portal_delivery_dashboard": public_dashboard_payload(payload)}
            return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), next_actions=["knowledge_code_external_e2e_portal_delivery_dashboard_read"], data=_with_v2(workspace_id, codebase_id, data, payload))
        payload = MaintainerHomeStatusDashboardService(workspace_path, workspace_id=workspace_id).read_dashboard(codebase_id)
        data = {"external_e2e_portal_delivery_dashboard": public_dashboard_payload(payload)}
        return envelope(workspace_id=workspace_id, artifact_refs=payload.get("artifact_refs", []), data=_with_v2(workspace_id, codebase_id, data, payload))
    except FileNotFoundError as exc:
        message = str(exc)
        next_actions = [_next_action_for(message)]
        return envelope(
            workspace_id=workspace_id,
            status="blocked",
            warnings=[message],
            next_actions=next_actions,
            data={"error": {"code": message, "message": message, "retryable": False}, "v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=message, message=message, next_actions=next_actions)},
        )


def _next_action_for(message: str) -> str:
    if "PORTAL" in message:
        return "knowledge_code_external_e2e_portal_delivery_portal_build"
    if "DELIVERY" in message:
        return "knowledge_code_external_e2e_portal_delivery_delivery_build"
    if "CONTRACT" in message:
        return "knowledge_code_external_e2e_portal_delivery_contract_build"
    if "PATH_BINDING" in message:
        return "knowledge_code_external_e2e_portal_delivery_path_binding_build"
    if "WORKTREE_DELIVERY" in message:
        return "knowledge_code_external_e2e_portal_delivery_worktree_delivery_build"
    if "SURFACE_BASELINE" in message:
        return "knowledge_code_external_e2e_portal_delivery_surface_baseline_build"
    if "MAINTAINER_DASHBOARD" in message:
        return "knowledge_code_external_e2e_portal_delivery_dashboard_build"
    return "knowledge_code_external_e2e_portal_delivery_e2e_build"


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
