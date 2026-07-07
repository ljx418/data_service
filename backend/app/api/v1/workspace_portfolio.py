"""HTTP routes for workspace portfolio artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime
from data_service.workspace_portfolio import WorkspacePortfolioService, public_portfolio_payload

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Workspace Portfolio"], dependencies=[Depends(verify_knowledge_access)])


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _service(workspace_id: str) -> tuple[WorkspacePortfolioService, str]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return WorkspacePortfolioService(workspace, workspace_id=str(meta["workspace_id"])), str(meta["workspace_id"])


@router.post("/{workspace_id}/portfolio/scan")
async def scan_portfolio(workspace_id: str, payload: dict[str, Any] | None = None):
    service, resolved_workspace_id = _service(workspace_id)
    result = service.scan(root=str((payload or {}).get("root") or "/mnt/c/workspace"), limit=int((payload or {}).get("limit") or 120))
    return _ok(resolved_workspace_id, result, ["knowledge_workspace_portfolio_build"])


@router.post("/{workspace_id}/portfolio/build")
async def build_portfolio(workspace_id: str, payload: dict[str, Any] | None = None):
    service, resolved_workspace_id = _service(workspace_id)
    result = service.build(
        root=str((payload or {}).get("root") or "/mnt/c/workspace"),
        limit=int((payload or {}).get("limit") or 120),
        max_code_projects=int((payload or {}).get("max_code_projects") or 1),
    )
    return _ok(resolved_workspace_id, result, ["knowledge_workspace_portfolio_read", "knowledge_workspace_portfolio_report"])


@router.get("/{workspace_id}/portfolio")
async def read_portfolio(workspace_id: str):
    service, resolved_workspace_id = _service(workspace_id)
    try:
        result = service.read()
    except FileNotFoundError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc), "next_actions": ["knowledge_workspace_portfolio_scan"]})
    return _ok(resolved_workspace_id, result, ["knowledge_workspace_portfolio_build"])


@router.get("/{workspace_id}/portfolio/report")
async def read_portfolio_report(workspace_id: str):
    service, resolved_workspace_id = _service(workspace_id)
    try:
        result = service.report()
    except FileNotFoundError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc), "next_actions": ["knowledge_workspace_portfolio_build"]})
    return _ok(resolved_workspace_id, result, ["knowledge_workspace_portfolio_read"])


def _ok(workspace_id: str, result: dict[str, Any], next_actions: list[str]):
    public = public_portfolio_payload(result)
    return envelope(workspace_id=workspace_id, artifact_refs=public.get("artifact_refs", []), next_actions=next_actions, data={"workspace_portfolio": public})
