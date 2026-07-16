"""MCP tools for V2.111-V2.115 workspace portfolio final acceptance."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .workspace_portfolio_final_acceptance import WorkspacePortfolioFinalAcceptanceService, public_final_acceptance_payload


WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_TOOL_NAMES = {
    "knowledge_workspace_portfolio_final_acceptance_plan",
    "knowledge_workspace_portfolio_final_acceptance_build",
    "knowledge_workspace_portfolio_final_acceptance_read",
    "knowledge_workspace_portfolio_final_acceptance_report",
}


def _schema(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    props = {"workspace_id": {"type": "string"}}
    props.update(extra or {})
    return {"type": "object", "properties": props, "required": ["workspace_id"]}


WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_TOOL_SPECS = [
    {"name": "knowledge_workspace_portfolio_final_acceptance_plan", "description": "Plan V2.111-V2.115 portfolio final acceptance closure from a real workspace root", "inputSchema": _schema({"root": {"type": "string"}, "limit": {"type": "integer", "default": 120}})},
    {
        "name": "knowledge_workspace_portfolio_final_acceptance_build",
        "description": "Build V2.111-V2.115 portfolio final acceptance artifacts",
        "inputSchema": _schema(
            {
                "root": {"type": "string"},
                "limit": {"type": "integer", "default": 120},
                "max_code_projects": {"type": "integer", "default": 3},
                "timeout_seconds": {"type": "integer", "default": 120},
                "headless": {"type": "boolean", "default": True},
            }
        ),
    },
    {"name": "knowledge_workspace_portfolio_final_acceptance_read", "description": "Read V2.111-V2.115 portfolio final acceptance artifacts", "inputSchema": _schema()},
    {"name": "knowledge_workspace_portfolio_final_acceptance_report", "description": "Read V2.111-V2.115 final acceptance HTML report and artifacts", "inputSchema": _schema()},
]


def handle_workspace_portfolio_final_acceptance_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_TOOL_NAMES:
        raise ValueError(f"Unknown workspace portfolio final acceptance tool: {name}")
    workspace = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace)
    workspace_id = str(meta["workspace_id"])
    service = WorkspacePortfolioFinalAcceptanceService(workspace, workspace_id=workspace_id)
    try:
        if name == "knowledge_workspace_portfolio_final_acceptance_plan":
            payload = service.plan(root=str(arguments.get("root") or "/mnt/c/workspace"), limit=int(arguments.get("limit") or 120))
            next_actions = ["knowledge_workspace_portfolio_final_acceptance_build"]
        elif name == "knowledge_workspace_portfolio_final_acceptance_build":
            payload = service.build(
                root=str(arguments.get("root") or "/mnt/c/workspace"),
                limit=int(arguments.get("limit") or 120),
                max_code_projects=int(arguments.get("max_code_projects") or 3),
                timeout_seconds=int(arguments.get("timeout_seconds") or 120),
                headless=bool(arguments.get("headless", True)),
            )
            next_actions = ["knowledge_workspace_portfolio_final_acceptance_read", "knowledge_workspace_portfolio_final_acceptance_report"]
        elif name == "knowledge_workspace_portfolio_final_acceptance_report":
            payload = service.report()
            next_actions = ["knowledge_workspace_portfolio_final_acceptance_read"]
        else:
            payload = service.read()
            next_actions = ["knowledge_workspace_portfolio_final_acceptance_build"]
    except FileNotFoundError as exc:
        return blocked(
            workspace_id=workspace_id,
            message=f"workspace portfolio final acceptance artifact missing: {exc}",
            next_actions=["knowledge_workspace_portfolio_final_acceptance_build"],
            code="workspace_portfolio_final_acceptance_not_built",
        )
    public = public_final_acceptance_payload(payload)
    return envelope(workspace_id=workspace_id, artifact_refs=public.get("artifact_refs", []), next_actions=next_actions, data={"workspace_portfolio_final_acceptance": public})
