"""Persistence helpers for V2.76-V2.80 project acceptance hardening artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir
from .shared import artifact_uri


def stage_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "project_acceptance_hardening"


def section_dir(workspace: Path, codebase_id: str, section: str) -> Path:
    return stage_dir(workspace, codebase_id) / section


def matrix_reconciliation_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "reconciled_matrix", "artifact_ref": artifact_uri(codebase_id, "acceptance_reconciliation", "reconciled_matrix.json")},
        {"type": "status_diff", "artifact_ref": artifact_uri(codebase_id, "acceptance_reconciliation", "status_diff.json")},
        {"type": "reconciliation_report", "artifact_ref": artifact_uri(codebase_id, "acceptance_reconciliation", "reconciliation_report.md")},
    ]


def external_binding_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "project_preflight", "artifact_ref": artifact_uri(codebase_id, "external_project_binding", "project_preflight.json")},
        {"type": "e2e_rerun_records", "artifact_ref": artifact_uri(codebase_id, "external_project_binding", "e2e_rerun_records.json")},
        {"type": "binding_decision_report", "artifact_ref": artifact_uri(codebase_id, "external_project_binding", "binding_decision_report.md")},
    ]


def warning_reduction_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "warning_inventory", "artifact_ref": artifact_uri(codebase_id, "warning_reduction", "warning_inventory.json")},
        {"type": "reduction_plan", "artifact_ref": artifact_uri(codebase_id, "warning_reduction", "reduction_plan.json")},
        {"type": "release_warning_gate", "artifact_ref": artifact_uri(codebase_id, "warning_reduction", "release_warning_gate.json")},
        {"type": "warning_reduction_report", "artifact_ref": artifact_uri(codebase_id, "warning_reduction", "warning_reduction_report.md")},
    ]


def console_productization_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "experience_model", "artifact_ref": artifact_uri(codebase_id, "console_productization", "experience_model.json")},
        {"type": "panel_contract", "artifact_ref": artifact_uri(codebase_id, "console_productization", "panel_contract.json")},
        {"type": "action_registry", "artifact_ref": artifact_uri(codebase_id, "console_productization", "action_registry.json")},
        {"type": "maintainer_console_product_report", "artifact_ref": artifact_uri(codebase_id, "console_productization", "maintainer_console_product_report.md")},
    ]


def release_readiness_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "readiness_gate", "artifact_ref": artifact_uri(codebase_id, "release_readiness", "readiness_gate.json")},
        {"type": "restore_verification", "artifact_ref": artifact_uri(codebase_id, "release_readiness", "restore_verification.json")},
        {"type": "smoke_run_records", "artifact_ref": artifact_uri(codebase_id, "release_readiness", "smoke_run_records.json")},
        {"type": "handoff_package_manifest", "artifact_ref": artifact_uri(codebase_id, "release_readiness", "handoff_package_manifest.json")},
        {"type": "release_closure_report", "artifact_ref": artifact_uri(codebase_id, "release_readiness", "release_closure_report.md")},
    ]


def _path(workspace: Path, codebase_id: str, section: str, filename: str) -> Path:
    return section_dir(workspace, codebase_id, section) / filename


def _read_json_required(path: Path, code: str) -> dict[str, Any]:
    payload = read_json(path, None)
    if not payload:
        raise FileNotFoundError(code)
    return payload


def _read_text_required(path: Path, code: str) -> str:
    if not path.exists():
        raise FileNotFoundError(code)
    return path.read_text(encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_matrix_reconciliation(workspace: Path, codebase_id: str, matrix: dict[str, Any], diff: dict[str, Any], report: str) -> None:
    write_json(_path(workspace, codebase_id, "acceptance_reconciliation", "reconciled_matrix.json"), matrix)
    write_json(_path(workspace, codebase_id, "acceptance_reconciliation", "status_diff.json"), diff)
    _write_text(_path(workspace, codebase_id, "acceptance_reconciliation", "reconciliation_report.md"), report)


def read_reconciled_matrix(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "acceptance_reconciliation", "reconciled_matrix.json"), "ACCEPTANCE_RECONCILIATION_NOT_BUILT")


def read_status_diff(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "acceptance_reconciliation", "status_diff.json"), "ACCEPTANCE_RECONCILIATION_NOT_BUILT")


def read_reconciliation_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "acceptance_reconciliation", "reconciliation_report.md"), "ACCEPTANCE_RECONCILIATION_NOT_BUILT")


def write_external_binding(workspace: Path, codebase_id: str, preflight: dict[str, Any], rerun: dict[str, Any], report: str) -> None:
    write_json(_path(workspace, codebase_id, "external_project_binding", "project_preflight.json"), preflight)
    write_json(_path(workspace, codebase_id, "external_project_binding", "e2e_rerun_records.json"), rerun)
    _write_text(_path(workspace, codebase_id, "external_project_binding", "binding_decision_report.md"), report)


def read_project_preflight(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "external_project_binding", "project_preflight.json"), "EXTERNAL_PROJECT_REAL_BINDING_NOT_BUILT")


def read_e2e_rerun_records(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "external_project_binding", "e2e_rerun_records.json"), "EXTERNAL_PROJECT_REAL_BINDING_NOT_BUILT")


def read_binding_decision_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "external_project_binding", "binding_decision_report.md"), "EXTERNAL_PROJECT_REAL_BINDING_NOT_BUILT")


def write_warning_reduction(workspace: Path, codebase_id: str, inventory: dict[str, Any], plan: dict[str, Any], gate: dict[str, Any], report: str) -> None:
    write_json(_path(workspace, codebase_id, "warning_reduction", "warning_inventory.json"), inventory)
    write_json(_path(workspace, codebase_id, "warning_reduction", "reduction_plan.json"), plan)
    write_json(_path(workspace, codebase_id, "warning_reduction", "release_warning_gate.json"), gate)
    _write_text(_path(workspace, codebase_id, "warning_reduction", "warning_reduction_report.md"), report)


def read_warning_inventory(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "warning_reduction", "warning_inventory.json"), "WARNING_REDUCTION_NOT_BUILT")


def read_reduction_plan(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "warning_reduction", "reduction_plan.json"), "WARNING_REDUCTION_NOT_BUILT")


def read_release_warning_gate(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "warning_reduction", "release_warning_gate.json"), "WARNING_REDUCTION_NOT_BUILT")


def read_warning_reduction_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "warning_reduction", "warning_reduction_report.md"), "WARNING_REDUCTION_NOT_BUILT")


def write_console_productization(workspace: Path, codebase_id: str, model: dict[str, Any], contract: dict[str, Any], actions: dict[str, Any], report: str) -> None:
    write_json(_path(workspace, codebase_id, "console_productization", "experience_model.json"), model)
    write_json(_path(workspace, codebase_id, "console_productization", "panel_contract.json"), contract)
    write_json(_path(workspace, codebase_id, "console_productization", "action_registry.json"), actions)
    _write_text(_path(workspace, codebase_id, "console_productization", "maintainer_console_product_report.md"), report)


def read_experience_model(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "console_productization", "experience_model.json"), "CONSOLE_PRODUCTIZATION_NOT_BUILT")


def read_panel_contract(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "console_productization", "panel_contract.json"), "CONSOLE_PRODUCTIZATION_NOT_BUILT")


def read_action_registry(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "console_productization", "action_registry.json"), "CONSOLE_PRODUCTIZATION_NOT_BUILT")


def read_console_product_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "console_productization", "maintainer_console_product_report.md"), "CONSOLE_PRODUCTIZATION_NOT_BUILT")


def write_release_readiness(workspace: Path, codebase_id: str, gate: dict[str, Any], restore: dict[str, Any], smoke: dict[str, Any], manifest: dict[str, Any], report: str) -> None:
    write_json(_path(workspace, codebase_id, "release_readiness", "readiness_gate.json"), gate)
    write_json(_path(workspace, codebase_id, "release_readiness", "restore_verification.json"), restore)
    write_json(_path(workspace, codebase_id, "release_readiness", "smoke_run_records.json"), smoke)
    write_json(_path(workspace, codebase_id, "release_readiness", "handoff_package_manifest.json"), manifest)
    _write_text(_path(workspace, codebase_id, "release_readiness", "release_closure_report.md"), report)


def read_readiness_gate(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "release_readiness", "readiness_gate.json"), "RELEASE_READINESS_CLOSURE_NOT_BUILT")


def read_restore_verification(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "release_readiness", "restore_verification.json"), "RELEASE_READINESS_CLOSURE_NOT_BUILT")


def read_smoke_run_records(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "release_readiness", "smoke_run_records.json"), "RELEASE_READINESS_CLOSURE_NOT_BUILT")


def read_handoff_package_manifest(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "release_readiness", "handoff_package_manifest.json"), "RELEASE_READINESS_CLOSURE_NOT_BUILT")


def read_release_closure_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "release_readiness", "release_closure_report.md"), "RELEASE_READINESS_CLOSURE_NOT_BUILT")
