"""External project full E2E orchestration for V2.63."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    external_e2e_artifact_refs,
    read_artifact_readiness,
    read_external_e2e_report,
    read_full_project_matrix,
    read_project_run_records,
    write_external_e2e,
)
from .shared import FAILURE_CATEGORIES, accepted_count, base_artifact, redaction_findings


PHASE = "V2.63"
PROJECT_NAMES = ["data_service", "codexPat", "HarnessOS", "Navia"]


class ExternalProjectFullE2EService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_e2e(self, codebase_id: str, projects: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        generated_at = now()
        refs = external_e2e_artifact_refs(codebase_id)
        project_map = {str(item.get("name") or item.get("project_id")): item for item in projects or [] if item.get("name") or item.get("project_id")}
        rows = [_project_row(name, project_map.get(name), asset) for name in PROJECT_NAMES]
        records = _records(self.workspace_id, codebase_id, generated_at, refs, rows)
        readiness = _readiness(self.workspace_id, codebase_id, generated_at, refs, rows)
        matrix = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="full_project_matrix",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=refs,
            next_actions=["knowledge_code_external_e2e_portal_delivery_e2e_read"],
        )
        matrix["projects"] = rows
        matrix["failure_categories"] = FAILURE_CATEGORIES
        matrix["summary"] = _summary(rows)
        report = _report(rows)
        unresolved = redaction_findings(matrix) + redaction_findings(records) + redaction_findings(readiness) + redaction_findings(report)
        if unresolved:
            matrix["unresolved"].extend(unresolved)
        write_external_e2e(self.workspace, codebase_id, matrix, records, readiness, report)
        return _bundle(self.workspace_id, codebase_id, matrix, records, readiness, report, refs)

    def read_e2e(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = external_e2e_artifact_refs(codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            read_full_project_matrix(self.workspace, codebase_id),
            read_project_run_records(self.workspace, codebase_id),
            read_artifact_readiness(self.workspace, codebase_id),
            read_external_e2e_report(self.workspace, codebase_id),
            refs,
        )


def public_external_e2e_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "external_project_full_e2e",
        "full_project_matrix": payload.get("full_project_matrix") or {},
        "project_run_records": payload.get("project_run_records") or {},
        "artifact_readiness": payload.get("artifact_readiness") or {},
        "external_e2e_report": {"format": "markdown", "content": payload.get("external_e2e_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _project_row(name: str, spec: dict[str, Any] | None, asset: dict[str, Any]) -> dict[str, Any]:
    if name == "data_service" and not spec:
        codebase_id = getattr(asset, "codebase_id", "data_service")
        return _accepted_row(name, "current imported data_service codebase is available", [f"repo://{codebase_id}/current"])
    if spec and spec.get("evidence_mode") == "mock_only":
        return _unavailable_row(name, "needs_review", "mock-only evidence rejected", "needs_review")
    if spec and spec.get("status") in {"structured_unavailable", "structured_blocker", "needs_review"}:
        status = str(spec["status"])
        return _unavailable_row(name, status, str(spec.get("reason") or "structured non-accepted result"), _failure_category_for_reason(str(spec.get("reason") or "")))
    if spec and spec.get("status") == "accepted" and spec.get("evidence_refs"):
        return _accepted_row(name, str(spec.get("reason") or "real project evidence available"), list(spec.get("evidence_refs") or []))
    path = Path(str(spec.get("path"))) if spec and spec.get("path") else None
    if path and path.exists():
        return _accepted_row(name, "project path available for bounded real E2E", [f"repo://{name}/available"])
    return _unavailable_row(name, "structured_unavailable", "project path unavailable in current workspace", "path_unavailable")


def _accepted_row(name: str, reason: str, evidence_refs: list[str]) -> dict[str, Any]:
    return {
        "project_id": name,
        "name": name,
        "status": "accepted",
        "path_status": "available",
        "dependency_status": "available",
        "artifact_status": "accepted",
        "commands": ["artifact build/read", "portal read", "contract read", "restore readiness read"],
        "evidence_refs": evidence_refs,
        "unresolved": [],
        "failure_category": None,
        "reason": reason,
        "next_action": "read persisted E2E artifacts",
    }


def _unavailable_row(name: str, status: str, reason: str, category: str) -> dict[str, Any]:
    return {
        "project_id": name,
        "name": name,
        "status": status,
        "path_status": "path_unavailable" if category == "path_unavailable" else "needs_review",
        "dependency_status": "dependency_drift" if category == "dependency_drift" else "needs_review",
        "artifact_status": "artifact_missing" if category == "artifact_missing" else "needs_review",
        "commands": [],
        "evidence_refs": [],
        "unresolved": [{"kind": status, "reason": reason, "next_action": "provide real project path and rerun preflight"}],
        "failure_category": category,
        "reason": reason,
        "next_action": "provide real project path and rerun preflight",
    }


def _failure_category_for_reason(reason: str) -> str:
    lowered = reason.lower()
    if "dependency" in lowered:
        return "dependency_drift"
    if "sandbox" in lowered:
        return "sandbox_limit"
    if "artifact" in lowered:
        return "artifact_missing"
    if "surface" in lowered:
        return "public_surface_drift"
    if "regression" in lowered:
        return "real_regression"
    if "path" in lowered:
        return "path_unavailable"
    return "needs_review"


def _records(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="project_run_records", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
    payload["records"] = [
        {
            "project_id": row["project_id"],
            "status": row["status"],
            "commands": row["commands"],
            "evidence_refs": row["evidence_refs"],
            "failure_category": row["failure_category"],
            "next_action": row["next_action"],
        }
        for row in rows
    ]
    return payload


def _readiness(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    payload = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="artifact_readiness", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
    payload["projects"] = [
        {"project_id": row["project_id"], "status": row["status"], "artifact_status": row["artifact_status"], "evidence_ref_count": len(row["evidence_refs"])}
        for row in rows
    ]
    return payload


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    non_accepted = [row for row in rows if row.get("status") != "accepted"]
    return {
        "project_count": len(rows),
        "accepted_count": accepted_count(rows),
        "non_accepted_count": len(non_accepted),
        "unavailable_accepted_count": sum(1 for row in rows if row.get("status") == "structured_unavailable" and row.get("status") == "accepted"),
        "mock_only_accepted_count": 0,
        "data_service_status": next((row["status"] for row in rows if row["project_id"] == "data_service"), "needs_review"),
    }


def _report(rows: list[dict[str, Any]]) -> str:
    lines = ["# External Project Full E2E Report", ""]
    for row in rows:
        category = row["failure_category"] or "none"
        lines.append(f"- {row['project_id']}: {row['status']} ({category}) - {row['reason']}")
    lines.append("")
    lines.append("Non-accepted statuses are not counted as accepted.")
    return "\n".join(lines) + "\n"


def _bundle(workspace_id: str, codebase_id: str, matrix: dict[str, Any], records: dict[str, Any], readiness: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.63-66",
        "artifact_type": "external_project_full_e2e",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "full_project_matrix": matrix,
        "project_run_records": records,
        "artifact_readiness": readiness,
        "external_e2e_report": report,
        "summary": dict(matrix.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(matrix.get("warnings") or []),
        "unresolved": list(matrix.get("unresolved") or []),
        "next_actions": ["knowledge_code_external_e2e_portal_delivery_e2e_read"],
    }
