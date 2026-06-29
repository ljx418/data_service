"""CLI subcommands for V2.71-V2.75 agent memory release stage."""

from __future__ import annotations

import argparse
import json


AGENT_MEMORY_RELEASE_COMMAND_TO_TOOL = {
    "external-closure-build": "knowledge_code_agent_memory_release_external_closure_build",
    "external-closure-read": "knowledge_code_agent_memory_release_external_closure_read",
    "ci-governance-build": "knowledge_code_agent_memory_release_ci_governance_build",
    "ci-governance-read": "knowledge_code_agent_memory_release_ci_governance_read",
    "memory-build": "knowledge_code_agent_memory_release_memory_build",
    "memory-read": "knowledge_code_agent_memory_release_memory_read",
    "console-build": "knowledge_code_agent_memory_release_console_build",
    "console-read": "knowledge_code_agent_memory_release_console_read",
    "release-restore-build": "knowledge_code_agent_memory_release_release_restore_build",
    "release-restore-read": "knowledge_code_agent_memory_release_release_restore_read",
}


def add_agent_memory_release_parser(code_subparsers: argparse._SubParsersAction) -> None:
    parser = code_subparsers.add_parser("agent-memory-release", help="Build and read V2.71-V2.75 agent memory release artifacts")
    subparsers = parser.add_subparsers(dest="code_agent_memory_release_command", required=True)
    for name in AGENT_MEMORY_RELEASE_COMMAND_TO_TOOL:
        command = subparsers.add_parser(name)
        command.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        command.add_argument("--workspace-id", required=True)
        command.add_argument("--codebase-id", required=True)
        if name == "external-closure-build":
            command.add_argument("--project", action="append", default=[], help="Project spec as name=path; may be repeated")
        if name == "ci-governance-build":
            command.add_argument("--command-results-json", default="{}", help="Optional command result summary JSON")


def agent_memory_release_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    command = args.code_agent_memory_release_command
    payload: dict = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command == "external-closure-build":
        projects = []
        for item in args.project or []:
            if "=" in item:
                name, path = item.split("=", 1)
                projects.append({"name": name, "path": path})
        payload["projects"] = projects
    if command == "ci-governance-build":
        results = json.loads(args.command_results_json or "{}")
        if not isinstance(results, dict):
            raise ValueError("command-results-json must be a JSON object")
        payload["command_results"] = results
    return AGENT_MEMORY_RELEASE_COMMAND_TO_TOOL[command], payload

