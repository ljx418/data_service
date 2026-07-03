"""CLI subcommands for V2.96-V2.100 automated evidence closure."""

from __future__ import annotations

import argparse
import json


AUTOMATED_EVIDENCE_CLOSURE_COMMAND_TO_TOOL = {
    "cli-gap-build": "knowledge_code_automated_evidence_closure_cli_gap_build",
    "cli-gap-read": "knowledge_code_automated_evidence_closure_cli_gap_read",
    "route-a-evidence-build": "knowledge_code_automated_evidence_closure_route_a_evidence_build",
    "route-a-evidence-read": "knowledge_code_automated_evidence_closure_route_a_evidence_read",
    "quality-workbench-build": "knowledge_code_automated_evidence_closure_quality_workbench_build",
    "quality-workbench-read": "knowledge_code_automated_evidence_closure_quality_workbench_read",
    "external-path-build": "knowledge_code_automated_evidence_closure_external_path_build",
    "external-path-read": "knowledge_code_automated_evidence_closure_external_path_read",
    "release-gate-build": "knowledge_code_automated_evidence_closure_release_gate_build",
    "release-gate-read": "knowledge_code_automated_evidence_closure_release_gate_read",
}


def add_automated_evidence_closure_parser(code_subparsers: argparse._SubParsersAction) -> None:
    parser = code_subparsers.add_parser("automated-evidence-closure", help="Build and read V2.96-V2.100 automated evidence closure artifacts")
    subparsers = parser.add_subparsers(dest="code_automated_evidence_closure_command", required=True)
    for name in AUTOMATED_EVIDENCE_CLOSURE_COMMAND_TO_TOOL:
        command = subparsers.add_parser(name)
        command.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        command.add_argument("--workspace-id", required=True)
        command.add_argument("--codebase-id", required=True)
        if name == "cli-gap-build":
            command.add_argument("--cli-state-json", default="{}", help="Optional CLI gap state JSON")
        if name == "route-a-evidence-build":
            command.add_argument("--material-state-json", default="{}", help="Optional Route A material state JSON")
        if name == "quality-workbench-build":
            command.add_argument("--decision-state-json", default="{}", help="Optional quality decision state JSON")
        if name == "external-path-build":
            command.add_argument("--project-state-json", default="{}", help="Optional external project state JSON")
        if name == "release-gate-build":
            command.add_argument("--gate-state-json", default="{}", help="Optional release gate state JSON")


def automated_evidence_closure_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    command = args.code_automated_evidence_closure_command
    payload: dict = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command == "cli-gap-build":
        payload["cli_state"] = _object(args.cli_state_json, "cli-state-json")
    if command == "route-a-evidence-build":
        payload["material_state"] = _object(args.material_state_json, "material-state-json")
    if command == "quality-workbench-build":
        payload["decision_state"] = _object(args.decision_state_json, "decision-state-json")
    if command == "external-path-build":
        payload["project_state"] = _object(args.project_state_json, "project-state-json")
    if command == "release-gate-build":
        payload["gate_state"] = _object(args.gate_state_json, "gate-state-json")
    return AUTOMATED_EVIDENCE_CLOSURE_COMMAND_TO_TOOL[command], payload


def _object(raw: str, label: str) -> dict:
    parsed = json.loads(raw or "{}")
    if not isinstance(parsed, dict):
        raise ValueError(f"{label} must be a JSON object")
    return parsed

