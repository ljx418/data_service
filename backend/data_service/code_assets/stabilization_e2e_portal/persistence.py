"""Persistence helpers for V2.59-V2.62 stabilization artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir
from .shared import artifact_uri


def stabilization_e2e_portal_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "stabilization_e2e_portal"


def stabilization_dir(workspace: Path, codebase_id: str) -> Path:
    return stabilization_e2e_portal_dir(workspace, codebase_id) / "stabilization"


def e2e_expansion_dir(workspace: Path, codebase_id: str) -> Path:
    return stabilization_e2e_portal_dir(workspace, codebase_id) / "e2e_expansion"


def packaging_dir(workspace: Path, codebase_id: str) -> Path:
    return stabilization_e2e_portal_dir(workspace, codebase_id) / "packaging"


def portal_integration_dir(workspace: Path, codebase_id: str) -> Path:
    return stabilization_e2e_portal_dir(workspace, codebase_id) / "portal_integration"


def public_surface_snapshot_path(workspace: Path, codebase_id: str) -> Path:
    return stabilization_dir(workspace, codebase_id) / "public_surface_snapshot.json"


def public_surface_parity_matrix_path(workspace: Path, codebase_id: str) -> Path:
    return stabilization_dir(workspace, codebase_id) / "public_surface_parity_matrix.json"


def public_surface_drift_report_path(workspace: Path, codebase_id: str) -> Path:
    return stabilization_dir(workspace, codebase_id) / "public_surface_drift_report.json"


def migration_notes_path(workspace: Path, codebase_id: str) -> Path:
    return stabilization_dir(workspace, codebase_id) / "migration_notes.md"


def project_e2e_matrix_path(workspace: Path, codebase_id: str) -> Path:
    return e2e_expansion_dir(workspace, codebase_id) / "project_e2e_matrix.json"


def project_failure_diagnosis_path(workspace: Path, codebase_id: str) -> Path:
    return e2e_expansion_dir(workspace, codebase_id) / "project_failure_diagnosis.json"


def project_artifact_availability_path(workspace: Path, codebase_id: str) -> Path:
    return e2e_expansion_dir(workspace, codebase_id) / "project_artifact_availability.json"


def e2e_expansion_report_path(workspace: Path, codebase_id: str) -> Path:
    return e2e_expansion_dir(workspace, codebase_id) / "e2e_expansion_report.md"


def package_manifest_path(workspace: Path, codebase_id: str) -> Path:
    return packaging_dir(workspace, codebase_id) / "package_manifest.json"


def cleanup_plan_path(workspace: Path, codebase_id: str) -> Path:
    return packaging_dir(workspace, codebase_id) / "cleanup_plan.md"


def handoff_checklist_path(workspace: Path, codebase_id: str) -> Path:
    return packaging_dir(workspace, codebase_id) / "handoff_checklist.md"


def package_audit_report_path(workspace: Path, codebase_id: str) -> Path:
    return packaging_dir(workspace, codebase_id) / "package_audit_report.md"


def portal_state_summary_path(workspace: Path, codebase_id: str) -> Path:
    return portal_integration_dir(workspace, codebase_id) / "portal_state_summary.json"


def portal_sections_path(workspace: Path, codebase_id: str) -> Path:
    return portal_integration_dir(workspace, codebase_id) / "portal_sections.json"


def portal_acceptance_panel_path(workspace: Path, codebase_id: str) -> Path:
    return portal_integration_dir(workspace, codebase_id) / "portal_acceptance_panel.json"


def project_portal_v3_html_path(workspace: Path, codebase_id: str) -> Path:
    return portal_integration_dir(workspace, codebase_id) / "project_portal_v3.html"


def stabilization_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "public_surface_snapshot", "artifact_ref": artifact_uri(codebase_id, "stabilization", "public_surface_snapshot.json")},
        {"type": "public_surface_parity_matrix", "artifact_ref": artifact_uri(codebase_id, "stabilization", "public_surface_parity_matrix.json")},
        {"type": "public_surface_drift_report", "artifact_ref": artifact_uri(codebase_id, "stabilization", "public_surface_drift_report.json")},
        {"type": "migration_notes", "artifact_ref": artifact_uri(codebase_id, "stabilization", "migration_notes.md")},
    ]


def e2e_expansion_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "project_e2e_matrix", "artifact_ref": artifact_uri(codebase_id, "e2e_expansion", "project_e2e_matrix.json")},
        {"type": "project_failure_diagnosis", "artifact_ref": artifact_uri(codebase_id, "e2e_expansion", "project_failure_diagnosis.json")},
        {"type": "project_artifact_availability", "artifact_ref": artifact_uri(codebase_id, "e2e_expansion", "project_artifact_availability.json")},
        {"type": "e2e_expansion_report", "artifact_ref": artifact_uri(codebase_id, "e2e_expansion", "e2e_expansion_report.md")},
    ]


def packaging_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "package_manifest", "artifact_ref": artifact_uri(codebase_id, "packaging", "package_manifest.json")},
        {"type": "cleanup_plan", "artifact_ref": artifact_uri(codebase_id, "packaging", "cleanup_plan.md")},
        {"type": "handoff_checklist", "artifact_ref": artifact_uri(codebase_id, "packaging", "handoff_checklist.md")},
        {"type": "package_audit_report", "artifact_ref": artifact_uri(codebase_id, "packaging", "package_audit_report.md")},
    ]


def portal_integration_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "portal_state_summary", "artifact_ref": artifact_uri(codebase_id, "portal_integration", "portal_state_summary.json")},
        {"type": "portal_sections", "artifact_ref": artifact_uri(codebase_id, "portal_integration", "portal_sections.json")},
        {"type": "portal_acceptance_panel", "artifact_ref": artifact_uri(codebase_id, "portal_integration", "portal_acceptance_panel.json")},
        {"type": "project_portal_v3_html", "artifact_ref": artifact_uri(codebase_id, "portal_integration", "project_portal_v3.html")},
    ]


def write_public_surface(workspace: Path, codebase_id: str, snapshot: dict[str, Any], parity: dict[str, Any], drift: dict[str, Any], migration_notes: str) -> None:
    write_json(public_surface_snapshot_path(workspace, codebase_id), snapshot)
    write_json(public_surface_parity_matrix_path(workspace, codebase_id), parity)
    write_json(public_surface_drift_report_path(workspace, codebase_id), drift)
    path = migration_notes_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(migration_notes, encoding="utf-8")


def write_e2e_expansion(workspace: Path, codebase_id: str, matrix: dict[str, Any], diagnosis: dict[str, Any], availability: dict[str, Any], report: str) -> None:
    write_json(project_e2e_matrix_path(workspace, codebase_id), matrix)
    write_json(project_failure_diagnosis_path(workspace, codebase_id), diagnosis)
    write_json(project_artifact_availability_path(workspace, codebase_id), availability)
    path = e2e_expansion_report_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def write_packaging(workspace: Path, codebase_id: str, manifest: dict[str, Any], cleanup: str, handoff: str, audit: str) -> None:
    write_json(package_manifest_path(workspace, codebase_id), manifest)
    cleanup_path = cleanup_plan_path(workspace, codebase_id)
    cleanup_path.parent.mkdir(parents=True, exist_ok=True)
    cleanup_path.write_text(cleanup, encoding="utf-8")
    handoff_checklist_path(workspace, codebase_id).write_text(handoff, encoding="utf-8")
    package_audit_report_path(workspace, codebase_id).write_text(audit, encoding="utf-8")


def write_portal_integration(workspace: Path, codebase_id: str, state: dict[str, Any], sections: dict[str, Any], panel: dict[str, Any], html: str) -> None:
    write_json(portal_state_summary_path(workspace, codebase_id), state)
    write_json(portal_sections_path(workspace, codebase_id), sections)
    write_json(portal_acceptance_panel_path(workspace, codebase_id), panel)
    html_path = project_portal_v3_html_path(workspace, codebase_id)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")


def _read_json_required(path: Path, code: str) -> dict[str, Any]:
    payload = read_json(path, None)
    if not payload:
        raise FileNotFoundError(code)
    return payload


def _read_text_required(path: Path, code: str) -> str:
    if not path.exists():
        raise FileNotFoundError(code)
    return path.read_text(encoding="utf-8")


def read_public_surface_snapshot(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(public_surface_snapshot_path(workspace, codebase_id), "PUBLIC_SURFACE_STABILIZATION_NOT_BUILT")


def read_public_surface_parity_matrix(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(public_surface_parity_matrix_path(workspace, codebase_id), "PUBLIC_SURFACE_STABILIZATION_NOT_BUILT")


def read_public_surface_drift_report(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(public_surface_drift_report_path(workspace, codebase_id), "PUBLIC_SURFACE_STABILIZATION_NOT_BUILT")


def read_migration_notes(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(migration_notes_path(workspace, codebase_id), "PUBLIC_SURFACE_STABILIZATION_NOT_BUILT")


def read_project_e2e_matrix(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(project_e2e_matrix_path(workspace, codebase_id), "REAL_PROJECT_E2E_EXPANSION_NOT_BUILT")


def read_project_failure_diagnosis(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(project_failure_diagnosis_path(workspace, codebase_id), "REAL_PROJECT_E2E_EXPANSION_NOT_BUILT")


def read_project_artifact_availability(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(project_artifact_availability_path(workspace, codebase_id), "REAL_PROJECT_E2E_EXPANSION_NOT_BUILT")


def read_e2e_expansion_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(e2e_expansion_report_path(workspace, codebase_id), "REAL_PROJECT_E2E_EXPANSION_NOT_BUILT")


def read_package_manifest(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(package_manifest_path(workspace, codebase_id), "ACCEPTANCE_PACKAGING_NOT_BUILT")


def read_cleanup_plan(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(cleanup_plan_path(workspace, codebase_id), "ACCEPTANCE_PACKAGING_NOT_BUILT")


def read_handoff_checklist(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(handoff_checklist_path(workspace, codebase_id), "ACCEPTANCE_PACKAGING_NOT_BUILT")


def read_package_audit_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(package_audit_report_path(workspace, codebase_id), "ACCEPTANCE_PACKAGING_NOT_BUILT")


def read_portal_state_summary(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(portal_state_summary_path(workspace, codebase_id), "PORTAL_UX_INTEGRATION_NOT_BUILT")


def read_portal_sections(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(portal_sections_path(workspace, codebase_id), "PORTAL_UX_INTEGRATION_NOT_BUILT")


def read_portal_acceptance_panel(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(portal_acceptance_panel_path(workspace, codebase_id), "PORTAL_UX_INTEGRATION_NOT_BUILT")


def read_project_portal_v3_html(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(project_portal_v3_html_path(workspace, codebase_id), "PORTAL_UX_INTEGRATION_NOT_BUILT")
