"""Persistence helpers for V2.91-V2.95 real acceptance closure artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir
from .shared import artifact_uri


def stage_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "real_acceptance_closure"


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


def runtime_restore_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "runtime_diagnosis", "artifact_ref": artifact_uri(codebase_id, "runtime_restore", "runtime_diagnosis.json")},
        {"type": "restore_checklist", "artifact_ref": artifact_uri(codebase_id, "runtime_restore", "restore_checklist.md")},
        {"type": "focused_regression_result", "artifact_ref": artifact_uri(codebase_id, "runtime_restore", "focused_regression_result.json")},
    ]


def route_a_closure_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "material_manifest", "artifact_ref": artifact_uri(codebase_id, "route_a_closure", "material_manifest.json")},
        {"type": "redaction_decision", "artifact_ref": artifact_uri(codebase_id, "route_a_closure", "redaction_decision.json")},
        {"type": "manual_acceptance_record", "artifact_ref": artifact_uri(codebase_id, "route_a_closure", "manual_acceptance_record.md")},
    ]


def quality_decision_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "human_decisions", "artifact_ref": artifact_uri(codebase_id, "quality_decision", "human_decisions.jsonl")},
        {"type": "rule_effect_closure", "artifact_ref": artifact_uri(codebase_id, "quality_decision", "rule_effect_closure.json")},
        {"type": "quality_closure_report", "artifact_ref": artifact_uri(codebase_id, "quality_decision", "quality_closure_report.md")},
    ]


def external_project_closure_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "path_binding_decision", "artifact_ref": artifact_uri(codebase_id, "external_project_closure", "path_binding_decision.json")},
        {"type": "e2e_result_matrix", "artifact_ref": artifact_uri(codebase_id, "external_project_closure", "e2e_result_matrix.json")},
        {"type": "unavailable_decisions", "artifact_ref": artifact_uri(codebase_id, "external_project_closure", "unavailable_decisions.md")},
    ]


def release_finalizer_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "final_gate_summary", "artifact_ref": artifact_uri(codebase_id, "release_finalizer", "final_gate_summary.json")},
        {"type": "final_release_report", "artifact_ref": artifact_uri(codebase_id, "release_finalizer", "final_release_report.md")},
        {"type": "false_green_audit", "artifact_ref": artifact_uri(codebase_id, "release_finalizer", "false_green_audit.md")},
    ]


def write_runtime_restore(workspace: Path, codebase_id: str, diagnosis: dict[str, Any], checklist: str, regression: dict[str, Any]) -> None:
    write_json(_path(workspace, codebase_id, "runtime_restore", "runtime_diagnosis.json"), diagnosis)
    _write_text(_path(workspace, codebase_id, "runtime_restore", "restore_checklist.md"), checklist)
    write_json(_path(workspace, codebase_id, "runtime_restore", "focused_regression_result.json"), regression)


def read_runtime_diagnosis(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "runtime_restore", "runtime_diagnosis.json"), "RUNTIME_RESTORE_NOT_BUILT")


def read_restore_checklist(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "runtime_restore", "restore_checklist.md"), "RUNTIME_RESTORE_NOT_BUILT")


def read_focused_regression_result(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "runtime_restore", "focused_regression_result.json"), "RUNTIME_RESTORE_NOT_BUILT")


def write_route_a_closure(workspace: Path, codebase_id: str, manifest: dict[str, Any], redaction: dict[str, Any], record: str) -> None:
    write_json(_path(workspace, codebase_id, "route_a_closure", "material_manifest.json"), manifest)
    write_json(_path(workspace, codebase_id, "route_a_closure", "redaction_decision.json"), redaction)
    _write_text(_path(workspace, codebase_id, "route_a_closure", "manual_acceptance_record.md"), record)


def read_material_manifest(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "route_a_closure", "material_manifest.json"), "ROUTE_A_CLOSURE_NOT_BUILT")


def read_redaction_decision(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "route_a_closure", "redaction_decision.json"), "ROUTE_A_CLOSURE_NOT_BUILT")


def read_manual_acceptance_record(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "route_a_closure", "manual_acceptance_record.md"), "ROUTE_A_CLOSURE_NOT_BUILT")


def write_quality_decision(workspace: Path, codebase_id: str, history: str, closure: dict[str, Any], report: str) -> None:
    _write_text(_path(workspace, codebase_id, "quality_decision", "human_decisions.jsonl"), history)
    write_json(_path(workspace, codebase_id, "quality_decision", "rule_effect_closure.json"), closure)
    _write_text(_path(workspace, codebase_id, "quality_decision", "quality_closure_report.md"), report)


def read_human_decisions(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "quality_decision", "human_decisions.jsonl"), "QUALITY_DECISION_NOT_BUILT")


def read_rule_effect_closure(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "quality_decision", "rule_effect_closure.json"), "QUALITY_DECISION_NOT_BUILT")


def read_quality_closure_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "quality_decision", "quality_closure_report.md"), "QUALITY_DECISION_NOT_BUILT")


def write_external_project_closure(workspace: Path, codebase_id: str, binding: dict[str, Any], matrix: dict[str, Any], decisions: str) -> None:
    write_json(_path(workspace, codebase_id, "external_project_closure", "path_binding_decision.json"), binding)
    write_json(_path(workspace, codebase_id, "external_project_closure", "e2e_result_matrix.json"), matrix)
    _write_text(_path(workspace, codebase_id, "external_project_closure", "unavailable_decisions.md"), decisions)


def read_path_binding_decision(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "external_project_closure", "path_binding_decision.json"), "EXTERNAL_PROJECT_CLOSURE_NOT_BUILT")


def read_e2e_result_matrix(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "external_project_closure", "e2e_result_matrix.json"), "EXTERNAL_PROJECT_CLOSURE_NOT_BUILT")


def read_unavailable_decisions(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "external_project_closure", "unavailable_decisions.md"), "EXTERNAL_PROJECT_CLOSURE_NOT_BUILT")


def write_release_finalizer(workspace: Path, codebase_id: str, summary: dict[str, Any], report: str, false_green: str) -> None:
    write_json(_path(workspace, codebase_id, "release_finalizer", "final_gate_summary.json"), summary)
    _write_text(_path(workspace, codebase_id, "release_finalizer", "final_release_report.md"), report)
    _write_text(_path(workspace, codebase_id, "release_finalizer", "false_green_audit.md"), false_green)


def read_final_gate_summary(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "release_finalizer", "final_gate_summary.json"), "RELEASE_FINALIZER_NOT_BUILT")


def read_final_release_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "release_finalizer", "final_release_report.md"), "RELEASE_FINALIZER_NOT_BUILT")


def read_false_green_audit(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "release_finalizer", "false_green_audit.md"), "RELEASE_FINALIZER_NOT_BUILT")
