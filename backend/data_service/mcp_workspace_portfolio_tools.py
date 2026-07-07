"""MCP tools for workspace portfolio artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .workspace_portfolio import WorkspacePortfolioService, public_portfolio_payload


WORKSPACE_PORTFOLIO_TOOL_NAMES = {
    "knowledge_workspace_portfolio_scan",
    "knowledge_workspace_portfolio_build",
    "knowledge_workspace_portfolio_read",
    "knowledge_workspace_portfolio_report",
}


def _schema(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    props = {"workspace_id": {"type": "string"}}
    props.update(extra or {})
    return {"type": "object", "properties": props, "required": ["workspace_id"]}


WORKSPACE_PORTFOLIO_TOOL_SPECS = [
    {"name": "knowledge_workspace_portfolio_scan", "description": "Scan a real workspace root into project portfolio artifacts", "inputSchema": _schema({"root": {"type": "string"}, "limit": {"type": "integer", "default": 120}})},
    {
        "name": "knowledge_workspace_portfolio_build",
        "description": "Build workspace portfolio knowledge artifacts",
        "inputSchema": _schema(
            {
                "root": {"type": "string"},
                "limit": {"type": "integer", "default": 120},
                "max_code_projects": {"type": "integer", "default": 1},
            }
        ),
    },
    {"name": "knowledge_workspace_portfolio_read", "description": "Read workspace portfolio artifacts", "inputSchema": _schema()},
    {"name": "knowledge_workspace_portfolio_report", "description": "Read workspace portfolio HTML report and artifacts", "inputSchema": _schema()},
]


def handle_workspace_portfolio_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in WORKSPACE_PORTFOLIO_TOOL_NAMES:
        raise ValueError(f"Unknown workspace portfolio tool: {name}")
    workspace = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace)
    workspace_id = str(meta["workspace_id"])
    service = WorkspacePortfolioService(workspace, workspace_id=workspace_id)
    try:
        if name == "knowledge_workspace_portfolio_scan":
            payload = service.scan(root=str(arguments.get("root") or "/mnt/c/workspace"), limit=int(arguments.get("limit") or 120))
            next_actions = ["knowledge_workspace_portfolio_build"]
        elif name == "knowledge_workspace_portfolio_build":
            payload = service.build(
                root=str(arguments.get("root") or "/mnt/c/workspace"),
                limit=int(arguments.get("limit") or 120),
                max_code_projects=int(arguments.get("max_code_projects") or 1),
            )
            next_actions = ["knowledge_workspace_portfolio_read", "knowledge_workspace_portfolio_report"]
        elif name == "knowledge_workspace_portfolio_report":
            payload = service.report()
            next_actions = ["knowledge_workspace_portfolio_read"]
        else:
            payload = service.read()
            next_actions = ["knowledge_workspace_portfolio_build"]
    except FileNotFoundError as exc:
        return blocked(workspace_id=workspace_id, message=f"workspace portfolio artifact missing: {exc}", next_actions=["knowledge_workspace_portfolio_scan"], code="workspace_portfolio_not_built")
    public = public_portfolio_payload(payload)
    return envelope(workspace_id=workspace_id, artifact_refs=public.get("artifact_refs", []), next_actions=next_actions, data={"workspace_portfolio": public})
