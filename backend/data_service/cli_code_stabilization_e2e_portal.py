"""CLI subcommands for V2.59-V2.62 stabilization stage."""

from __future__ import annotations

import argparse


STABILIZATION_E2E_PORTAL_COMMAND_TO_TOOL = {
    "surface-build": "knowledge_code_stabilization_surface_build",
    "surface": "knowledge_code_stabilization_surface_read",
    "e2e-build": "knowledge_code_stabilization_e2e_build",
    "e2e": "knowledge_code_stabilization_e2e_read",
    "package-build": "knowledge_code_stabilization_package_build",
    "package": "knowledge_code_stabilization_package_read",
    "portal-build": "knowledge_code_stabilization_portal_build",
    "portal": "knowledge_code_stabilization_portal_read",
}


def add_stabilization_e2e_portal_parser(code_subparsers: argparse._SubParsersAction) -> None:
    parser = code_subparsers.add_parser("stabilization-e2e-portal", help="Build and read V2.59-V2.62 stabilization artifacts")
    subparsers = parser.add_subparsers(dest="code_stabilization_e2e_portal_command", required=True)
    for name in STABILIZATION_E2E_PORTAL_COMMAND_TO_TOOL:
        command = subparsers.add_parser(name)
        command.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        command.add_argument("--workspace-id", required=True)
        command.add_argument("--codebase-id", required=True)
        if name == "e2e-build":
            command.add_argument("--project", action="append", default=[], help="Project spec as name=path; may be repeated")
        if name == "package-build":
            command.add_argument("--repo-root")


def stabilization_e2e_portal_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    command = args.code_stabilization_e2e_portal_command
    payload = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command == "e2e-build":
        projects = []
        for item in args.project or []:
            if "=" in item:
                name, path = item.split("=", 1)
                projects.append({"name": name, "path": path})
        payload["projects"] = projects
    if command == "package-build":
        payload["repo_root"] = args.repo_root
    return STABILIZATION_E2E_PORTAL_COMMAND_TO_TOOL[command], payload
