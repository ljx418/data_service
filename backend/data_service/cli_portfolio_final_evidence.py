"""CLI subcommands for V2.106-V2.110 workspace portfolio final evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .mcp_workspace_runtime import WorkspaceRuntime
from .workspace_portfolio_final_evidence import WorkspacePortfolioFinalEvidenceService, public_final_evidence_payload


def add_portfolio_final_evidence_parser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("portfolio-final-evidence", help="Build and read V2.106-V2.110 portfolio final evidence artifacts")
    commands = parser.add_subparsers(dest="portfolio_final_evidence_command", required=True)
    for name in ("plan", "build", "read", "report"):
        command = commands.add_parser(name)
        command.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        command.add_argument("--workspace-id", required=True)
        if name in {"plan", "build"}:
            command.add_argument("--root", default="/mnt/c/workspace", help="Read-only workspace root to scan")
            command.add_argument("--limit", type=int, default=120, help="Maximum first-level entries to scan")
        if name == "build":
            command.add_argument("--max-code-projects", type=int, default=3, help="Maximum discovered code projects to process in one bounded run")


def run_portfolio_final_evidence_command(args: argparse.Namespace) -> int:
    root = Path(args.workspace_root).expanduser() if getattr(args, "workspace_root", None) else None
    runtime = WorkspaceRuntime((root / "_default") if root else (Path.cwd() / "workspace"), workspace_root=root)
    workspace = runtime.resolve_workspace(getattr(args, "workspace_id", None), None)
    meta = runtime.ensure_workspace_meta(workspace)
    service = WorkspacePortfolioFinalEvidenceService(workspace, workspace_id=str(meta["workspace_id"]))
    if args.portfolio_final_evidence_command == "plan":
        payload = service.plan(root=getattr(args, "root"), limit=int(getattr(args, "limit", 120)))
    elif args.portfolio_final_evidence_command == "build":
        payload = service.build(
            root=getattr(args, "root"),
            limit=int(getattr(args, "limit", 120)),
            max_code_projects=int(getattr(args, "max_code_projects", 3)),
        )
    elif args.portfolio_final_evidence_command == "report":
        payload = service.report()
    else:
        payload = service.read()
    print(json.dumps(public_final_evidence_payload(payload), ensure_ascii=False, indent=2))
    return 0
