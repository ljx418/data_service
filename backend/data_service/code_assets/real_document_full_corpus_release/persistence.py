"""Persistence helpers for V2.86-V2.90 full corpus release hardening artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir
from .shared import artifact_uri


def stage_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "real_document_full_corpus_release"


def section_dir(workspace: Path, codebase_id: str, section: str) -> Path:
    return stage_dir(workspace, codebase_id) / section


def _path(workspace: Path, codebase_id: str, section: str, filename: str) -> Path:
    return section_dir(workspace, codebase_id, section) / filename


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _read_json_required(path: Path, code: str) -> dict[str, Any]:
    payload = read_json(path, None)
    if not payload:
        raise FileNotFoundError(code)
    return payload


def _read_text_required(path: Path, code: str) -> str:
    if not path.exists():
        raise FileNotFoundError(code)
    return path.read_text(encoding="utf-8")


def full_corpus_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "full_corpus_run", "artifact_ref": artifact_uri(codebase_id, "full_corpus_e2e", "full_corpus_run.json")},
        {"type": "parser_failures", "artifact_ref": artifact_uri(codebase_id, "full_corpus_e2e", "parser_failures.json")},
        {"type": "full_corpus_report", "artifact_ref": artifact_uri(codebase_id, "full_corpus_e2e", "full_corpus_report.md")},
    ]


def route_a_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "sample_pack_contract", "artifact_ref": artifact_uri(codebase_id, "route_a_acceptance", "sample_pack_contract.json")},
        {"type": "redaction_review", "artifact_ref": artifact_uri(codebase_id, "route_a_acceptance", "redaction_review.json")},
        {"type": "manual_acceptance_record", "artifact_ref": artifact_uri(codebase_id, "route_a_acceptance", "manual_acceptance_record.md")},
    ]


def quality_review_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "human_quality_review", "artifact_ref": artifact_uri(codebase_id, "quality_review", "human_quality_review.json")},
        {"type": "correction_decision_history", "artifact_ref": artifact_uri(codebase_id, "quality_review", "correction_decision_history.jsonl")},
        {"type": "rule_effect_review", "artifact_ref": artifact_uri(codebase_id, "quality_review", "rule_effect_review.md")},
    ]


def external_project_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "path_manifest", "artifact_ref": artifact_uri(codebase_id, "external_project_closure", "path_manifest.json")},
        {"type": "project_e2e_records", "artifact_ref": artifact_uri(codebase_id, "external_project_closure", "project_e2e_records.json")},
        {"type": "unavailable_diagnosis", "artifact_ref": artifact_uri(codebase_id, "external_project_closure", "unavailable_diagnosis.md")},
    ]


def release_gate_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "release_gate_summary", "artifact_ref": artifact_uri(codebase_id, "release_gate", "release_gate_summary.json")},
        {"type": "release_readiness_report", "artifact_ref": artifact_uri(codebase_id, "release_gate", "release_readiness_report.md")},
    ]


def write_full_corpus(workspace: Path, codebase_id: str, run: dict[str, Any], failures: dict[str, Any], report: str) -> None:
    write_json(_path(workspace, codebase_id, "full_corpus_e2e", "full_corpus_run.json"), run)
    write_json(_path(workspace, codebase_id, "full_corpus_e2e", "parser_failures.json"), failures)
    _write_text(_path(workspace, codebase_id, "full_corpus_e2e", "full_corpus_report.md"), report)


def read_full_corpus_run(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "full_corpus_e2e", "full_corpus_run.json"), "FULL_CORPUS_E2E_NOT_BUILT")


def read_parser_failures(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "full_corpus_e2e", "parser_failures.json"), "FULL_CORPUS_E2E_NOT_BUILT")


def read_full_corpus_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "full_corpus_e2e", "full_corpus_report.md"), "FULL_CORPUS_E2E_NOT_BUILT")


def write_route_a(workspace: Path, codebase_id: str, contract: dict[str, Any], redaction: dict[str, Any], record: str) -> None:
    write_json(_path(workspace, codebase_id, "route_a_acceptance", "sample_pack_contract.json"), contract)
    write_json(_path(workspace, codebase_id, "route_a_acceptance", "redaction_review.json"), redaction)
    _write_text(_path(workspace, codebase_id, "route_a_acceptance", "manual_acceptance_record.md"), record)


def read_route_a_contract(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "route_a_acceptance", "sample_pack_contract.json"), "ROUTE_A_ACCEPTANCE_NOT_BUILT")


def read_route_a_redaction(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "route_a_acceptance", "redaction_review.json"), "ROUTE_A_ACCEPTANCE_NOT_BUILT")


def read_route_a_record(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "route_a_acceptance", "manual_acceptance_record.md"), "ROUTE_A_ACCEPTANCE_NOT_BUILT")


def write_quality_review(workspace: Path, codebase_id: str, review: dict[str, Any], history: str, report: str) -> None:
    write_json(_path(workspace, codebase_id, "quality_review", "human_quality_review.json"), review)
    _write_text(_path(workspace, codebase_id, "quality_review", "correction_decision_history.jsonl"), history)
    _write_text(_path(workspace, codebase_id, "quality_review", "rule_effect_review.md"), report)


def read_human_quality_review(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "quality_review", "human_quality_review.json"), "QUALITY_REVIEW_NOT_BUILT")


def read_correction_decision_history(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "quality_review", "correction_decision_history.jsonl"), "QUALITY_REVIEW_NOT_BUILT")


def read_rule_effect_review(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "quality_review", "rule_effect_review.md"), "QUALITY_REVIEW_NOT_BUILT")


def write_external_project(workspace: Path, codebase_id: str, manifest: dict[str, Any], records: dict[str, Any], diagnosis: str) -> None:
    write_json(_path(workspace, codebase_id, "external_project_closure", "path_manifest.json"), manifest)
    write_json(_path(workspace, codebase_id, "external_project_closure", "project_e2e_records.json"), records)
    _write_text(_path(workspace, codebase_id, "external_project_closure", "unavailable_diagnosis.md"), diagnosis)


def read_path_manifest(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "external_project_closure", "path_manifest.json"), "EXTERNAL_PROJECT_CLOSURE_NOT_BUILT")


def read_project_e2e_records(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "external_project_closure", "project_e2e_records.json"), "EXTERNAL_PROJECT_CLOSURE_NOT_BUILT")


def read_unavailable_diagnosis(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "external_project_closure", "unavailable_diagnosis.md"), "EXTERNAL_PROJECT_CLOSURE_NOT_BUILT")


def write_release_gate(workspace: Path, codebase_id: str, summary: dict[str, Any], report: str) -> None:
    write_json(_path(workspace, codebase_id, "release_gate", "release_gate_summary.json"), summary)
    _write_text(_path(workspace, codebase_id, "release_gate", "release_readiness_report.md"), report)


def read_release_gate_summary(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "release_gate", "release_gate_summary.json"), "RELEASE_GATE_NOT_BUILT")


def read_release_readiness_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "release_gate", "release_readiness_report.md"), "RELEASE_GATE_NOT_BUILT")
