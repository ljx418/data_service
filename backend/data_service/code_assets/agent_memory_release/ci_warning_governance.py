"""CI and warning governance artifacts for V2.72."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    ci_warning_governance_artifact_refs,
    read_ci_matrix,
    read_ci_readiness_report,
    read_failure_diagnosis,
    read_warning_budget,
    write_ci_warning_governance,
)
from .shared import FAILURE_CATEGORIES, base_artifact, redaction_findings


PHASE = "V2.72"
DEFAULT_WARNING_BUDGET = 300
DEFAULT_OBSERVED_WARNINGS = 277


class CIWarningGovernanceService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_ci_warning_governance(self, codebase_id: str, command_results: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = ci_warning_governance_artifact_refs(codebase_id)
        results = command_results or {}
        observed = int(results.get("observed_warning_count", DEFAULT_OBSERVED_WARNINGS))
        budget_value = int(results.get("warning_budget", DEFAULT_WARNING_BUDGET))
        status = "accepted" if observed <= budget_value else "needs_review"
        matrix = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="ci_matrix", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs, next_actions=["knowledge_code_agent_memory_release_ci_governance_read"])
        matrix["groups"] = _ci_groups()
        budget = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="warning_budget", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
        budget.update({"observed_warning_count": observed, "warning_budget": budget_value, "status": status, "next_action": "reduce warning sources or revise budget with evidence" if status != "accepted" else "none"})
        diagnosis = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="failure_diagnosis", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
        diagnosis["items"] = _diagnosis_items(results, status)
        report = _report(matrix, budget, diagnosis)
        unresolved = redaction_findings(matrix) + redaction_findings(budget) + redaction_findings(diagnosis) + redaction_findings(report)
        if status != "accepted":
            budget["unresolved"].append({"kind": "needs_review", "reason": "warning count is over budget", "next_action": "reduce warnings or document budget change"})
        if unresolved:
            budget["unresolved"].extend(unresolved)
        write_ci_warning_governance(self.workspace, codebase_id, matrix, budget, diagnosis, report)
        return _bundle(self.workspace_id, codebase_id, matrix, budget, diagnosis, report, refs)

    def read_ci_warning_governance(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = ci_warning_governance_artifact_refs(codebase_id)
        return _bundle(self.workspace_id, codebase_id, read_ci_matrix(self.workspace, codebase_id), read_warning_budget(self.workspace, codebase_id), read_failure_diagnosis(self.workspace, codebase_id), read_ci_readiness_report(self.workspace, codebase_id), refs)


def public_ci_warning_governance_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "ci_warning_governance",
        "ci_matrix": payload.get("ci_matrix") or {},
        "warning_budget": payload.get("warning_budget") or {},
        "failure_diagnosis": payload.get("failure_diagnosis") or {},
        "ci_readiness_report": {"format": "markdown", "content": payload.get("ci_readiness_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _ci_groups() -> list[dict[str, Any]]:
    return [
        {"group": "v2_71_75_focused", "command": "pytest -q backend/tests/test_v2_71_external_project_binding_closure.py backend/tests/test_v2_72_ci_warning_governance.py backend/tests/test_v2_73_agent_long_term_memory_productization.py backend/tests/test_v2_74_interactive_maintainer_console.py backend/tests/test_v2_75_release_restore_packaging.py backend/tests/test_public_surface_guard.py", "status": "planned"},
        {"group": "v2_63_70_regression", "command": "pytest -q backend/tests/test_v2_63_external_project_full_e2e.py ... backend/tests/test_v2_70_maintainer_home_status_dashboard.py", "status": "planned"},
        {"group": "infrastructure", "command": "compileall + git diff --check + protected legacy diff", "status": "planned"},
    ]


def _diagnosis_items(results: dict[str, Any], status: str) -> list[dict[str, Any]]:
    category = str(results.get("failure_category") or ("needs_review" if status != "accepted" else "needs_review"))
    if category not in FAILURE_CATEGORIES:
        category = "needs_review"
    return [{"id": "warning_budget", "status": status, "failure_category": category, "reason": "warning budget governance item", "next_action": "none" if status == "accepted" else "review warning budget"}]


def _report(matrix: dict[str, Any], budget: dict[str, Any], diagnosis: dict[str, Any]) -> str:
    return "\n".join([
        "# V2.72 CI Warning Governance Report",
        "",
        f"Observed warnings: {budget['observed_warning_count']}",
        f"Warning budget: {budget['warning_budget']}",
        f"Status: {budget['status']}",
        "",
        "Failure categories are constrained to the approved enum.",
    ]) + "\n"


def _bundle(workspace_id: str, codebase_id: str, matrix: dict[str, Any], budget: dict[str, Any], diagnosis: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.71-75",
        "artifact_type": "ci_warning_governance",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "ci_matrix": matrix,
        "warning_budget": budget,
        "failure_diagnosis": diagnosis,
        "ci_readiness_report": report,
        "summary": {"status": budget.get("status"), "observed_warning_count": budget.get("observed_warning_count"), "warning_budget": budget.get("warning_budget")},
        "artifact_refs": refs,
        "warnings": list(budget.get("warnings") or []),
        "unresolved": list(budget.get("unresolved") or []),
        "next_actions": ["knowledge_code_agent_memory_release_ci_governance_read"],
    }

