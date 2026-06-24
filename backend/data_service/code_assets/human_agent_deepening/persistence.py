"""Persistence helpers for V2.54-V2.58 Human / Agent Deepening artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir


def human_agent_deepening_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "human_agent_deepening"


def human_portal_deepening_dir(workspace: Path, codebase_id: str) -> Path:
    return human_agent_deepening_dir(workspace, codebase_id) / "human_portal_deepening"


def project_story_path(workspace: Path, codebase_id: str) -> Path:
    return human_portal_deepening_dir(workspace, codebase_id) / "project_story.json"


def risk_priority_path(workspace: Path, codebase_id: str) -> Path:
    return human_portal_deepening_dir(workspace, codebase_id) / "risk_priority.json"


def reading_path_path(workspace: Path, codebase_id: str) -> Path:
    return human_portal_deepening_dir(workspace, codebase_id) / "reading_path.json"


def chart_audit_path(workspace: Path, codebase_id: str) -> Path:
    return human_portal_deepening_dir(workspace, codebase_id) / "chart_audit.json"


def portal_v2_html_path(workspace: Path, codebase_id: str) -> Path:
    return human_portal_deepening_dir(workspace, codebase_id) / "project_portal_v2.html"


def agent_task_workflow_dir(workspace: Path, codebase_id: str, task_id: str) -> Path:
    return human_agent_deepening_dir(workspace, codebase_id) / "agent_task_workflow" / task_id


def workflow_bundle_path(workspace: Path, codebase_id: str, task_id: str) -> Path:
    return agent_task_workflow_dir(workspace, codebase_id, task_id) / "workflow_bundle.json"


def stop_conditions_path(workspace: Path, codebase_id: str, task_id: str) -> Path:
    return agent_task_workflow_dir(workspace, codebase_id, task_id) / "stop_conditions.json"


def task_workflow_suggested_tests_path(workspace: Path, codebase_id: str, task_id: str) -> Path:
    return agent_task_workflow_dir(workspace, codebase_id, task_id) / "suggested_tests.json"


def task_workflow_markdown_path(workspace: Path, codebase_id: str, task_id: str) -> Path:
    return agent_task_workflow_dir(workspace, codebase_id, task_id) / "task_workflow.md"


def doc_code_evidence_loop_dir(workspace: Path, codebase_id: str) -> Path:
    return human_agent_deepening_dir(workspace, codebase_id) / "doc_code_evidence_loop"


def evidence_loop_path(workspace: Path, codebase_id: str) -> Path:
    return doc_code_evidence_loop_dir(workspace, codebase_id) / "evidence_loop.json"


def decision_history_path(workspace: Path, codebase_id: str) -> Path:
    return doc_code_evidence_loop_dir(workspace, codebase_id) / "decision_history.jsonl"


def rule_effect_path(workspace: Path, codebase_id: str) -> Path:
    return doc_code_evidence_loop_dir(workspace, codebase_id) / "rule_effect.json"


def evidence_loop_report_path(workspace: Path, codebase_id: str) -> Path:
    return doc_code_evidence_loop_dir(workspace, codebase_id) / "evidence_loop_report.md"


def regression_expansion_dir(workspace: Path, codebase_id: str) -> Path:
    return human_agent_deepening_dir(workspace, codebase_id) / "regression_expansion"


def expanded_matrix_path(workspace: Path, codebase_id: str) -> Path:
    return regression_expansion_dir(workspace, codebase_id) / "expanded_matrix.json"


def artifact_diff_path(workspace: Path, codebase_id: str) -> Path:
    return regression_expansion_dir(workspace, codebase_id) / "artifact_diff.json"


def failure_diagnosis_path(workspace: Path, codebase_id: str) -> Path:
    return regression_expansion_dir(workspace, codebase_id) / "failure_diagnosis.json"


def regression_report_path(workspace: Path, codebase_id: str) -> Path:
    return regression_expansion_dir(workspace, codebase_id) / "regression_report.md"


def restore_ux_dir(workspace: Path, codebase_id: str) -> Path:
    return human_agent_deepening_dir(workspace, codebase_id) / "restore_ux"


def restore_checklist_path(workspace: Path, codebase_id: str) -> Path:
    return restore_ux_dir(workspace, codebase_id) / "restore_checklist.md"


def troubleshooting_path(workspace: Path, codebase_id: str) -> Path:
    return restore_ux_dir(workspace, codebase_id) / "troubleshooting.md"


def onboarding_report_path(workspace: Path, codebase_id: str) -> Path:
    return restore_ux_dir(workspace, codebase_id) / "onboarding_report.json"


def human_portal_deepening_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    prefix = f"human_agent_deepening://{codebase_id}/human_portal_deepening"
    return [
        {"type": "project_story", "artifact_ref": f"{prefix}/project_story.json"},
        {"type": "risk_priority", "artifact_ref": f"{prefix}/risk_priority.json"},
        {"type": "reading_path", "artifact_ref": f"{prefix}/reading_path.json"},
        {"type": "chart_audit", "artifact_ref": f"{prefix}/chart_audit.json"},
        {"type": "project_portal_v2_html", "artifact_ref": f"{prefix}/project_portal_v2.html"},
    ]


def agent_task_workflow_artifact_refs(codebase_id: str, task_id: str) -> list[dict[str, str]]:
    prefix = f"human_agent_deepening://{codebase_id}/agent_task_workflow/{task_id}"
    return [
        {"type": "workflow_bundle", "artifact_ref": f"{prefix}/workflow_bundle.json"},
        {"type": "stop_conditions", "artifact_ref": f"{prefix}/stop_conditions.json"},
        {"type": "suggested_tests", "artifact_ref": f"{prefix}/suggested_tests.json"},
        {"type": "task_workflow_markdown", "artifact_ref": f"{prefix}/task_workflow.md"},
    ]


def doc_code_evidence_loop_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    prefix = f"human_agent_deepening://{codebase_id}/doc_code_evidence_loop"
    return [
        {"type": "evidence_loop", "artifact_ref": f"{prefix}/evidence_loop.json"},
        {"type": "decision_history", "artifact_ref": f"{prefix}/decision_history.jsonl"},
        {"type": "rule_effect", "artifact_ref": f"{prefix}/rule_effect.json"},
        {"type": "evidence_loop_report", "artifact_ref": f"{prefix}/evidence_loop_report.md"},
    ]


def regression_expansion_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    prefix = f"human_agent_deepening://{codebase_id}/regression_expansion"
    return [
        {"type": "expanded_matrix", "artifact_ref": f"{prefix}/expanded_matrix.json"},
        {"type": "artifact_diff", "artifact_ref": f"{prefix}/artifact_diff.json"},
        {"type": "failure_diagnosis", "artifact_ref": f"{prefix}/failure_diagnosis.json"},
        {"type": "regression_report", "artifact_ref": f"{prefix}/regression_report.md"},
    ]


def restore_ux_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    prefix = f"human_agent_deepening://{codebase_id}/restore_ux"
    return [
        {"type": "restore_checklist", "artifact_ref": f"{prefix}/restore_checklist.md"},
        {"type": "troubleshooting", "artifact_ref": f"{prefix}/troubleshooting.md"},
        {"type": "onboarding_report", "artifact_ref": f"{prefix}/onboarding_report.json"},
    ]


def write_human_portal_deepening(
    workspace: Path,
    codebase_id: str,
    project_story: dict[str, Any],
    risk_priority: dict[str, Any],
    reading_path: dict[str, Any],
    chart_audit: dict[str, Any],
    html: str,
) -> None:
    write_json(project_story_path(workspace, codebase_id), project_story)
    write_json(risk_priority_path(workspace, codebase_id), risk_priority)
    write_json(reading_path_path(workspace, codebase_id), reading_path)
    write_json(chart_audit_path(workspace, codebase_id), chart_audit)
    html_path = portal_v2_html_path(workspace, codebase_id)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")


def write_agent_task_workflow(
    workspace: Path,
    codebase_id: str,
    task_id: str,
    workflow_bundle: dict[str, Any],
    stop_conditions: dict[str, Any],
    suggested_tests: dict[str, Any],
    markdown: str,
) -> None:
    write_json(workflow_bundle_path(workspace, codebase_id, task_id), workflow_bundle)
    write_json(stop_conditions_path(workspace, codebase_id, task_id), stop_conditions)
    write_json(task_workflow_suggested_tests_path(workspace, codebase_id, task_id), suggested_tests)
    markdown_path = task_workflow_markdown_path(workspace, codebase_id, task_id)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown, encoding="utf-8")


def write_doc_code_evidence_loop(
    workspace: Path,
    codebase_id: str,
    evidence_loop: dict[str, Any],
    decisions: list[dict[str, Any]],
    rule_effect: dict[str, Any],
    report: str,
) -> None:
    write_json(evidence_loop_path(workspace, codebase_id), evidence_loop)
    history_path = decision_history_path(workspace, codebase_id)
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text("".join(f"{__import__('json').dumps(row, ensure_ascii=False, sort_keys=True)}\n" for row in decisions), encoding="utf-8")
    write_json(rule_effect_path(workspace, codebase_id), rule_effect)
    report_path = evidence_loop_report_path(workspace, codebase_id)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")


def write_regression_expansion(
    workspace: Path,
    codebase_id: str,
    expanded_matrix: dict[str, Any],
    artifact_diff: dict[str, Any],
    failure_diagnosis: dict[str, Any],
    report: str,
) -> None:
    write_json(expanded_matrix_path(workspace, codebase_id), expanded_matrix)
    write_json(artifact_diff_path(workspace, codebase_id), artifact_diff)
    write_json(failure_diagnosis_path(workspace, codebase_id), failure_diagnosis)
    report_path = regression_report_path(workspace, codebase_id)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")


def write_restore_ux(workspace: Path, codebase_id: str, checklist: str, troubleshooting: str, onboarding_report: dict[str, Any]) -> None:
    checklist_path = restore_checklist_path(workspace, codebase_id)
    checklist_path.parent.mkdir(parents=True, exist_ok=True)
    checklist_path.write_text(checklist, encoding="utf-8")
    troubleshooting_path(workspace, codebase_id).write_text(troubleshooting, encoding="utf-8")
    write_json(onboarding_report_path(workspace, codebase_id), onboarding_report)


def read_project_story(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(project_story_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("HUMAN_PORTAL_DEEPENING_NOT_BUILT")
    return payload


def read_risk_priority(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(risk_priority_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("HUMAN_PORTAL_DEEPENING_NOT_BUILT")
    return payload


def read_reading_path(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(reading_path_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("HUMAN_PORTAL_DEEPENING_NOT_BUILT")
    return payload


def read_chart_audit(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(chart_audit_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("HUMAN_PORTAL_DEEPENING_NOT_BUILT")
    return payload


def read_portal_v2_html(workspace: Path, codebase_id: str) -> str:
    path = portal_v2_html_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("HUMAN_PORTAL_DEEPENING_NOT_BUILT")
    return path.read_text(encoding="utf-8")


def read_workflow_bundle(workspace: Path, codebase_id: str, task_id: str) -> dict[str, Any]:
    payload = read_json(workflow_bundle_path(workspace, codebase_id, task_id), None)
    if not payload:
        raise FileNotFoundError("AGENT_TASK_WORKFLOW_NOT_BUILT")
    return payload


def read_stop_conditions(workspace: Path, codebase_id: str, task_id: str) -> dict[str, Any]:
    payload = read_json(stop_conditions_path(workspace, codebase_id, task_id), None)
    if not payload:
        raise FileNotFoundError("AGENT_TASK_WORKFLOW_NOT_BUILT")
    return payload


def read_task_workflow_suggested_tests(workspace: Path, codebase_id: str, task_id: str) -> dict[str, Any]:
    payload = read_json(task_workflow_suggested_tests_path(workspace, codebase_id, task_id), None)
    if not payload:
        raise FileNotFoundError("AGENT_TASK_WORKFLOW_NOT_BUILT")
    return payload


def read_task_workflow_markdown(workspace: Path, codebase_id: str, task_id: str) -> str:
    path = task_workflow_markdown_path(workspace, codebase_id, task_id)
    if not path.exists():
        raise FileNotFoundError("AGENT_TASK_WORKFLOW_NOT_BUILT")
    return path.read_text(encoding="utf-8")


def read_evidence_loop(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(evidence_loop_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("DOC_CODE_EVIDENCE_LOOP_NOT_BUILT")
    return payload


def read_decision_history(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    path = decision_history_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("DOC_CODE_EVIDENCE_LOOP_NOT_BUILT")
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(__import__("json").loads(line))
    return rows


def read_rule_effect(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(rule_effect_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("DOC_CODE_EVIDENCE_LOOP_NOT_BUILT")
    return payload


def read_evidence_loop_report(workspace: Path, codebase_id: str) -> str:
    path = evidence_loop_report_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("DOC_CODE_EVIDENCE_LOOP_NOT_BUILT")
    return path.read_text(encoding="utf-8")


def read_expanded_matrix(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(expanded_matrix_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("REGRESSION_EXPANSION_NOT_BUILT")
    return payload


def read_artifact_diff(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(artifact_diff_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("REGRESSION_EXPANSION_NOT_BUILT")
    return payload


def read_failure_diagnosis(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(failure_diagnosis_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("REGRESSION_EXPANSION_NOT_BUILT")
    return payload


def read_regression_report(workspace: Path, codebase_id: str) -> str:
    path = regression_report_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("REGRESSION_EXPANSION_NOT_BUILT")
    return path.read_text(encoding="utf-8")


def read_restore_checklist(workspace: Path, codebase_id: str) -> str:
    path = restore_checklist_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("RESTORE_UX_NOT_BUILT")
    return path.read_text(encoding="utf-8")


def read_troubleshooting(workspace: Path, codebase_id: str) -> str:
    path = troubleshooting_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("RESTORE_UX_NOT_BUILT")
    return path.read_text(encoding="utf-8")


def read_onboarding_report(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(onboarding_report_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("RESTORE_UX_NOT_BUILT")
    return payload
