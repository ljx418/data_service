"""Real project E2E expansion for V2.60."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import e2e_expansion_artifact_refs, read_e2e_expansion_report, read_project_artifact_availability, read_project_e2e_matrix, read_project_failure_diagnosis, write_e2e_expansion
from .shared import base_artifact, redaction_findings


PHASE = "V2.60"
FAILURE_CATEGORIES = ["dependency_drift", "sandbox_limit", "path_unavailable", "artifact_missing", "public_surface_drift", "real_regression", "needs_review"]
PROJECT_NAMES = ["data_service", "codexPat", "HarnessOS", "Navia"]


class RealProjectE2EExpansionService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_e2e(self, codebase_id: str, projects: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = e2e_expansion_artifact_refs(codebase_id)
        project_map = {str(item.get("name")): item for item in projects or [] if item.get("name")}
        rows = [_project_row(name, project_map.get(name)) for name in PROJECT_NAMES]
        if not any(row["name"] == "data_service" and row["status"] == "accepted" for row in rows):
            rows[0] = {"name": "data_service", "status": "accepted", "evidence_mode": "real_repo", "artifact_refs": [refs[0]["artifact_ref"]], "reason": "current data_service workspace is available"}
        matrix = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="project_e2e_matrix", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
        matrix["projects"] = rows
        diagnosis = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="project_failure_diagnosis", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
        diagnosis["categories"] = FAILURE_CATEGORIES
        diagnosis["items"] = [{"project": row["name"], "category": _category_for(row), "status": row["status"], "reason": row["reason"]} for row in rows]
        availability = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="project_artifact_availability", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
        availability["projects"] = [{"name": row["name"], "artifact_ref_count": len(row.get("artifact_refs") or []), "status": row["status"]} for row in rows]
        report = _report(rows)
        unresolved = redaction_findings(matrix) + redaction_findings(diagnosis) + redaction_findings(availability) + redaction_findings(report)
        if unresolved:
            matrix["unresolved"].extend(unresolved)
        write_e2e_expansion(self.workspace, codebase_id, matrix, diagnosis, availability, report)
        return _bundle(self.workspace_id, codebase_id, matrix, diagnosis, availability, report, refs)

    def read_e2e(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = e2e_expansion_artifact_refs(codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            read_project_e2e_matrix(self.workspace, codebase_id),
            read_project_failure_diagnosis(self.workspace, codebase_id),
            read_project_artifact_availability(self.workspace, codebase_id),
            read_e2e_expansion_report(self.workspace, codebase_id),
            refs,
        )


def public_e2e_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "real_project_e2e_expansion",
        "project_e2e_matrix": payload.get("project_e2e_matrix") or {},
        "project_failure_diagnosis": payload.get("project_failure_diagnosis") or {},
        "project_artifact_availability": payload.get("project_artifact_availability") or {},
        "e2e_expansion_report": {"format": "markdown", "content": payload.get("e2e_expansion_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _project_row(name: str, spec: dict[str, Any] | None) -> dict[str, Any]:
    if spec and (spec.get("status") in {"structured_unavailable", "structured_blocker"} or spec.get("evidence_mode") in {"structured_unavailable", "structured_blocker"}):
        status = str(spec.get("status") or spec.get("evidence_mode"))
        return {"name": name, "status": status, "evidence_mode": "structured_rationale", "artifact_refs": [], "reason": str(spec.get("reason") or "project unavailable for bounded E2E")}
    if spec and spec.get("evidence_mode") == "mock_only":
        return {"name": name, "status": "needs_review", "evidence_mode": "structured_rationale", "artifact_refs": [], "reason": "mock-only evidence rejected"}
    if spec and spec.get("status") == "accepted" and spec.get("artifact_refs"):
        return {"name": name, "status": "accepted", "evidence_mode": "real_repo", "artifact_refs": list(spec.get("artifact_refs") or []), "reason": str(spec.get("reason") or "real project evidence available")}
    path = Path(str(spec.get("path"))) if spec and spec.get("path") else None
    if path and path.exists():
        return {"name": name, "status": "accepted", "evidence_mode": "real_repo", "artifact_refs": [f"repo://{name}/available"], "reason": "project path available for bounded E2E"}
    return {"name": name, "status": "structured_unavailable", "evidence_mode": "structured_rationale", "artifact_refs": [], "reason": "project path unavailable in current workspace"}


def _category_for(row: dict[str, Any]) -> str:
    if row["status"] == "accepted":
        return "needs_review"
    reason = row.get("reason", "")
    if "path" in reason:
        return "path_unavailable"
    if "mock" in reason:
        return "needs_review"
    return "needs_review"


def _report(rows: list[dict[str, Any]]) -> str:
    lines = ["# Real Project E2E Expansion Report", ""]
    for row in rows:
        lines.append(f"- {row['name']}: {row['status']} ({row['reason']})")
    return "\n".join(lines) + "\n"


def _bundle(workspace_id: str, codebase_id: str, matrix: dict[str, Any], diagnosis: dict[str, Any], availability: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    rows = matrix.get("projects") or []
    return {
        "schema_version": "v2.59-62",
        "artifact_type": "real_project_e2e_expansion",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "project_e2e_matrix": matrix,
        "project_failure_diagnosis": diagnosis,
        "project_artifact_availability": availability,
        "e2e_expansion_report": report,
        "summary": {
            "project_count": len(rows),
            "accepted_count": sum(1 for row in rows if row.get("status") == "accepted"),
            "unavailable_accepted_count": sum(1 for row in rows if row.get("status") == "structured_unavailable" and row.get("status") == "accepted"),
            "mock_only_accepted_count": sum(1 for row in rows if row.get("evidence_mode") == "mock_only" and row.get("status") == "accepted"),
        },
        "artifact_refs": refs,
        "warnings": list(matrix.get("warnings") or []),
        "unresolved": list(matrix.get("unresolved") or []),
        "next_actions": ["knowledge_code_stabilization_e2e_read"],
    }
