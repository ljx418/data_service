"""CLI subcommands for V2.63-V2.70 external E2E portal delivery stage."""

from __future__ import annotations

import argparse


EXTERNAL_E2E_PORTAL_DELIVERY_COMMAND_TO_TOOL = {
    "e2e-build": "knowledge_code_external_e2e_portal_delivery_e2e_build",
    "e2e-read": "knowledge_code_external_e2e_portal_delivery_e2e_read",
    "portal-build": "knowledge_code_external_e2e_portal_delivery_portal_build",
    "portal-read": "knowledge_code_external_e2e_portal_delivery_portal_read",
    "delivery-build": "knowledge_code_external_e2e_portal_delivery_delivery_build",
    "delivery-read": "knowledge_code_external_e2e_portal_delivery_delivery_read",
    "contract-build": "knowledge_code_external_e2e_portal_delivery_contract_build",
    "contract-read": "knowledge_code_external_e2e_portal_delivery_contract_read",
    "path-binding-build": "knowledge_code_external_e2e_portal_delivery_path_binding_build",
    "path-binding-read": "knowledge_code_external_e2e_portal_delivery_path_binding_read",
    "worktree-delivery-build": "knowledge_code_external_e2e_portal_delivery_worktree_delivery_build",
    "worktree-delivery-read": "knowledge_code_external_e2e_portal_delivery_worktree_delivery_read",
    "surface-baseline-build": "knowledge_code_external_e2e_portal_delivery_surface_baseline_build",
    "surface-baseline-read": "knowledge_code_external_e2e_portal_delivery_surface_baseline_read",
    "dashboard-build": "knowledge_code_external_e2e_portal_delivery_dashboard_build",
    "dashboard-read": "knowledge_code_external_e2e_portal_delivery_dashboard_read",
}


def add_external_e2e_portal_delivery_parser(code_subparsers: argparse._SubParsersAction) -> None:
    parser = code_subparsers.add_parser("external-e2e-portal-delivery", help="Build and read V2.63-V2.70 external E2E portal delivery artifacts")
    subparsers = parser.add_subparsers(dest="code_external_e2e_portal_delivery_command", required=True)
    for name in EXTERNAL_E2E_PORTAL_DELIVERY_COMMAND_TO_TOOL:
        command = subparsers.add_parser(name)
        command.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        command.add_argument("--workspace-id", required=True)
        command.add_argument("--codebase-id", required=True)
        if name == "e2e-build":
            command.add_argument("--project", action="append", default=[], help="Project spec as name=path; may be repeated")
        if name == "delivery-build":
            command.add_argument("--repo-root")
        if name == "path-binding-build":
            command.add_argument("--project", action="append", default=[], help="Project spec as name=path; may be repeated")
            command.add_argument("--search-root", action="append", default=[], help="Directory containing external project repos; may be repeated")
        if name == "worktree-delivery-build":
            command.add_argument("--repo-root")
        if name == "surface-baseline-build":
            command.add_argument("--baseline-label", default="v2.67-70")


def external_e2e_portal_delivery_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    command = args.code_external_e2e_portal_delivery_command
    payload = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command == "e2e-build":
        projects = []
        for item in args.project or []:
            if "=" in item:
                name, path = item.split("=", 1)
                projects.append({"name": name, "path": path})
        payload["projects"] = projects
    if command == "delivery-build":
        payload["repo_root"] = args.repo_root
    if command == "path-binding-build":
        projects = []
        for item in args.project or []:
            if "=" in item:
                name, path = item.split("=", 1)
                projects.append({"name": name, "path": path})
        payload["projects"] = projects
        payload["search_roots"] = list(args.search_root or [])
    if command == "worktree-delivery-build":
        payload["repo_root"] = args.repo_root
    if command == "surface-baseline-build":
        payload["baseline_label"] = args.baseline_label
    return EXTERNAL_E2E_PORTAL_DELIVERY_COMMAND_TO_TOOL[command], payload
