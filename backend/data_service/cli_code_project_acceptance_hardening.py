"""CLI subcommands for V2.76-V2.80 project acceptance hardening stage."""

from __future__ import annotations

import argparse
import json


PROJECT_ACCEPTANCE_HARDENING_COMMAND_TO_TOOL = {
    "matrix-build": "knowledge_code_project_acceptance_hardening_matrix_build",
    "matrix-read": "knowledge_code_project_acceptance_hardening_matrix_read",
    "external-binding-build": "knowledge_code_project_acceptance_hardening_external_binding_build",
    "external-binding-read": "knowledge_code_project_acceptance_hardening_external_binding_read",
    "warning-reduction-build": "knowledge_code_project_acceptance_hardening_warning_reduction_build",
    "warning-reduction-read": "knowledge_code_project_acceptance_hardening_warning_reduction_read",
    "console-product-build": "knowledge_code_project_acceptance_hardening_console_product_build",
    "console-product-read": "knowledge_code_project_acceptance_hardening_console_product_read",
    "release-readiness-build": "knowledge_code_project_acceptance_hardening_release_readiness_build",
    "release-readiness-read": "knowledge_code_project_acceptance_hardening_release_readiness_read",
}


def add_project_acceptance_hardening_parser(code_subparsers: argparse._SubParsersAction) -> None:
    parser = code_subparsers.add_parser("project-acceptance-hardening", help="Build and read V2.76-V2.80 project acceptance hardening artifacts")
    subparsers = parser.add_subparsers(dest="code_project_acceptance_hardening_command", required=True)
    for name in PROJECT_ACCEPTANCE_HARDENING_COMMAND_TO_TOOL:
        command = subparsers.add_parser(name)
        command.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        command.add_argument("--workspace-id", required=True)
        command.add_argument("--codebase-id", required=True)
        if name == "external-binding-build":
            command.add_argument("--project", action="append", default=[], help="Project spec as name=path or name=path:e2e_status; may be repeated")
        if name == "warning-reduction-build":
            command.add_argument("--command-results-json", default="{}", help="Optional warning command result summary JSON")
        if name == "release-readiness-build":
            command.add_argument("--approval-state-json", default="{}", help="Optional release approval state JSON")


def project_acceptance_hardening_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    command = args.code_project_acceptance_hardening_command
    payload: dict = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command == "external-binding-build":
        payload["project_paths"] = _project_specs(args.project or [])
    if command == "warning-reduction-build":
        results = json.loads(args.command_results_json or "{}")
        if not isinstance(results, dict):
            raise ValueError("command-results-json must be a JSON object")
        payload["command_results"] = results
    if command == "release-readiness-build":
        approval = json.loads(args.approval_state_json or "{}")
        if not isinstance(approval, dict):
            raise ValueError("approval-state-json must be a JSON object")
        payload["approval_state"] = approval
    return PROJECT_ACCEPTANCE_HARDENING_COMMAND_TO_TOOL[command], payload


def _project_specs(items: list[str]) -> list[dict]:
    projects = []
    for item in items:
        if "=" not in item:
            continue
        name, value = item.split("=", 1)
        path, sep, status = value.partition(":")
        spec = {"name": name, "path": path}
        if sep:
            spec["e2e_status"] = status
        projects.append(spec)
    return projects
