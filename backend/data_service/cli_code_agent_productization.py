"""CLI subcommands for V2.46 Agent Productization."""

from __future__ import annotations

import argparse


def add_agent_productization_parser(code_subparsers: argparse._SubParsersAction) -> None:
    agent = code_subparsers.add_parser("agent-productization", help="Build and read V2.46 Agent Productization artifacts")
    subparsers = agent.add_subparsers(dest="code_agent_productization_command", required=True)
    for name, help_text in {
        "mcp-build": "Build Codex/Agent MCP usage guide and workflows",
        "mcp": "Read Codex/Agent MCP usage guide and workflows",
        "profile-build": "Build project profile onboarding draft and no-hardcode audit",
        "profile": "Read project profile onboarding draft and no-hardcode audit",
        "portal-build": "Build human-readable architecture portal HTML and chart",
        "portal": "Read human-readable architecture portal HTML and chart",
    }.items():
        parser = subparsers.add_parser(name, help=help_text)
        parser.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        parser.add_argument("--workspace-id", required=True)
        parser.add_argument("--codebase-id", required=True)
    task_build = subparsers.add_parser("task-build", help="Build task reading order, impact candidates, and suggested tests")
    task_build.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    task_build.add_argument("--workspace-id", required=True)
    task_build.add_argument("--codebase-id", required=True)
    task_build.add_argument("--task", required=True)
    task_read = subparsers.add_parser("task", help="Read task reading order, impact candidates, and suggested tests")
    task_read.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    task_read.add_argument("--workspace-id", required=True)
    task_read.add_argument("--codebase-id", required=True)
    task_read.add_argument("--task-id", required=True)
    feedback = subparsers.add_parser("governance-feedback", help="Record governance feedback for Agent Productization artifacts")
    feedback.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    feedback.add_argument("--workspace-id", required=True)
    feedback.add_argument("--codebase-id", required=True)
    feedback.add_argument("--target-type", required=True)
    feedback.add_argument("--target-id", required=True)
    feedback.add_argument("--action", required=True)
    feedback.add_argument("--rule-type", default="read_time_overlay")
    feedback.add_argument("--severity", default="medium")
    feedback.add_argument("--reason", default="")
    feedback.add_argument("--suggested-value", default="")
    rules = subparsers.add_parser("governance-rules-build", help="Build governance rules from feedback")
    rules.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    rules.add_argument("--workspace-id", required=True)
    rules.add_argument("--codebase-id", required=True)
    review = subparsers.add_parser("governance-rule-review", help="Approve, reject, or revoke a governance rule")
    review.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    review.add_argument("--workspace-id", required=True)
    review.add_argument("--codebase-id", required=True)
    review.add_argument("--rule-id", required=True)
    review.add_argument("--status", required=True)
    review.add_argument("--reviewer", default="")
    review.add_argument("--note", default="")
    overlay = subparsers.add_parser("governance-overlay", help="Read governance read-time overlay")
    overlay.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    overlay.add_argument("--workspace-id", required=True)
    overlay.add_argument("--codebase-id", required=True)
    playbook_build = subparsers.add_parser("playbook-build", help="Build role-scoped Agent Context Playbooks")
    playbook_build.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    playbook_build.add_argument("--workspace-id", required=True)
    playbook_build.add_argument("--codebase-id", required=True)
    playbook_build.add_argument("--role", default="")
    playbook_build.add_argument("--max-tokens", type=int, default=4000)
    playbook = subparsers.add_parser("playbook", help="Read a role-scoped Agent Context Playbook")
    playbook.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
    playbook.add_argument("--workspace-id", required=True)
    playbook.add_argument("--codebase-id", required=True)
    playbook.add_argument("--role", required=True)
    for name, help_text in {
        "closure-build": "Build Agent Productization continuous acceptance closure artifacts",
        "closure": "Read Agent Productization continuous acceptance closure artifacts",
    }.items():
        parser = subparsers.add_parser(name, help=help_text)
        parser.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        parser.add_argument("--workspace-id", required=True)
        parser.add_argument("--codebase-id", required=True)


def agent_productization_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    mapping = {
        "mcp-build": "knowledge_code_agent_productization_mcp_build",
        "mcp": "knowledge_code_agent_productization_mcp_read",
        "profile-build": "knowledge_code_agent_productization_profile_build",
        "profile": "knowledge_code_agent_productization_profile_read",
        "portal-build": "knowledge_code_agent_productization_portal_build",
        "portal": "knowledge_code_agent_productization_portal_read",
        "task-build": "knowledge_code_agent_productization_task_navigation_build",
        "task": "knowledge_code_agent_productization_task_navigation_read",
        "governance-feedback": "knowledge_code_agent_productization_governance_feedback",
        "governance-rules-build": "knowledge_code_agent_productization_governance_rules_build",
        "governance-rule-review": "knowledge_code_agent_productization_governance_rule_review",
        "governance-overlay": "knowledge_code_agent_productization_governance_overlay",
        "playbook-build": "knowledge_code_agent_productization_playbook_build",
        "playbook": "knowledge_code_agent_productization_playbook_read",
        "closure-build": "knowledge_code_agent_productization_closure_build",
        "closure": "knowledge_code_agent_productization_closure_read",
    }
    command = args.code_agent_productization_command
    payload = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command == "task-build":
        payload["task"] = args.task
    if command == "task":
        payload["task_id"] = args.task_id
    if command == "governance-feedback":
        payload.update(
            {
                "target_type": args.target_type,
                "target_id": args.target_id,
                "action": args.action,
                "rule_type": args.rule_type,
                "severity": args.severity,
                "reason": args.reason,
                "suggested_value": args.suggested_value,
            }
        )
    if command == "governance-rule-review":
        payload.update({"rule_id": args.rule_id, "status": args.status, "reviewer": args.reviewer, "note": args.note})
    if command == "playbook-build":
        if args.role:
            payload["role"] = args.role
        payload["max_tokens"] = args.max_tokens
    if command == "playbook":
        payload["role"] = args.role
    return mapping[command], payload
