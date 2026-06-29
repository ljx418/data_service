"""Persistence helpers for V2.71-V2.75 agent memory release artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir
from .shared import artifact_uri


def stage_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "agent_memory_release"


def section_dir(workspace: Path, codebase_id: str, section: str) -> Path:
    return stage_dir(workspace, codebase_id) / section


def external_project_closure_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "project_binding_closure", "artifact_ref": artifact_uri(codebase_id, "external_project_closure", "project_binding_closure.json")},
        {"type": "e2e_closure_report", "artifact_ref": artifact_uri(codebase_id, "external_project_closure", "e2e_closure_report.md")},
    ]


def ci_warning_governance_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "ci_matrix", "artifact_ref": artifact_uri(codebase_id, "ci_warning_governance", "ci_matrix.json")},
        {"type": "warning_budget", "artifact_ref": artifact_uri(codebase_id, "ci_warning_governance", "warning_budget.json")},
        {"type": "failure_diagnosis", "artifact_ref": artifact_uri(codebase_id, "ci_warning_governance", "failure_diagnosis.json")},
        {"type": "ci_readiness_report", "artifact_ref": artifact_uri(codebase_id, "ci_warning_governance", "ci_readiness_report.md")},
    ]


def agent_memory_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "memory_index", "artifact_ref": artifact_uri(codebase_id, "agent_memory", "memory_index.json")},
        {"type": "evidence_index", "artifact_ref": artifact_uri(codebase_id, "agent_memory", "evidence_index.json")},
        {"type": "acceptance_state", "artifact_ref": artifact_uri(codebase_id, "agent_memory", "acceptance_state.json")},
        {"type": "task_briefing", "artifact_ref": artifact_uri(codebase_id, "agent_memory", "task_briefing.json")},
        {"type": "retention_policy", "artifact_ref": artifact_uri(codebase_id, "agent_memory", "retention_policy.md")},
    ]


def interactive_console_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "console_model", "artifact_ref": artifact_uri(codebase_id, "interactive_console", "console_model.json")},
        {"type": "navigation_model", "artifact_ref": artifact_uri(codebase_id, "interactive_console", "navigation_model.json")},
        {"type": "status_panels", "artifact_ref": artifact_uri(codebase_id, "interactive_console", "status_panels.json")},
        {"type": "maintainer_console_html", "artifact_ref": artifact_uri(codebase_id, "interactive_console", "maintainer_console.html")},
    ]


def release_restore_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "release_manifest", "artifact_ref": artifact_uri(codebase_id, "release_restore", "release_manifest.json")},
        {"type": "mcp_config_template", "artifact_ref": artifact_uri(codebase_id, "release_restore", "mcp_config_template.json")},
        {"type": "smoke_commands", "artifact_ref": artifact_uri(codebase_id, "release_restore", "smoke_commands.md")},
        {"type": "restore_runbook", "artifact_ref": artifact_uri(codebase_id, "release_restore", "restore_runbook.md")},
        {"type": "release_readiness_report", "artifact_ref": artifact_uri(codebase_id, "release_restore", "release_readiness_report.md")},
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


def write_external_project_closure(workspace: Path, codebase_id: str, closure: dict[str, Any], report: str) -> None:
    write_json(_path(workspace, codebase_id, "external_project_closure", "project_binding_closure.json"), closure)
    _write_text(_path(workspace, codebase_id, "external_project_closure", "e2e_closure_report.md"), report)


def read_project_binding_closure(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "external_project_closure", "project_binding_closure.json"), "EXTERNAL_PROJECT_CLOSURE_NOT_BUILT")


def read_e2e_closure_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "external_project_closure", "e2e_closure_report.md"), "EXTERNAL_PROJECT_CLOSURE_NOT_BUILT")


def write_ci_warning_governance(workspace: Path, codebase_id: str, matrix: dict[str, Any], budget: dict[str, Any], diagnosis: dict[str, Any], report: str) -> None:
    write_json(_path(workspace, codebase_id, "ci_warning_governance", "ci_matrix.json"), matrix)
    write_json(_path(workspace, codebase_id, "ci_warning_governance", "warning_budget.json"), budget)
    write_json(_path(workspace, codebase_id, "ci_warning_governance", "failure_diagnosis.json"), diagnosis)
    _write_text(_path(workspace, codebase_id, "ci_warning_governance", "ci_readiness_report.md"), report)


def read_ci_matrix(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "ci_warning_governance", "ci_matrix.json"), "CI_WARNING_GOVERNANCE_NOT_BUILT")


def read_warning_budget(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "ci_warning_governance", "warning_budget.json"), "CI_WARNING_GOVERNANCE_NOT_BUILT")


def read_failure_diagnosis(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "ci_warning_governance", "failure_diagnosis.json"), "CI_WARNING_GOVERNANCE_NOT_BUILT")


def read_ci_readiness_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "ci_warning_governance", "ci_readiness_report.md"), "CI_WARNING_GOVERNANCE_NOT_BUILT")


def write_agent_memory(workspace: Path, codebase_id: str, memory: dict[str, Any], evidence: dict[str, Any], acceptance: dict[str, Any], briefing: dict[str, Any], retention: str) -> None:
    write_json(_path(workspace, codebase_id, "agent_memory", "memory_index.json"), memory)
    write_json(_path(workspace, codebase_id, "agent_memory", "evidence_index.json"), evidence)
    write_json(_path(workspace, codebase_id, "agent_memory", "acceptance_state.json"), acceptance)
    write_json(_path(workspace, codebase_id, "agent_memory", "task_briefing.json"), briefing)
    _write_text(_path(workspace, codebase_id, "agent_memory", "retention_policy.md"), retention)


def read_memory_index(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "agent_memory", "memory_index.json"), "AGENT_MEMORY_NOT_BUILT")


def read_evidence_index(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "agent_memory", "evidence_index.json"), "AGENT_MEMORY_NOT_BUILT")


def read_acceptance_state(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "agent_memory", "acceptance_state.json"), "AGENT_MEMORY_NOT_BUILT")


def read_task_briefing(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "agent_memory", "task_briefing.json"), "AGENT_MEMORY_NOT_BUILT")


def read_retention_policy(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "agent_memory", "retention_policy.md"), "AGENT_MEMORY_NOT_BUILT")


def write_interactive_console(workspace: Path, codebase_id: str, model: dict[str, Any], navigation: dict[str, Any], panels: dict[str, Any], html: str) -> None:
    write_json(_path(workspace, codebase_id, "interactive_console", "console_model.json"), model)
    write_json(_path(workspace, codebase_id, "interactive_console", "navigation_model.json"), navigation)
    write_json(_path(workspace, codebase_id, "interactive_console", "status_panels.json"), panels)
    _write_text(_path(workspace, codebase_id, "interactive_console", "maintainer_console.html"), html)


def read_console_model(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "interactive_console", "console_model.json"), "INTERACTIVE_CONSOLE_NOT_BUILT")


def read_navigation_model(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "interactive_console", "navigation_model.json"), "INTERACTIVE_CONSOLE_NOT_BUILT")


def read_console_status_panels(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "interactive_console", "status_panels.json"), "INTERACTIVE_CONSOLE_NOT_BUILT")


def read_maintainer_console_html(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "interactive_console", "maintainer_console.html"), "INTERACTIVE_CONSOLE_NOT_BUILT")


def write_release_restore(workspace: Path, codebase_id: str, manifest: dict[str, Any], mcp_config: dict[str, Any], smoke: str, runbook: str, report: str) -> None:
    write_json(_path(workspace, codebase_id, "release_restore", "release_manifest.json"), manifest)
    write_json(_path(workspace, codebase_id, "release_restore", "mcp_config_template.json"), mcp_config)
    _write_text(_path(workspace, codebase_id, "release_restore", "smoke_commands.md"), smoke)
    _write_text(_path(workspace, codebase_id, "release_restore", "restore_runbook.md"), runbook)
    _write_text(_path(workspace, codebase_id, "release_restore", "release_readiness_report.md"), report)


def read_release_manifest(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "release_restore", "release_manifest.json"), "RELEASE_RESTORE_NOT_BUILT")


def read_mcp_config_template(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "release_restore", "mcp_config_template.json"), "RELEASE_RESTORE_NOT_BUILT")


def read_smoke_commands(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "release_restore", "smoke_commands.md"), "RELEASE_RESTORE_NOT_BUILT")


def read_restore_runbook(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "release_restore", "restore_runbook.md"), "RELEASE_RESTORE_NOT_BUILT")


def read_release_readiness_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "release_restore", "release_readiness_report.md"), "RELEASE_RESTORE_NOT_BUILT")

