"""HTTP routes for V2.111-V2.115 workspace portfolio final acceptance."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime
from data_service.workspace_portfolio_final_acceptance import WorkspacePortfolioFinalAcceptanceService, public_final_acceptance_payload

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Workspace Portfolio Final Acceptance"], dependencies=[Depends(verify_knowledge_access)])


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _service(workspace_id: str) -> tuple[WorkspacePortfolioFinalAcceptanceService, str]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return WorkspacePortfolioFinalAcceptanceService(workspace, workspace_id=str(meta["workspace_id"])), str(meta["workspace_id"])


@router.post("/{workspace_id}/portfolio-final-acceptance/plan")
async def plan_portfolio_final_acceptance(workspace_id: str, payload: dict[str, Any] | None = None):
    service, resolved_workspace_id = _service(workspace_id)
    result = service.plan(root=str((payload or {}).get("root") or "/mnt/c/workspace"), limit=int((payload or {}).get("limit") or 120))
    return _ok(resolved_workspace_id, result, ["knowledge_workspace_portfolio_final_acceptance_build"])


@router.post("/{workspace_id}/portfolio-final-acceptance/build")
async def build_portfolio_final_acceptance(workspace_id: str, payload: dict[str, Any] | None = None):
    service, resolved_workspace_id = _service(workspace_id)
    result = service.build(
        root=str((payload or {}).get("root") or "/mnt/c/workspace"),
        limit=int((payload or {}).get("limit") or 120),
        max_code_projects=int((payload or {}).get("max_code_projects") or 3),
        timeout_seconds=int((payload or {}).get("timeout_seconds") or 120),
        headless=bool((payload or {}).get("headless", True)),
    )
    return _ok(resolved_workspace_id, result, ["knowledge_workspace_portfolio_final_acceptance_read", "knowledge_workspace_portfolio_final_acceptance_report"])


@router.get("/{workspace_id}/portfolio-final-acceptance")
async def read_portfolio_final_acceptance(workspace_id: str):
    service, resolved_workspace_id = _service(workspace_id)
    try:
        result = service.read()
    except FileNotFoundError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc), "next_actions": ["knowledge_workspace_portfolio_final_acceptance_build"]})
    return _ok(resolved_workspace_id, result, ["knowledge_workspace_portfolio_final_acceptance_build"])


@router.get("/{workspace_id}/portfolio-final-acceptance/report")
async def read_portfolio_final_acceptance_report(workspace_id: str):
    service, resolved_workspace_id = _service(workspace_id)
    try:
        result = service.report()
    except FileNotFoundError as exc:
        return JSONResponse(status_code=404, content={"error": str(exc), "next_actions": ["knowledge_workspace_portfolio_final_acceptance_build"]})
    return _ok(resolved_workspace_id, result, ["knowledge_workspace_portfolio_final_acceptance_read"])


def _ok(workspace_id: str, result: dict[str, Any], next_actions: list[str]):
    public = public_final_acceptance_payload(result)
    return envelope(workspace_id=workspace_id, artifact_refs=public.get("artifact_refs", []), next_actions=next_actions, data={"workspace_portfolio_final_acceptance": public})
