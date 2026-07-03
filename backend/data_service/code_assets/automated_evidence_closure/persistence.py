"""Persistence helpers for V2.96-V2.100 automated evidence closure artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir
from .shared import artifact_uri


def stage_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "automated_evidence_closure"


def _path(workspace: Path, codebase_id: str, section: str, filename: str) -> Path:
    return stage_dir(workspace, codebase_id) / section / filename


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


def cli_gap_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [{"type": "cli_surface_result", "artifact_ref": artifact_uri(codebase_id, "cli_gap_closure", "cli_surface_result.json")}]


def route_a_evidence_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "material_scan", "artifact_ref": artifact_uri(codebase_id, "route_a_evidence", "material_scan.json")},
        {"type": "redaction_audit", "artifact_ref": artifact_uri(codebase_id, "route_a_evidence", "redaction_audit.json")},
        {"type": "evidence_capture_manifest", "artifact_ref": artifact_uri(codebase_id, "route_a_evidence", "evidence_capture_manifest.json")},
        {"type": "manual_confirmation_queue", "artifact_ref": artifact_uri(codebase_id, "route_a_evidence", "manual_confirmation_queue.md")},
    ]


def quality_workbench_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "risk_queue", "artifact_ref": artifact_uri(codebase_id, "quality_workbench", "risk_queue.json")},
        {"type": "decision_recommendations", "artifact_ref": artifact_uri(codebase_id, "quality_workbench", "decision_recommendations.json")},
        {"type": "human_decision_backlog", "artifact_ref": artifact_uri(codebase_id, "quality_workbench", "human_decision_backlog.md")},
    ]


def external_path_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "project_paths", "artifact_ref": artifact_uri(codebase_id, "external_path_registry", "project_paths.json")},
        {"type": "project_smoke_matrix", "artifact_ref": artifact_uri(codebase_id, "external_path_registry", "project_smoke_matrix.json")},
        {"type": "unavailable_resolution", "artifact_ref": artifact_uri(codebase_id, "external_path_registry", "unavailable_resolution.md")},
    ]


def release_gate_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "evidence_summary", "artifact_ref": artifact_uri(codebase_id, "release_evidence_gate", "evidence_summary.json")},
        {"type": "final_release_gate", "artifact_ref": artifact_uri(codebase_id, "release_evidence_gate", "final_release_gate.md")},
        {"type": "false_green_recheck", "artifact_ref": artifact_uri(codebase_id, "release_evidence_gate", "false_green_recheck.md")},
    ]


def write_cli_gap(workspace: Path, codebase_id: str, result: dict[str, Any]) -> None:
    write_json(_path(workspace, codebase_id, "cli_gap_closure", "cli_surface_result.json"), result)


def read_cli_gap(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "cli_gap_closure", "cli_surface_result.json"), "CLI_GAP_NOT_BUILT")


def write_route_a_evidence(workspace: Path, codebase_id: str, scan: dict[str, Any], redaction: dict[str, Any], capture: dict[str, Any], queue: str) -> None:
    write_json(_path(workspace, codebase_id, "route_a_evidence", "material_scan.json"), scan)
    write_json(_path(workspace, codebase_id, "route_a_evidence", "redaction_audit.json"), redaction)
    write_json(_path(workspace, codebase_id, "route_a_evidence", "evidence_capture_manifest.json"), capture)
    _write_text(_path(workspace, codebase_id, "route_a_evidence", "manual_confirmation_queue.md"), queue)


def read_material_scan(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "route_a_evidence", "material_scan.json"), "ROUTE_A_EVIDENCE_NOT_BUILT")


def read_redaction_audit(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "route_a_evidence", "redaction_audit.json"), "ROUTE_A_EVIDENCE_NOT_BUILT")


def read_evidence_capture_manifest(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "route_a_evidence", "evidence_capture_manifest.json"), "ROUTE_A_EVIDENCE_NOT_BUILT")


def read_manual_confirmation_queue(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "route_a_evidence", "manual_confirmation_queue.md"), "ROUTE_A_EVIDENCE_NOT_BUILT")


def write_quality_workbench(workspace: Path, codebase_id: str, risk_queue: dict[str, Any], recommendations: dict[str, Any], backlog: str) -> None:
    write_json(_path(workspace, codebase_id, "quality_workbench", "risk_queue.json"), risk_queue)
    write_json(_path(workspace, codebase_id, "quality_workbench", "decision_recommendations.json"), recommendations)
    _write_text(_path(workspace, codebase_id, "quality_workbench", "human_decision_backlog.md"), backlog)


def read_risk_queue(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "quality_workbench", "risk_queue.json"), "QUALITY_WORKBENCH_NOT_BUILT")


def read_decision_recommendations(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "quality_workbench", "decision_recommendations.json"), "QUALITY_WORKBENCH_NOT_BUILT")


def read_human_decision_backlog(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "quality_workbench", "human_decision_backlog.md"), "QUALITY_WORKBENCH_NOT_BUILT")


def write_external_path(workspace: Path, codebase_id: str, paths: dict[str, Any], matrix: dict[str, Any], resolution: str) -> None:
    write_json(_path(workspace, codebase_id, "external_path_registry", "project_paths.json"), paths)
    write_json(_path(workspace, codebase_id, "external_path_registry", "project_smoke_matrix.json"), matrix)
    _write_text(_path(workspace, codebase_id, "external_path_registry", "unavailable_resolution.md"), resolution)


def read_project_paths(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "external_path_registry", "project_paths.json"), "EXTERNAL_PATH_NOT_BUILT")


def read_project_smoke_matrix(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "external_path_registry", "project_smoke_matrix.json"), "EXTERNAL_PATH_NOT_BUILT")


def read_unavailable_resolution(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "external_path_registry", "unavailable_resolution.md"), "EXTERNAL_PATH_NOT_BUILT")


def write_release_gate(workspace: Path, codebase_id: str, summary: dict[str, Any], gate: str, false_green: str) -> None:
    write_json(_path(workspace, codebase_id, "release_evidence_gate", "evidence_summary.json"), summary)
    _write_text(_path(workspace, codebase_id, "release_evidence_gate", "final_release_gate.md"), gate)
    _write_text(_path(workspace, codebase_id, "release_evidence_gate", "false_green_recheck.md"), false_green)


def read_evidence_summary(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "release_evidence_gate", "evidence_summary.json"), "RELEASE_GATE_NOT_BUILT")


def read_final_release_gate(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "release_evidence_gate", "final_release_gate.md"), "RELEASE_GATE_NOT_BUILT")


def read_false_green_recheck(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "release_evidence_gate", "false_green_recheck.md"), "RELEASE_GATE_NOT_BUILT")
