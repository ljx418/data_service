"""CLI subcommands for V2.81-V2.85 real document acceptance stage."""

from __future__ import annotations

import argparse
import json


REAL_DOCUMENT_ACCEPTANCE_COMMAND_TO_TOOL = {
    "sample-contract-build": "knowledge_code_real_document_acceptance_sample_contract_build",
    "sample-contract-read": "knowledge_code_real_document_acceptance_sample_contract_read",
    "real-e2e-build": "knowledge_code_real_document_acceptance_real_e2e_build",
    "real-e2e-read": "knowledge_code_real_document_acceptance_real_e2e_read",
    "retrieval-trace-build": "knowledge_code_real_document_acceptance_retrieval_trace_build",
    "retrieval-trace-read": "knowledge_code_real_document_acceptance_retrieval_trace_read",
    "quality-build": "knowledge_code_real_document_acceptance_quality_build",
    "quality-read": "knowledge_code_real_document_acceptance_quality_read",
    "release-closure-build": "knowledge_code_real_document_acceptance_release_closure_build",
    "release-closure-read": "knowledge_code_real_document_acceptance_release_closure_read",
}


def add_real_document_acceptance_parser(code_subparsers: argparse._SubParsersAction) -> None:
    parser = code_subparsers.add_parser("real-document-acceptance", help="Build and read V2.81-V2.85 real document acceptance artifacts")
    subparsers = parser.add_subparsers(dest="code_real_document_acceptance_command", required=True)
    for name in REAL_DOCUMENT_ACCEPTANCE_COMMAND_TO_TOOL:
        command = subparsers.add_parser(name)
        command.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        command.add_argument("--workspace-id", required=True)
        command.add_argument("--codebase-id", required=True)
        if name == "sample-contract-build":
            command.add_argument("--sample-config-json", default="{}", help="Optional sample contract configuration JSON")
        if name == "release-closure-build":
            command.add_argument("--approval-state-json", default="{}", help="Optional release approval state JSON")


def real_document_acceptance_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    command = args.code_real_document_acceptance_command
    payload: dict = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command == "sample-contract-build":
        config = json.loads(args.sample_config_json or "{}")
        if not isinstance(config, dict):
            raise ValueError("sample-config-json must be a JSON object")
        payload["sample_config"] = config
    if command == "release-closure-build":
        approval = json.loads(args.approval_state_json or "{}")
        if not isinstance(approval, dict):
            raise ValueError("approval-state-json must be a JSON object")
        payload["approval_state"] = approval
    return REAL_DOCUMENT_ACCEPTANCE_COMMAND_TO_TOOL[command], payload
