"""External project binding closure for V2.71."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..external_e2e_portal_delivery.external_e2e import PROJECT_NAMES
from ..external_e2e_portal_delivery.persistence import read_full_project_matrix, read_path_binding_matrix
from ..registry import CodebaseRegistry
from .persistence import (
    external_project_closure_artifact_refs,
    read_e2e_closure_report,
    read_project_binding_closure,
    write_external_project_closure,
)
from .shared import base_artifact, redaction_findings, status_summary


PHASE = "V2.71"


class ExternalProjectClosureService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_external_project_closure(self, codebase_id: str, projects: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = external_project_closure_artifact_refs(codebase_id)
        path_binding = _try_read(lambda: read_path_binding_matrix(self.workspace, codebase_id))
        external_e2e = _try_read(lambda: read_full_project_matrix(self.workspace, codebase_id))
        rows = [_closure_row(name, projects or [], path_binding, external_e2e) for name in PROJECT_NAMES]
        closure = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="project_binding_closure",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=_evidence_refs(path_binding, external_e2e),
            next_actions=["knowledge_code_agent_memory_release_external_closure_read"],
        )
        closure["projects"] = rows
        summary = {"project_count": len(rows), **status_summary(rows)}
        summary["unavailable_accepted_count"] = sum(1 for row in rows if row.get("status") == "accepted" and row.get("path_status") == "path_unavailable")
        closure["summary"] = summary
        report = _report(rows, summary)
        unresolved = redaction_findings(closure) + redaction_findings(report)
        if unresolved:
            closure["unresolved"].extend(unresolved)
        write_external_project_closure(self.workspace, codebase_id, closure, report)
        return _bundle(self.workspace_id, codebase_id, closure, report, refs)

    def read_external_project_closure(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = external_project_closure_artifact_refs(codebase_id)
        return _bundle(self.workspace_id, codebase_id, read_project_binding_closure(self.workspace, codebase_id), read_e2e_closure_report(self.workspace, codebase_id), refs)


def public_external_project_closure_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "external_project_binding_closure",
        "project_binding_closure": payload.get("project_binding_closure") or {},
        "e2e_closure_report": {"format": "markdown", "content": payload.get("e2e_closure_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _try_read(reader) -> dict[str, Any]:
    try:
        return reader()
    except FileNotFoundError:
        return {}


def _evidence_refs(*sources: dict[str, Any]) -> list[Any]:
    refs: list[Any] = []
    for source in sources:
        refs.extend(source.get("artifact_refs") or [])
        refs.extend(source.get("evidence_refs") or [])
    return refs


def _project_row(source: dict[str, Any], name: str) -> dict[str, Any]:
    for row in source.get("projects") or []:
        if row.get("project_id") == name or row.get("name") == name:
            return row
    return {}


def _closure_row(name: str, overrides: list[dict[str, Any]], path_binding: dict[str, Any], external_e2e: dict[str, Any]) -> dict[str, Any]:
    override = next((item for item in overrides if item.get("project_id") == name or item.get("name") == name), {})
    binding = _project_row(path_binding, name)
    e2e = _project_row(external_e2e, name)
    evidence_refs = list(binding.get("evidence_refs") or []) + list(e2e.get("evidence_refs") or [])
    path_status = str(binding.get("path_status") or "path_unavailable")
    if override.get("status") in {"structured_unavailable", "structured_blocker", "needs_review"}:
        status = str(override["status"])
        reason = str(override.get("reason") or "override requires review")
    elif binding.get("status") == "accepted" and (name == "data_service" or e2e.get("status") == "accepted"):
        status = "accepted"
        reason = "real repository binding has evidence"
        if name == "data_service":
            evidence_refs = evidence_refs or ["repo://data_service/current_working_directory"]
    elif binding.get("status") in {"structured_blocker", "needs_review"}:
        status = str(binding["status"])
        reason = str(binding.get("reason") or f"{name} binding requires review")
    else:
        status = "structured_unavailable"
        reason = "real repository path is not available in current environment"
    unresolved = [] if status == "accepted" else [{"kind": status, "reason": reason, "next_action": "provide real repository path and rerun closure"}]
    return {
        "project_id": name,
        "status": status,
        "path_status": path_status,
        "e2e_status": str(e2e.get("status") or ("accepted" if status == "accepted" and name == "data_service" else "structured_unavailable")),
        "accepted": status == "accepted",
        "reason": reason,
        "evidence_refs": evidence_refs,
        "unresolved": unresolved,
        "next_action": "none" if status == "accepted" else "provide real repository path and rerun closure",
    }


def _report(rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    lines = ["# V2.71 External Project Binding Closure", ""]
    for row in rows:
        lines.append(f"- {row['project_id']}: {row['status']} - {row['reason']}")
    lines.extend(["", f"Accepted: {summary['accepted_count']}", f"Unavailable accepted: {summary['unavailable_accepted_count']}", "", "Unavailable projects are not counted as accepted."])
    return "\n".join(lines) + "\n"


def _bundle(workspace_id: str, codebase_id: str, closure: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.71-75",
        "artifact_type": "external_project_binding_closure",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "project_binding_closure": closure,
        "e2e_closure_report": report,
        "summary": dict(closure.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(closure.get("warnings") or []),
        "unresolved": list(closure.get("unresolved") or []),
        "next_actions": ["knowledge_code_agent_memory_release_external_closure_read"],
    }

