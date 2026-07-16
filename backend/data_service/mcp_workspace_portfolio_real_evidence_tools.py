"""MCP tools for V2.116-V2.120 workspace portfolio real evidence acceptance."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from .workspace_portfolio_real_evidence_acceptance import WorkspacePortfolioRealEvidenceService, public_real_evidence_payload


WORKSPACE_PORTFOLIO_REAL_EVIDENCE_TOOL_NAMES = {
    "knowledge_workspace_portfolio_real_evidence_plan",
    "knowledge_workspace_portfolio_real_evidence_build",
    "knowledge_workspace_portfolio_real_evidence_read",
    "knowledge_workspace_portfolio_real_evidence_report",
}


def _schema(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    props = {"workspace_id": {"type": "string"}}
    props.update(extra or {})
    return {"type": "object", "properties": props, "required": ["workspace_id"]}


WORKSPACE_PORTFOLIO_REAL_EVIDENCE_TOOL_SPECS = [
    {"name": "knowledge_workspace_portfolio_real_evidence_plan", "description": "Plan V2.116-V2.120 portfolio real evidence acceptance closure from a real workspace root", "inputSchema": _schema({"root": {"type": "string"}, "limit": {"type": "integer", "default": 120}})},
    {
        "name": "knowledge_workspace_portfolio_real_evidence_build",
        "description": "Build V2.116-V2.120 portfolio real evidence acceptance artifacts",
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
    {"name": "knowledge_workspace_portfolio_real_evidence_read", "description": "Read V2.116-V2.120 portfolio real evidence acceptance artifacts", "inputSchema": _schema()},
    {"name": "knowledge_workspace_portfolio_real_evidence_report", "description": "Read V2.116-V2.120 final acceptance HTML report and artifacts", "inputSchema": _schema()},
]


def handle_workspace_portfolio_real_evidence_tool(
    name: str,
    arguments: dict[str, Any],
    *,
    blocked: Callable[..., dict[str, Any]],
    envelope: Callable[..., dict[str, Any]],
    ensure_workspace_meta: Callable[..., dict[str, Any]],
    resolve_workspace: Callable[[str | None, str | None], Path],
) -> dict[str, Any]:
    if name not in WORKSPACE_PORTFOLIO_REAL_EVIDENCE_TOOL_NAMES:
        raise ValueError(f"Unknown workspace portfolio real evidence tool: {name}")
    workspace = resolve_workspace(arguments.get("workspace_id"), None)
    meta = ensure_workspace_meta(workspace)
    workspace_id = str(meta["workspace_id"])
    service = WorkspacePortfolioRealEvidenceService(workspace, workspace_id=workspace_id)
    try:
        if name == "knowledge_workspace_portfolio_real_evidence_plan":
            payload = service.plan(root=str(arguments.get("root") or "/mnt/c/workspace"), limit=int(arguments.get("limit") or 120))
            next_actions = ["knowledge_workspace_portfolio_real_evidence_build"]
        elif name == "knowledge_workspace_portfolio_real_evidence_build":
            payload = service.build(
                root=str(arguments.get("root") or "/mnt/c/workspace"),
                limit=int(arguments.get("limit") or 120),
                max_code_projects=int(arguments.get("max_code_projects") or 3),
                timeout_seconds=int(arguments.get("timeout_seconds") or 120),
                headless=bool(arguments.get("headless", True)),
            )
            next_actions = ["knowledge_workspace_portfolio_real_evidence_read", "knowledge_workspace_portfolio_real_evidence_report"]
        elif name == "knowledge_workspace_portfolio_real_evidence_report":
            payload = service.report()
            next_actions = ["knowledge_workspace_portfolio_real_evidence_read"]
        else:
            payload = service.read()
            next_actions = ["knowledge_workspace_portfolio_real_evidence_build"]
    except FileNotFoundError as exc:
        return blocked(
            workspace_id=workspace_id,
            message=f"workspace portfolio real evidence artifact missing: {exc}",
            next_actions=["knowledge_workspace_portfolio_real_evidence_build"],
            code="workspace_portfolio_real_evidence_not_built",
        )
    public = public_real_evidence_payload(payload)
    return envelope(workspace_id=workspace_id, artifact_refs=public.get("artifact_refs", []), next_actions=next_actions, data={"workspace_portfolio_real_evidence": public})
