"""Acceptance matrix reconciliation artifacts for V2.76."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..agent_memory_release.persistence import (
    read_acceptance_state,
    read_ci_matrix,
    read_console_status_panels,
    read_project_binding_closure,
    read_release_manifest,
)
from ..registry import CodebaseRegistry
from .persistence import (
    matrix_reconciliation_artifact_refs,
    read_reconciled_matrix,
    read_reconciliation_report,
    read_status_diff,
    write_matrix_reconciliation,
)
from .shared import base_artifact, redaction_findings, status_summary, unresolved_item


PHASE = "V2.76"


class AcceptanceMatrixReconciliationService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_reconciliation(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = matrix_reconciliation_artifact_refs(codebase_id)
        rows = _rows(self.workspace, codebase_id)
        matrix = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="reconciled_acceptance_matrix",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=_evidence_refs(rows),
            next_actions=["knowledge_code_project_acceptance_hardening_matrix_read"],
        )
        matrix["rows"] = rows
        matrix["summary"] = status_summary(rows)
        diff = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="acceptance_status_diff",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=matrix["evidence_refs"],
        )
        diff["items"] = [_diff_item(row) for row in rows if row.get("status") != row.get("documented_status")]
        diff["summary"] = {"diff_count": len(diff["items"]), "docs_only_accepted_count": sum(1 for item in diff["items"] if item.get("false_green_risk") == "docs_only_acceptance")}
        report = _report(matrix, diff)
        unresolved = redaction_findings(matrix) + redaction_findings(diff) + redaction_findings(report)
        if unresolved:
            matrix["unresolved"].extend(unresolved)
            diff["unresolved"].extend(unresolved)
        write_matrix_reconciliation(self.workspace, codebase_id, matrix, diff, report)
        return _bundle(self.workspace_id, codebase_id, matrix, diff, report, refs)

    def read_reconciliation(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = matrix_reconciliation_artifact_refs(codebase_id)
        return _bundle(self.workspace_id, codebase_id, read_reconciled_matrix(self.workspace, codebase_id), read_status_diff(self.workspace, codebase_id), read_reconciliation_report(self.workspace, codebase_id), refs)


def public_matrix_reconciliation_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "acceptance_matrix_reconciliation",
        "reconciled_matrix": payload.get("reconciled_matrix") or {},
        "status_diff": payload.get("status_diff") or {},
        "reconciliation_report": {"format": "markdown", "content": payload.get("reconciliation_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _rows(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    specs = [
        ("external_project_closure", "External project closure", read_project_binding_closure, "agent_memory_release://{codebase_id}/external_project_closure/project_binding_closure.json"),
        ("ci_warning_governance", "CI warning governance", read_ci_matrix, "agent_memory_release://{codebase_id}/ci_warning_governance/ci_matrix.json"),
        ("agent_memory", "Agent long-term memory", read_acceptance_state, "agent_memory_release://{codebase_id}/agent_memory/acceptance_state.json"),
        ("interactive_console", "Interactive maintainer console", read_console_status_panels, "agent_memory_release://{codebase_id}/interactive_console/status_panels.json"),
        ("release_restore", "Release restore packaging", read_release_manifest, "agent_memory_release://{codebase_id}/release_restore/release_manifest.json"),
    ]
    rows: list[dict[str, Any]] = []
    for capability_id, title, reader, ref_template in specs:
        artifact_ref = ref_template.format(codebase_id=codebase_id)
        try:
            source = reader(workspace, codebase_id)
            source_status = _source_status(source)
            rows.append(
                {
                    "capability_id": capability_id,
                    "title": title,
                    "documented_status": "planned",
                    "status": source_status,
                    "evidence_refs": [artifact_ref],
                    "artifact_ref": artifact_ref,
                    "unresolved": list(source.get("unresolved") or []) if isinstance(source, dict) else [],
                    "decision_basis": "persisted artifact evidence",
                    "next_action": "none" if source_status == "accepted" else "review upstream artifact status",
                }
            )
        except FileNotFoundError:
            rows.append(
                {
                    "capability_id": capability_id,
                    "title": title,
                    "documented_status": "planned",
                    "status": "needs_review",
                    "evidence_refs": [],
                    "artifact_ref": artifact_ref,
                    "unresolved": [unresolved_item("needs_review", "expected persisted artifact is missing", item_id=capability_id, next_action="build upstream phase artifact")],
                    "decision_basis": "missing artifact, not documentation claim",
                    "next_action": "build upstream phase artifact",
                }
            )
    return rows


def _source_status(source: dict[str, Any]) -> str:
    for key in ("readiness_status", "overall_status", "status"):
        if source.get(key):
            return str(source[key])
    if source.get("summary", {}).get("stage_status"):
        return str(source["summary"]["stage_status"])
    if source.get("projects"):
        statuses = {str(row.get("status")) for row in source["projects"]}
        return "accepted" if statuses == {"accepted"} else "needs_review"
    return "accepted"


def _evidence_refs(rows: list[dict[str, Any]]) -> list[Any]:
    refs: list[Any] = []
    for row in rows:
        refs.extend(row.get("evidence_refs") or [])
    return refs


def _diff_item(row: dict[str, Any]) -> dict[str, Any]:
    risk = "none"
    if row.get("documented_status") == "accepted" and not row.get("evidence_refs"):
        risk = "docs_only_acceptance"
    if row.get("documented_status") == "planned" and row.get("status") == "accepted":
        risk = "documentation_lag"
    return {
        "capability_id": row["capability_id"],
        "documented_status": row.get("documented_status"),
        "evidence_status": row.get("status"),
        "false_green_risk": risk,
        "evidence_refs": list(row.get("evidence_refs") or []),
        "next_action": row.get("next_action"),
    }


def _report(matrix: dict[str, Any], diff: dict[str, Any]) -> str:
    lines = ["# V2.76 Acceptance Matrix Reconciliation Report", "", "Persisted artifacts are treated as evidence. Documentation claims are not code facts.", ""]
    lines.append(f"Rows: {len(matrix.get('rows') or [])}")
    lines.append(f"Status diffs: {len(diff.get('items') or [])}")
    lines.append("")
    for row in matrix.get("rows") or []:
        lines.append(f"- {row['capability_id']}: {row['status']} (documented={row['documented_status']})")
    lines.append("")
    lines.append("`needs_review`, `structured_unavailable`, and `structured_blocker` are preserved.")
    return "\n".join(lines) + "\n"


def _bundle(workspace_id: str, codebase_id: str, matrix: dict[str, Any], diff: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.76-80",
        "artifact_type": "acceptance_matrix_reconciliation",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "reconciled_matrix": matrix,
        "status_diff": diff,
        "reconciliation_report": report,
        "summary": dict(matrix.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(matrix.get("warnings") or []) + list(diff.get("warnings") or []),
        "unresolved": list(matrix.get("unresolved") or []) + list(diff.get("unresolved") or []),
        "next_actions": ["knowledge_code_project_acceptance_hardening_matrix_read"],
    }
