"""CLI subcommands for V2.111-V2.115 workspace portfolio final acceptance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .mcp_workspace_runtime import WorkspaceRuntime
from .workspace_portfolio_final_acceptance import WorkspacePortfolioFinalAcceptanceService, public_final_acceptance_payload


def add_portfolio_final_acceptance_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("portfolio-final-acceptance", help="Build and read V2.111-V2.115 portfolio final acceptance artifacts")
    commands = parser.add_subparsers(dest="portfolio_final_acceptance_command", required=True)
    for name in ("plan", "build", "read", "report"):
        command = commands.add_parser(name)
        command.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        command.add_argument("--workspace-id", required=True)
        if name in {"plan", "build"}:
            command.add_argument("--root", default="/mnt/c/workspace", help="Read-only workspace root to scan")
            command.add_argument("--limit", type=int, default=120, help="Maximum first-level entries to scan")
        if name == "build":
            command.add_argument("--max-code-projects", type=int, default=3, help="Maximum discovered code projects to include in one bounded run")
            command.add_argument("--timeout-seconds", type=int, default=120, help="Per-project command timeout budget")
            command.add_argument("--headless", action="store_true", help="Request headless UI evidence mode")


def run_portfolio_final_acceptance_command(args: argparse.Namespace) -> int:
    root = Path(args.workspace_root).expanduser() if getattr(args, "workspace_root", None) else None
    runtime = WorkspaceRuntime((root / "_default") if root else (Path.cwd() / "workspace"), workspace_root=root)
    workspace = runtime.resolve_workspace(getattr(args, "workspace_id", None), None)
    meta = runtime.ensure_workspace_meta(workspace)
    service = WorkspacePortfolioFinalAcceptanceService(workspace, workspace_id=str(meta["workspace_id"]))
    if args.portfolio_final_acceptance_command == "plan":
        payload = service.plan(root=getattr(args, "root"), limit=int(getattr(args, "limit", 120)))
    elif args.portfolio_final_acceptance_command == "build":
        payload = service.build(
            root=getattr(args, "root"),
            limit=int(getattr(args, "limit", 120)),
            max_code_projects=int(getattr(args, "max_code_projects", 3)),
            timeout_seconds=int(getattr(args, "timeout_seconds", 120)),
            headless=bool(getattr(args, "headless", False)),
        )
    elif args.portfolio_final_acceptance_command == "report":
        payload = service.report()
    else:
        payload = service.read()
    print(json.dumps(public_final_acceptance_payload(payload), ensure_ascii=False, indent=2))
    return 0
