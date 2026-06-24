"""CLI subcommands for V2.54-V2.58 Human / Agent Deepening."""

from __future__ import annotations

import argparse


HUMAN_AGENT_DEEPENING_COMMAND_TO_TOOL = {
    "portal-build": "knowledge_code_human_agent_deepening_portal_build",
    "portal": "knowledge_code_human_agent_deepening_portal_read",
    "task-workflow-build": "knowledge_code_human_agent_deepening_task_workflow_build",
    "task-workflow": "knowledge_code_human_agent_deepening_task_workflow_read",
    "evidence-loop-build": "knowledge_code_human_agent_deepening_evidence_loop_build",
    "evidence-loop": "knowledge_code_human_agent_deepening_evidence_loop_read",
    "regression-build": "knowledge_code_human_agent_deepening_regression_build",
    "regression": "knowledge_code_human_agent_deepening_regression_read",
    "restore-build": "knowledge_code_human_agent_deepening_restore_build",
    "restore": "knowledge_code_human_agent_deepening_restore_read",
}


def add_human_agent_deepening_parser(code_subparsers: argparse._SubParsersAction) -> None:
    parser = code_subparsers.add_parser("human-agent-deepening", help="Build and read V2.54-V2.58 Human / Agent Deepening artifacts")
    subparsers = parser.add_subparsers(dest="code_human_agent_deepening_command", required=True)
    for name, help_text in {
        "portal-build": "Build V2.54 Human Portal Deepening artifacts",
        "portal": "Read V2.54 Human Portal Deepening artifacts",
        "task-workflow-build": "Build V2.55 Agent Task Workflow artifacts",
        "task-workflow": "Read V2.55 Agent Task Workflow artifacts",
        "evidence-loop-build": "Build V2.56 Doc-Code Governance Evidence Loop artifacts",
        "evidence-loop": "Read V2.56 Doc-Code Governance Evidence Loop artifacts",
        "regression-build": "Build V2.57 Multi-project Regression Expansion artifacts",
        "regression": "Read V2.57 Multi-project Regression Expansion artifacts",
        "restore-build": "Build V2.58 Developer Onboarding Restore UX artifacts",
        "restore": "Read V2.58 Developer Onboarding Restore UX artifacts",
    }.items():
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        command.add_argument("--workspace-id", required=True)
        command.add_argument("--codebase-id", required=True)
        if name == "task-workflow-build":
            command.add_argument("--task", required=True)
            command.add_argument("--max-tokens", type=int, default=4000)
        if name == "task-workflow":
            command.add_argument("--task-id", required=True)
        if name == "regression-build":
            command.add_argument("--project", action="append", default=[], help="Project spec as name=path; may be repeated")


def human_agent_deepening_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    command = args.code_human_agent_deepening_command
    payload = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command == "task-workflow-build":
        payload["task"] = args.task
        payload["max_tokens"] = args.max_tokens
    if command == "task-workflow":
        payload["task_id"] = args.task_id
    if command == "regression-build":
        projects = []
        for item in args.project or []:
            if "=" in item:
                name, path = item.split("=", 1)
                projects.append({"name": name, "path": path})
        payload["projects"] = projects
    return HUMAN_AGENT_DEEPENING_COMMAND_TO_TOOL[command], payload
