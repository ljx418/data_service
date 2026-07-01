"""CLI subcommands for V2.86-V2.90 full corpus release hardening."""

from __future__ import annotations

import argparse
import json


REAL_DOCUMENT_FULL_CORPUS_RELEASE_COMMAND_TO_TOOL = {
    "full-corpus-build": "knowledge_code_real_document_full_corpus_release_full_corpus_build",
    "full-corpus-read": "knowledge_code_real_document_full_corpus_release_full_corpus_read",
    "route-a-build": "knowledge_code_real_document_full_corpus_release_route_a_build",
    "route-a-read": "knowledge_code_real_document_full_corpus_release_route_a_read",
    "quality-review-build": "knowledge_code_real_document_full_corpus_release_quality_review_build",
    "quality-review-read": "knowledge_code_real_document_full_corpus_release_quality_review_read",
    "external-project-build": "knowledge_code_real_document_full_corpus_release_external_project_build",
    "external-project-read": "knowledge_code_real_document_full_corpus_release_external_project_read",
    "release-gate-build": "knowledge_code_real_document_full_corpus_release_release_gate_build",
    "release-gate-read": "knowledge_code_real_document_full_corpus_release_release_gate_read",
}


def add_real_document_full_corpus_release_parser(code_subparsers: argparse._SubParsersAction) -> None:
    parser = code_subparsers.add_parser("real-document-full-corpus-release", help="Build and read V2.86-V2.90 full corpus release artifacts")
    subparsers = parser.add_subparsers(dest="code_real_document_full_corpus_release_command", required=True)
    for name in REAL_DOCUMENT_FULL_CORPUS_RELEASE_COMMAND_TO_TOOL:
        command = subparsers.add_parser(name)
        command.add_argument("--workspace-root", help="Managed workspace root; overrides DATA_SERVICE_WORKSPACE_ROOT for this command")
        command.add_argument("--workspace-id", required=True)
        command.add_argument("--codebase-id", required=True)
        if name == "full-corpus-build":
            command.add_argument("--options-json", default="{}", help="Optional full corpus options JSON")
        if name == "route-a-build":
            command.add_argument("--acceptance-state-json", default="{}", help="Optional Route A acceptance state JSON")
        if name == "quality-review-build":
            command.add_argument("--review-state-json", default="{}", help="Optional quality review state JSON")
        if name == "external-project-build":
            command.add_argument("--project-paths-json", default="{}", help="Optional external project paths JSON")
        if name == "release-gate-build":
            command.add_argument("--gate-state-json", default="{}", help="Optional release gate state JSON")


def real_document_full_corpus_release_tool_payload(args: argparse.Namespace) -> tuple[str, dict]:
    command = args.code_real_document_full_corpus_release_command
    payload: dict = {"workspace_id": args.workspace_id, "codebase_id": args.codebase_id}
    if command == "full-corpus-build":
        payload["options"] = _object(args.options_json, "options-json")
    if command == "route-a-build":
        payload["acceptance_state"] = _object(args.acceptance_state_json, "acceptance-state-json")
    if command == "quality-review-build":
        payload["review_state"] = _object(args.review_state_json, "review-state-json")
    if command == "external-project-build":
        payload["project_paths"] = _object(args.project_paths_json, "project-paths-json")
    if command == "release-gate-build":
        payload["gate_state"] = _object(args.gate_state_json, "gate-state-json")
    return REAL_DOCUMENT_FULL_CORPUS_RELEASE_COMMAND_TO_TOOL[command], payload


def _object(raw: str, label: str) -> dict:
    parsed = json.loads(raw or "{}")
    if not isinstance(parsed, dict):
        raise ValueError(f"{label} must be a JSON object")
    return parsed
