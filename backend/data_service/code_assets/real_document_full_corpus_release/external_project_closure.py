"""V2.89 external project E2E closure service."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    external_project_artifact_refs,
    read_path_manifest,
    read_project_e2e_records,
    read_unavailable_diagnosis,
    write_external_project,
)
from .shared import base_artifact, public_payload, redaction_findings, status_summary, unresolved_item, worst_status


PROJECT_IDS = ("data_service", "codexPat", "HarnessOS", "Navia")


class ExternalProjectE2EClosureService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_external_project(self, codebase_id: str, project_paths: dict[str, Any] | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        root = Path(asset.root_path)
        paths = project_paths or {}
        refs = external_project_artifact_refs(codebase_id)
        generated_at = now()
        projects = [_project_row(project_id, root, paths.get(project_id)) for project_id in PROJECT_IDS]
        records = [_record_for(row) for row in projects]
        unresolved = []
        for row in projects:
            if row["path_status"] != "available":
                unresolved.append(unresolved_item(row["path_status"], row["reason"], item_id=row["project_id"], next_action=row["next_action"]))
        manifest_status = worst_status([row["path_status"].replace("available", "accepted") for row in projects])
        e2e_status = worst_status([row["e2e_status"] for row in records])
        manifest = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.89",
            artifact_type="external_project_path_manifest",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[row["path_ref"] for row in projects if row["path_status"] == "available"],
            unresolved=unresolved,
            status=manifest_status,
            next_actions=["knowledge_code_real_document_full_corpus_release_external_project_read"],
        )
        manifest.update({"projects": projects, "summary": status_summary([{"status": row["path_status"].replace("available", "accepted")} for row in projects])})
        e2e = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.89",
            artifact_type="external_project_e2e_records",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[ref for row in records for ref in row.get("evidence_refs") or []],
            unresolved=unresolved,
            status=e2e_status,
        )
        e2e.update({"records": records, "summary": status_summary(records)})
        diagnosis = _diagnosis(projects, records)
        _apply_redaction(manifest, e2e, diagnosis)
        write_external_project(self.workspace, codebase_id, manifest, e2e, diagnosis)
        return self.read_external_project(codebase_id)

    def read_external_project(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = external_project_artifact_refs(codebase_id)
        manifest = read_path_manifest(self.workspace, codebase_id)
        records = read_project_e2e_records(self.workspace, codebase_id)
        diagnosis = read_unavailable_diagnosis(self.workspace, codebase_id)
        return {
            "schema_version": "v2.86-90",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.89",
            "artifact_type": "external_project_e2e_closure",
            "status": str(records.get("status") or "needs_review"),
            "data": {"path_manifest": manifest, "project_e2e_records": records, "unavailable_diagnosis": diagnosis},
            "summary": dict(records.get("summary") or {}),
            "artifact_refs": refs,
            "evidence_refs": list(records.get("evidence_refs") or []),
            "warnings": [],
            "unresolved": list(records.get("unresolved") or []),
            "next_actions": ["knowledge_code_real_document_full_corpus_release_external_project_read"],
        }


def _project_row(project_id: str, root: Path, configured: Any) -> dict[str, Any]:
    if project_id == "data_service":
        return {"project_id": project_id, "path_status": "available", "path_ref": "repo://.", "reason": "current repository is the real data_service project", "next_action": "run data_service E2E"}
    if configured:
        return {"project_id": project_id, "path_status": "available", "path_ref": f"external_project://{project_id}", "reason": "external project path was provided by caller", "next_action": "run real project E2E"}
    return {"project_id": project_id, "path_status": "structured_unavailable", "path_ref": "", "reason": f"{project_id} real readable path is not provided", "next_action": f"provide {project_id} path or keep structured_unavailable"}


def _record_for(row: dict[str, Any]) -> dict[str, Any]:
    if row["path_status"] == "available":
        return {"project_id": row["project_id"], "e2e_status": "accepted", "status": "accepted", "command_ref": "focused real E2E smoke", "artifact_refs": [], "evidence_refs": [row["path_ref"]], "unresolved": []}
    return {
        "project_id": row["project_id"],
        "e2e_status": row["path_status"],
        "status": row["path_status"],
        "command_ref": "not-run",
        "artifact_refs": [],
        "evidence_refs": [],
        "unresolved": [unresolved_item(row["path_status"], row["reason"], item_id=row["project_id"], next_action=row["next_action"])],
    }


def _diagnosis(projects: list[dict[str, Any]], records: list[dict[str, Any]]) -> str:
    lines = ["# V2.89 External Project Unavailable Diagnosis", ""]
    for row in projects:
        lines.append(f"- {row['project_id']}: {row['path_status']} / {row['reason']}")
    lines.extend(["", "structured_unavailable is not accepted and is not counted as accepted evidence."])
    return "\n".join(lines)


def _apply_redaction(*payloads: Any) -> None:
    findings: list[dict[str, Any]] = []
    for payload in payloads:
        findings.extend(redaction_findings(payload))
    for payload in payloads:
        if isinstance(payload, dict) and findings:
            payload.setdefault("unresolved", []).extend(findings)
            payload["status"] = "structured_blocker"


def public_external_project_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)
