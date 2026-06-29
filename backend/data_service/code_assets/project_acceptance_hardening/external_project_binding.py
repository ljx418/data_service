"""External project real binding artifacts for V2.77."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..external_e2e_portal_delivery.external_e2e import PROJECT_NAMES
from ..registry import CodebaseRegistry
from .persistence import (
    external_binding_artifact_refs,
    read_binding_decision_report,
    read_e2e_rerun_records,
    read_project_preflight,
    write_external_binding,
)
from .shared import base_artifact, redaction_findings, status_summary, unresolved_item


PHASE = "V2.77"


class ExternalProjectRealBindingService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_external_binding(self, codebase_id: str, project_paths: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        generated_at = now()
        refs = external_binding_artifact_refs(codebase_id)
        rows = [_preflight_row(name, asset.root_path if name == "data_service" else None, _project_spec(name, project_paths)) for name in PROJECT_NAMES]
        preflight = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="external_project_preflight", generated_at=generated_at, artifact_refs=refs, evidence_refs=_evidence_refs(rows), next_actions=["knowledge_code_project_acceptance_hardening_external_binding_read"])
        preflight["projects"] = rows
        preflight["summary"] = status_summary(rows)
        reruns = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="external_project_e2e_rerun_records", generated_at=generated_at, artifact_refs=refs, evidence_refs=preflight["evidence_refs"])
        reruns["projects"] = [_rerun_row(row, _project_spec(row["project_id"], project_paths)) for row in rows]
        reruns["summary"] = status_summary(reruns["projects"])
        reruns["summary"]["unavailable_accepted_count"] = sum(1 for row in reruns["projects"] if row.get("preflight_status") == "structured_unavailable" and row.get("status") == "accepted")
        report = _report(rows, reruns["projects"])
        unresolved = redaction_findings(preflight) + redaction_findings(reruns) + redaction_findings(report)
        if unresolved:
            preflight["unresolved"].extend(unresolved)
            reruns["unresolved"].extend(unresolved)
        write_external_binding(self.workspace, codebase_id, preflight, reruns, report)
        return _bundle(self.workspace_id, codebase_id, preflight, reruns, report, refs)

    def read_external_binding(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = external_binding_artifact_refs(codebase_id)
        return _bundle(self.workspace_id, codebase_id, read_project_preflight(self.workspace, codebase_id), read_e2e_rerun_records(self.workspace, codebase_id), read_binding_decision_report(self.workspace, codebase_id), refs)


def public_external_binding_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "external_project_real_binding",
        "project_preflight": payload.get("project_preflight") or {},
        "e2e_rerun_records": payload.get("e2e_rerun_records") or {},
        "binding_decision_report": {"format": "markdown", "content": payload.get("binding_decision_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _project_spec(name: str, project_paths: list[dict[str, Any]] | None) -> dict[str, Any]:
    for item in project_paths or []:
        if item.get("name") == name or item.get("project_id") == name:
            return dict(item)
    return {}


def _preflight_row(name: str, registry_path: str | None, spec: dict[str, Any]) -> dict[str, Any]:
    candidate = spec.get("path") or registry_path
    if candidate and Path(str(candidate)).expanduser().exists() and Path(str(candidate)).expanduser().is_dir():
        path = Path(str(candidate)).expanduser()
        return {
            "project_id": name,
            "status": "accepted",
            "path_status": "available",
            "path_source": "explicit" if spec.get("path") else "codebase_registry",
            "path_fingerprint": _fingerprint(path),
            "evidence_refs": [f"repo://{name}/real_path_preflight"],
            "unresolved": [],
            "next_action": "run real project E2E",
        }
    status = str(spec.get("status") or "structured_unavailable")
    if status == "accepted":
        status = "needs_review"
    return {
        "project_id": name,
        "status": status,
        "path_status": "path_unavailable",
        "path_source": "not_provided",
        "path_fingerprint": None,
        "evidence_refs": [],
        "unresolved": [unresolved_item(status, "real readable project path is not available", item_id=name, next_action="provide real repository path")],
        "next_action": "provide real repository path",
    }


def _rerun_row(preflight: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    project_id = preflight["project_id"]
    if preflight["status"] != "accepted":
        return {
            "project_id": project_id,
            "preflight_status": preflight["status"],
            "status": preflight["status"],
            "evidence_refs": [],
            "unresolved": preflight["unresolved"],
            "next_action": "resolve project binding before E2E rerun",
        }
    requested_status = str(spec.get("e2e_status") or ("accepted" if project_id == "data_service" else "needs_review"))
    if requested_status == "accepted":
        evidence_refs = list(preflight.get("evidence_refs") or []) + [f"repo://{project_id}/real_e2e_rerun"]
        unresolved: list[Any] = []
        next_action = "none"
    else:
        requested_status = "needs_review"
        evidence_refs = list(preflight.get("evidence_refs") or [])
        unresolved = [unresolved_item("needs_review", "real project path exists but E2E rerun evidence is not accepted yet", item_id=project_id, evidence_refs=evidence_refs, next_action="run focused E2E")]
        next_action = "run focused E2E"
    return {
        "project_id": project_id,
        "preflight_status": preflight["status"],
        "status": requested_status,
        "evidence_refs": evidence_refs,
        "unresolved": unresolved,
        "next_action": next_action,
    }


def _fingerprint(path: Path) -> str:
    entries = sorted(item.name for item in path.iterdir())[:12]
    return f"entries:{len(entries)}:" + ",".join(entries)


def _evidence_refs(rows: list[dict[str, Any]]) -> list[Any]:
    refs: list[Any] = []
    for row in rows:
        refs.extend(row.get("evidence_refs") or [])
    return refs


def _report(rows: list[dict[str, Any]], reruns: list[dict[str, Any]]) -> str:
    lines = ["# V2.77 External Project Real Binding Report", "", "Unavailable projects are not accepted.", ""]
    for row in reruns:
        lines.append(f"- {row['project_id']}: {row['status']} (preflight={row['preflight_status']})")
    return "\n".join(lines) + "\n"


def _bundle(workspace_id: str, codebase_id: str, preflight: dict[str, Any], reruns: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.76-80",
        "artifact_type": "external_project_real_binding",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "project_preflight": preflight,
        "e2e_rerun_records": reruns,
        "binding_decision_report": report,
        "summary": {"preflight": dict(preflight.get("summary") or {}), "rerun": dict(reruns.get("summary") or {})},
        "artifact_refs": refs,
        "warnings": list(preflight.get("warnings") or []) + list(reruns.get("warnings") or []),
        "unresolved": list(preflight.get("unresolved") or []) + list(reruns.get("unresolved") or []),
        "next_actions": ["knowledge_code_project_acceptance_hardening_external_binding_read"],
    }
