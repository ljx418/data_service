"""CLI subcommands for V2.91-V2.95 real acceptance closure."""

from __future__ import annotations

import argparse
import json


REAL_ACCEPTANCE_CLOSURE_COMMAND_TO_TOOL = {
    "runtime-restore-build": "knowledge_code_real_acceptance_closure_runtime_restore_build",
    "runtime-restore-read": "knowledge_code_real_acceptance_closure_runtime_restore_read",
    "route-a-closure-build": "knowledge_code_real_acceptance_closure_route_a_closure_build",
    "route-a-closure-read": "knowledge_code_real_acceptance_closure_route_a_closure_read",
    "quality-decision-build": "knowledge_code_real_acceptance_closure_quality_decision_build",
    "quality-decision-read": "knowledge_code_real_acceptance_closure_quality_decision_read",
    "external-project-closure-build": "knowledge_code_real_acceptance_closure_external_project_closure_build",
    "external-project-closure-read": "knowledge_code_real_acceptance_closure_external_project_closure_read",
    "release-finalizer-build": "knowledge_code_real_acceptance_closure_release_finalizer_build",
    "release-finalizer-read": "knowledge_code_real_acceptance_closure_release_finalizer_read",
}


def add_real_acceptance_closure_parser(code_subparsers: argparse._SubParsersAction) -> None:
    parser = code_subparsers.add_parser("real-acceptance-closure", help="Build and read V2.91-V2.95 real acceptance closure artifacts")
    subparsers = parser.add_subparsers(dest="code_real_acceptance_closure_command", required=True)
    for name in REAL_ACCEPTANCE_CLOSURE_COMMAND_TO_TOOL:
        command = subparsers.add_parser(name)
        command.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        command.add_argument("--workspace-id", required=True)
        command.add_argument("--codebase-id", required=True)
        if name == "runtime-restore-build":
            command.add_argument("--runtime-state-json", default="{}", help="Optional runtime restore state JSON")
        if name == "route-a-closure-build":
            command.add_argument("--material-state-json", default="{}", help="Optional Route A material state JSON")
        if name == "quality-decision-build":
            command.add_argument("--decision-state-json", default="{}", help="Optional quality decision state JSON")
        if name == "external-project-closure-build":
            command.add_argument("--project-state-json", default="{}", help="Optional external project state JSON")
        if name == "release-finalizer-build":
            command.add_argument("--gate-state-json", default="{}", help="Optional final gate state JSON")


def real_acceptance_closure_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    command = args.code_real_acceptance_closure_command
    payload: dict = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command == "runtime-restore-build":
        payload["runtime_state"] = _object(args.runtime_state_json, "runtime-state-json")
    if command == "route-a-closure-build":
        payload["material_state"] = _object(args.material_state_json, "material-state-json")
    if command == "quality-decision-build":
        payload["decision_state"] = _object(args.decision_state_json, "decision-state-json")
    if command == "external-project-closure-build":
        payload["project_state"] = _object(args.project_state_json, "project-state-json")
    if command == "release-finalizer-build":
        payload["gate_state"] = _object(args.gate_state_json, "gate-state-json")
    return REAL_ACCEPTANCE_CLOSURE_COMMAND_TO_TOOL[command], payload


def _object(raw: str, label: str) -> dict:
    parsed = json.loads(raw or "{}")
    if not isinstance(parsed, dict):
        raise ValueError(f"{label} must be a JSON object")
    return parsed
