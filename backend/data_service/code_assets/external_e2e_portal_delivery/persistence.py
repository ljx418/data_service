"""Persistence helpers for V2.63-V2.66 external E2E portal delivery artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir
from .shared import artifact_uri


def stage_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "external_e2e_portal_delivery"


def external_e2e_dir(workspace: Path, codebase_id: str) -> Path:
    return stage_dir(workspace, codebase_id) / "external_e2e"


def portal_v3_dir(workspace: Path, codebase_id: str) -> Path:
    return stage_dir(workspace, codebase_id) / "portal_v3"


def delivery_dir(workspace: Path, codebase_id: str) -> Path:
    return stage_dir(workspace, codebase_id) / "delivery"


def contract_regression_dir(workspace: Path, codebase_id: str) -> Path:
    return stage_dir(workspace, codebase_id) / "contract_regression"


def path_binding_dir(workspace: Path, codebase_id: str) -> Path:
    return stage_dir(workspace, codebase_id) / "path_binding"


def worktree_delivery_dir(workspace: Path, codebase_id: str) -> Path:
    return stage_dir(workspace, codebase_id) / "worktree_delivery"


def surface_baseline_dir(workspace: Path, codebase_id: str) -> Path:
    return stage_dir(workspace, codebase_id) / "surface_baseline"


def maintainer_dashboard_dir(workspace: Path, codebase_id: str) -> Path:
    return stage_dir(workspace, codebase_id) / "maintainer_dashboard"


def full_project_matrix_path(workspace: Path, codebase_id: str) -> Path:
    return external_e2e_dir(workspace, codebase_id) / "full_project_matrix.json"


def project_run_records_path(workspace: Path, codebase_id: str) -> Path:
    return external_e2e_dir(workspace, codebase_id) / "project_run_records.json"


def artifact_readiness_path(workspace: Path, codebase_id: str) -> Path:
    return external_e2e_dir(workspace, codebase_id) / "artifact_readiness.json"


def external_e2e_report_path(workspace: Path, codebase_id: str) -> Path:
    return external_e2e_dir(workspace, codebase_id) / "external_e2e_report.md"


def experience_model_path(workspace: Path, codebase_id: str) -> Path:
    return portal_v3_dir(workspace, codebase_id) / "experience_model.json"


def navigation_model_path(workspace: Path, codebase_id: str) -> Path:
    return portal_v3_dir(workspace, codebase_id) / "navigation_model.json"


def status_panels_path(workspace: Path, codebase_id: str) -> Path:
    return portal_v3_dir(workspace, codebase_id) / "status_panels.json"


def portal_html_path(workspace: Path, codebase_id: str) -> Path:
    return portal_v3_dir(workspace, codebase_id) / "project_portal_v3_plus.html"


def version_manifest_path(workspace: Path, codebase_id: str) -> Path:
    return delivery_dir(workspace, codebase_id) / "version_manifest.json"


def review_package_manifest_path(workspace: Path, codebase_id: str) -> Path:
    return delivery_dir(workspace, codebase_id) / "review_package_manifest.json"


def cleanup_execution_plan_path(workspace: Path, codebase_id: str) -> Path:
    return delivery_dir(workspace, codebase_id) / "cleanup_execution_plan.md"


def delivery_audit_report_path(workspace: Path, codebase_id: str) -> Path:
    return delivery_dir(workspace, codebase_id) / "delivery_audit_report.md"


def contract_baseline_path(workspace: Path, codebase_id: str) -> Path:
    return contract_regression_dir(workspace, codebase_id) / "contract_baseline.json"


def contract_diff_path(workspace: Path, codebase_id: str) -> Path:
    return contract_regression_dir(workspace, codebase_id) / "contract_diff.json"


def compatibility_report_path(workspace: Path, codebase_id: str) -> Path:
    return contract_regression_dir(workspace, codebase_id) / "compatibility_report.json"


def regression_diagnosis_path(workspace: Path, codebase_id: str) -> Path:
    return contract_regression_dir(workspace, codebase_id) / "regression_diagnosis.md"


def path_binding_matrix_path(workspace: Path, codebase_id: str) -> Path:
    return path_binding_dir(workspace, codebase_id) / "path_binding_matrix.json"


def path_binding_evidence_path(workspace: Path, codebase_id: str) -> Path:
    return path_binding_dir(workspace, codebase_id) / "path_binding_evidence.json"


def path_binding_report_path(workspace: Path, codebase_id: str) -> Path:
    return path_binding_dir(workspace, codebase_id) / "path_binding_report.md"


def delivery_review_manifest_path(workspace: Path, codebase_id: str) -> Path:
    return worktree_delivery_dir(workspace, codebase_id) / "delivery_review_manifest.json"


def delivery_review_plan_path(workspace: Path, codebase_id: str) -> Path:
    return worktree_delivery_dir(workspace, codebase_id) / "delivery_review_plan.md"


def delivery_review_audit_path(workspace: Path, codebase_id: str) -> Path:
    return worktree_delivery_dir(workspace, codebase_id) / "delivery_review_audit.md"


def surface_baseline_version_path(workspace: Path, codebase_id: str) -> Path:
    return surface_baseline_dir(workspace, codebase_id) / "surface_baseline_version.json"


def surface_baseline_diff_path(workspace: Path, codebase_id: str) -> Path:
    return surface_baseline_dir(workspace, codebase_id) / "surface_baseline_diff.json"


def surface_baseline_report_path(workspace: Path, codebase_id: str) -> Path:
    return surface_baseline_dir(workspace, codebase_id) / "surface_baseline_report.md"


def maintainer_dashboard_model_path(workspace: Path, codebase_id: str) -> Path:
    return maintainer_dashboard_dir(workspace, codebase_id) / "maintainer_home_model.json"


def maintainer_dashboard_panels_path(workspace: Path, codebase_id: str) -> Path:
    return maintainer_dashboard_dir(workspace, codebase_id) / "maintainer_status_panels.json"


def maintainer_dashboard_html_path(workspace: Path, codebase_id: str) -> Path:
    return maintainer_dashboard_dir(workspace, codebase_id) / "maintainer_home.html"


def external_e2e_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "full_project_matrix", "artifact_ref": artifact_uri(codebase_id, "external_e2e", "full_project_matrix.json")},
        {"type": "project_run_records", "artifact_ref": artifact_uri(codebase_id, "external_e2e", "project_run_records.json")},
        {"type": "artifact_readiness", "artifact_ref": artifact_uri(codebase_id, "external_e2e", "artifact_readiness.json")},
        {"type": "external_e2e_report", "artifact_ref": artifact_uri(codebase_id, "external_e2e", "external_e2e_report.md")},
    ]


def portal_v3_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "experience_model", "artifact_ref": artifact_uri(codebase_id, "portal_v3", "experience_model.json")},
        {"type": "navigation_model", "artifact_ref": artifact_uri(codebase_id, "portal_v3", "navigation_model.json")},
        {"type": "status_panels", "artifact_ref": artifact_uri(codebase_id, "portal_v3", "status_panels.json")},
        {"type": "project_portal_v3_plus_html", "artifact_ref": artifact_uri(codebase_id, "portal_v3", "project_portal_v3_plus.html")},
    ]


def delivery_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "version_manifest", "artifact_ref": artifact_uri(codebase_id, "delivery", "version_manifest.json")},
        {"type": "review_package_manifest", "artifact_ref": artifact_uri(codebase_id, "delivery", "review_package_manifest.json")},
        {"type": "cleanup_execution_plan", "artifact_ref": artifact_uri(codebase_id, "delivery", "cleanup_execution_plan.md")},
        {"type": "delivery_audit_report", "artifact_ref": artifact_uri(codebase_id, "delivery", "delivery_audit_report.md")},
    ]


def contract_regression_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "contract_baseline", "artifact_ref": artifact_uri(codebase_id, "contract_regression", "contract_baseline.json")},
        {"type": "contract_diff", "artifact_ref": artifact_uri(codebase_id, "contract_regression", "contract_diff.json")},
        {"type": "compatibility_report", "artifact_ref": artifact_uri(codebase_id, "contract_regression", "compatibility_report.json")},
        {"type": "regression_diagnosis", "artifact_ref": artifact_uri(codebase_id, "contract_regression", "regression_diagnosis.md")},
    ]


def path_binding_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "path_binding_matrix", "artifact_ref": artifact_uri(codebase_id, "path_binding", "path_binding_matrix.json")},
        {"type": "path_binding_evidence", "artifact_ref": artifact_uri(codebase_id, "path_binding", "path_binding_evidence.json")},
        {"type": "path_binding_report", "artifact_ref": artifact_uri(codebase_id, "path_binding", "path_binding_report.md")},
    ]


def worktree_delivery_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "delivery_review_manifest", "artifact_ref": artifact_uri(codebase_id, "worktree_delivery", "delivery_review_manifest.json")},
        {"type": "delivery_review_plan", "artifact_ref": artifact_uri(codebase_id, "worktree_delivery", "delivery_review_plan.md")},
        {"type": "delivery_review_audit", "artifact_ref": artifact_uri(codebase_id, "worktree_delivery", "delivery_review_audit.md")},
    ]


def surface_baseline_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "surface_baseline_version", "artifact_ref": artifact_uri(codebase_id, "surface_baseline", "surface_baseline_version.json")},
        {"type": "surface_baseline_diff", "artifact_ref": artifact_uri(codebase_id, "surface_baseline", "surface_baseline_diff.json")},
        {"type": "surface_baseline_report", "artifact_ref": artifact_uri(codebase_id, "surface_baseline", "surface_baseline_report.md")},
    ]


def maintainer_dashboard_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "maintainer_home_model", "artifact_ref": artifact_uri(codebase_id, "maintainer_dashboard", "maintainer_home_model.json")},
        {"type": "maintainer_status_panels", "artifact_ref": artifact_uri(codebase_id, "maintainer_dashboard", "maintainer_status_panels.json")},
        {"type": "maintainer_home_html", "artifact_ref": artifact_uri(codebase_id, "maintainer_dashboard", "maintainer_home.html")},
    ]


def write_external_e2e(workspace: Path, codebase_id: str, matrix: dict[str, Any], records: dict[str, Any], readiness: dict[str, Any], report: str) -> None:
    write_json(full_project_matrix_path(workspace, codebase_id), matrix)
    write_json(project_run_records_path(workspace, codebase_id), records)
    write_json(artifact_readiness_path(workspace, codebase_id), readiness)
    path = external_e2e_report_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def write_portal_v3(workspace: Path, codebase_id: str, experience: dict[str, Any], navigation: dict[str, Any], panels: dict[str, Any], html: str) -> None:
    write_json(experience_model_path(workspace, codebase_id), experience)
    write_json(navigation_model_path(workspace, codebase_id), navigation)
    write_json(status_panels_path(workspace, codebase_id), panels)
    path = portal_html_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def write_delivery(workspace: Path, codebase_id: str, version: dict[str, Any], package: dict[str, Any], cleanup: str, audit: str) -> None:
    write_json(version_manifest_path(workspace, codebase_id), version)
    write_json(review_package_manifest_path(workspace, codebase_id), package)
    path = cleanup_execution_plan_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(cleanup, encoding="utf-8")
    delivery_audit_report_path(workspace, codebase_id).write_text(audit, encoding="utf-8")


def write_contract_regression(workspace: Path, codebase_id: str, baseline: dict[str, Any], diff: dict[str, Any], compatibility: dict[str, Any], diagnosis: str) -> None:
    write_json(contract_baseline_path(workspace, codebase_id), baseline)
    write_json(contract_diff_path(workspace, codebase_id), diff)
    write_json(compatibility_report_path(workspace, codebase_id), compatibility)
    path = regression_diagnosis_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(diagnosis, encoding="utf-8")


def write_path_binding(workspace: Path, codebase_id: str, matrix: dict[str, Any], evidence: dict[str, Any], report: str) -> None:
    write_json(path_binding_matrix_path(workspace, codebase_id), matrix)
    write_json(path_binding_evidence_path(workspace, codebase_id), evidence)
    path = path_binding_report_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def write_worktree_delivery(workspace: Path, codebase_id: str, manifest: dict[str, Any], plan: str, audit: str) -> None:
    write_json(delivery_review_manifest_path(workspace, codebase_id), manifest)
    path = delivery_review_plan_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(plan, encoding="utf-8")
    delivery_review_audit_path(workspace, codebase_id).write_text(audit, encoding="utf-8")


def write_surface_baseline(workspace: Path, codebase_id: str, baseline: dict[str, Any], diff: dict[str, Any], report: str) -> None:
    write_json(surface_baseline_version_path(workspace, codebase_id), baseline)
    write_json(surface_baseline_diff_path(workspace, codebase_id), diff)
    path = surface_baseline_report_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(report, encoding="utf-8")


def write_maintainer_dashboard(workspace: Path, codebase_id: str, model: dict[str, Any], panels: dict[str, Any], html: str) -> None:
    write_json(maintainer_dashboard_model_path(workspace, codebase_id), model)
    write_json(maintainer_dashboard_panels_path(workspace, codebase_id), panels)
    path = maintainer_dashboard_html_path(workspace, codebase_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def _read_json_required(path: Path, code: str) -> dict[str, Any]:
    payload = read_json(path, None)
    if not payload:
        raise FileNotFoundError(code)
    return payload


def _read_text_required(path: Path, code: str) -> str:
    if not path.exists():
        raise FileNotFoundError(code)
    return path.read_text(encoding="utf-8")


def read_full_project_matrix(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(full_project_matrix_path(workspace, codebase_id), "EXTERNAL_E2E_NOT_BUILT")


def read_project_run_records(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(project_run_records_path(workspace, codebase_id), "EXTERNAL_E2E_NOT_BUILT")


def read_artifact_readiness(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(artifact_readiness_path(workspace, codebase_id), "EXTERNAL_E2E_NOT_BUILT")


def read_external_e2e_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(external_e2e_report_path(workspace, codebase_id), "EXTERNAL_E2E_NOT_BUILT")


def read_experience_model(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(experience_model_path(workspace, codebase_id), "PORTAL_V3_NOT_BUILT")


def read_navigation_model(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(navigation_model_path(workspace, codebase_id), "PORTAL_V3_NOT_BUILT")


def read_status_panels(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(status_panels_path(workspace, codebase_id), "PORTAL_V3_NOT_BUILT")


def read_portal_html(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(portal_html_path(workspace, codebase_id), "PORTAL_V3_NOT_BUILT")


def read_version_manifest(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(version_manifest_path(workspace, codebase_id), "DELIVERY_NOT_BUILT")


def read_review_package_manifest(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(review_package_manifest_path(workspace, codebase_id), "DELIVERY_NOT_BUILT")


def read_cleanup_execution_plan(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(cleanup_execution_plan_path(workspace, codebase_id), "DELIVERY_NOT_BUILT")


def read_delivery_audit_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(delivery_audit_report_path(workspace, codebase_id), "DELIVERY_NOT_BUILT")


def read_contract_baseline(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(contract_baseline_path(workspace, codebase_id), "CONTRACT_REGRESSION_NOT_BUILT")


def read_contract_diff(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(contract_diff_path(workspace, codebase_id), "CONTRACT_REGRESSION_NOT_BUILT")


def read_compatibility_report(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(compatibility_report_path(workspace, codebase_id), "CONTRACT_REGRESSION_NOT_BUILT")


def read_regression_diagnosis(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(regression_diagnosis_path(workspace, codebase_id), "CONTRACT_REGRESSION_NOT_BUILT")


def read_path_binding_matrix(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(path_binding_matrix_path(workspace, codebase_id), "PATH_BINDING_NOT_BUILT")


def read_path_binding_evidence(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(path_binding_evidence_path(workspace, codebase_id), "PATH_BINDING_NOT_BUILT")


def read_path_binding_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(path_binding_report_path(workspace, codebase_id), "PATH_BINDING_NOT_BUILT")


def read_delivery_review_manifest(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(delivery_review_manifest_path(workspace, codebase_id), "WORKTREE_DELIVERY_NOT_BUILT")


def read_delivery_review_plan(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(delivery_review_plan_path(workspace, codebase_id), "WORKTREE_DELIVERY_NOT_BUILT")


def read_delivery_review_audit(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(delivery_review_audit_path(workspace, codebase_id), "WORKTREE_DELIVERY_NOT_BUILT")


def read_surface_baseline_version(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(surface_baseline_version_path(workspace, codebase_id), "SURFACE_BASELINE_NOT_BUILT")


def read_surface_baseline_diff(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(surface_baseline_diff_path(workspace, codebase_id), "SURFACE_BASELINE_NOT_BUILT")


def read_surface_baseline_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(surface_baseline_report_path(workspace, codebase_id), "SURFACE_BASELINE_NOT_BUILT")


def read_maintainer_dashboard_model(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(maintainer_dashboard_model_path(workspace, codebase_id), "MAINTAINER_DASHBOARD_NOT_BUILT")


def read_maintainer_dashboard_panels(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(maintainer_dashboard_panels_path(workspace, codebase_id), "MAINTAINER_DASHBOARD_NOT_BUILT")


def read_maintainer_dashboard_html(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(maintainer_dashboard_html_path(workspace, codebase_id), "MAINTAINER_DASHBOARD_NOT_BUILT")
