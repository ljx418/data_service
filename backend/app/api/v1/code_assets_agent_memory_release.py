"""HTTP routes for V2.71-V2.75 agent memory release stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, JSONResponse

from data_service.code_assets.agent_memory_release.agent_memory import AgentMemoryService, public_agent_memory_payload
from data_service.code_assets.agent_memory_release.ci_warning_governance import CIWarningGovernanceService, public_ci_warning_governance_payload
from data_service.code_assets.agent_memory_release.external_project_closure import ExternalProjectClosureService, public_external_project_closure_payload
from data_service.code_assets.agent_memory_release.interactive_console import InteractiveMaintainerConsoleService, public_interactive_console_payload
from data_service.code_assets.agent_memory_release.release_restore import ReleaseRestoreService, public_release_restore_payload
from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Agent Memory Release"], dependencies=[Depends(verify_knowledge_access)])


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-memory-release/external-closure/build")
async def build_external_closure(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = ExternalProjectClosureService(workspace, workspace_id=str(meta["workspace_id"])).build_external_project_closure(codebase_id, projects=list((payload or {}).get("projects") or []))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_agent_memory_release_external_closure_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "agent_memory_release_external_closure", public_external_project_closure_payload, "knowledge_code_agent_memory_release_external_closure_read")


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-memory-release/external-closure")
async def read_external_closure(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = ExternalProjectClosureService(workspace, workspace_id=str(meta["workspace_id"])).read_external_project_closure(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_agent_memory_release_external_closure_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "agent_memory_release_external_closure", public_external_project_closure_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-memory-release/ci-governance/build")
async def build_ci_governance(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = CIWarningGovernanceService(workspace, workspace_id=str(meta["workspace_id"])).build_ci_warning_governance(codebase_id, command_results=dict((payload or {}).get("command_results") or {}))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_agent_memory_release_ci_governance_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "agent_memory_release_ci_governance", public_ci_warning_governance_payload, "knowledge_code_agent_memory_release_ci_governance_read")


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-memory-release/ci-governance")
async def read_ci_governance(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = CIWarningGovernanceService(workspace, workspace_id=str(meta["workspace_id"])).read_ci_warning_governance(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_agent_memory_release_ci_governance_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "agent_memory_release_ci_governance", public_ci_warning_governance_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-memory-release/memory/build")
async def build_memory(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = AgentMemoryService(workspace, workspace_id=str(meta["workspace_id"])).build_agent_memory(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_agent_memory_release_memory_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "agent_memory_release_memory", public_agent_memory_payload, "knowledge_code_agent_memory_release_memory_read")


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-memory-release/memory")
async def read_memory(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = AgentMemoryService(workspace, workspace_id=str(meta["workspace_id"])).read_agent_memory(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_agent_memory_release_memory_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "agent_memory_release_memory", public_agent_memory_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-memory-release/console/build")
async def build_console(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = InteractiveMaintainerConsoleService(workspace, workspace_id=str(meta["workspace_id"])).build_interactive_console(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_agent_memory_release_console_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "agent_memory_release_console", public_interactive_console_payload, "knowledge_code_agent_memory_release_console_read")


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-memory-release/console")
async def read_console(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = InteractiveMaintainerConsoleService(workspace, workspace_id=str(meta["workspace_id"])).read_interactive_console(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_agent_memory_release_console_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "agent_memory_release_console", public_interactive_console_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-memory-release/console/view")
async def view_console(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = InteractiveMaintainerConsoleService(workspace, workspace_id=str(meta["workspace_id"])).read_interactive_console(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_agent_memory_release_console_build")
    return HTMLResponse(content=str(result.get("maintainer_console_html") or ""), status_code=200)


@router.post("/{workspace_id}/codebases/{codebase_id}/agent-memory-release/release-restore/build")
async def build_release_restore(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = ReleaseRestoreService(workspace, workspace_id=str(meta["workspace_id"])).build_release_restore(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_agent_memory_release_release_restore_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "agent_memory_release_release_restore", public_release_restore_payload, "knowledge_code_agent_memory_release_release_restore_read")


@router.get("/{workspace_id}/codebases/{codebase_id}/agent-memory-release/release-restore")
async def read_release_restore(workspace_id: str, codebase_id: str):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = ReleaseRestoreService(workspace, workspace_id=str(meta["workspace_id"])).read_release_restore(codebase_id)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), "knowledge_code_agent_memory_release_release_restore_build")
    return _ok(str(meta["workspace_id"]), codebase_id, result, "agent_memory_release_release_restore", public_release_restore_payload)


def _ok(workspace_id: str, codebase_id: str, result: dict[str, Any], key: str, public_payload, next_action: str | None = None):
    data = {key: public_payload(result)}
    next_actions = [next_action] if next_action else None
    return envelope(workspace_id=workspace_id, artifact_refs=result.get("artifact_refs", []), next_actions=next_actions, data=_with_v2(workspace_id, codebase_id, data, result))


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body


def _error(status_code: int, workspace_id: str, codebase_id: str, error: str, next_action: str):
    payload = {"v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=error, message=error, next_actions=[next_action])}
    return JSONResponse(status_code=status_code, content=payload)

