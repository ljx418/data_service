"""External repository path binding for V2.67."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .external_e2e import PROJECT_NAMES
from .persistence import (
    path_binding_artifact_refs,
    read_path_binding_evidence,
    read_path_binding_matrix,
    read_path_binding_report,
    write_path_binding,
)
from .shared import base_artifact, redaction_findings


PHASE = "V2.67"
ENV_PREFIX = "DATA_SERVICE_EXTERNAL_PROJECT_"


class ExternalRepositoryPathBindingService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_path_binding(self, codebase_id: str, projects: list[dict[str, Any]] | None = None, search_roots: list[str] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = path_binding_artifact_refs(codebase_id)
        project_specs = {str(item.get("name") or item.get("project_id")): item for item in projects or [] if item.get("name") or item.get("project_id")}
        roots = [Path(item) for item in search_roots or [] if item]
        rows = [_binding_row(name, project_specs.get(name), roots) for name in PROJECT_NAMES]
        matrix = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="path_binding_matrix",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=refs,
            next_actions=["knowledge_code_external_e2e_portal_delivery_path_binding_read"],
        )
        matrix["projects"] = rows
        matrix["summary"] = _summary(rows)
        evidence = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="path_binding_evidence",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=refs,
        )
        evidence["items"] = [_evidence_row(row) for row in rows]
        report = _report(rows)
        unresolved = redaction_findings(matrix) + redaction_findings(evidence) + redaction_findings(report)
        if unresolved:
            matrix["unresolved"].extend(unresolved)
        write_path_binding(self.workspace, codebase_id, matrix, evidence, report)
        return _bundle(self.workspace_id, codebase_id, matrix, evidence, report, refs)

    def read_path_binding(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = path_binding_artifact_refs(codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            read_path_binding_matrix(self.workspace, codebase_id),
            read_path_binding_evidence(self.workspace, codebase_id),
            read_path_binding_report(self.workspace, codebase_id),
            refs,
        )


def public_path_binding_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "external_repository_path_binding",
        "path_binding_matrix": payload.get("path_binding_matrix") or {},
        "path_binding_evidence": payload.get("path_binding_evidence") or {},
        "path_binding_report": {"format": "markdown", "content": payload.get("path_binding_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _binding_row(name: str, spec: dict[str, Any] | None, search_roots: list[Path]) -> dict[str, Any]:
    candidate, source = _candidate_path(name, spec, search_roots)
    if candidate and candidate.exists() and candidate.is_dir():
        evidence_refs = [f"repo://{name}/path_binding_available"]
        return {
            "project_id": name,
            "status": "accepted",
            "path_status": "available",
            "path_source": source,
            "path_fingerprint": _fingerprint(candidate),
            "evidence_refs": evidence_refs,
            "unresolved": [],
            "reason": "real repository path is readable",
            "next_action": "run external E2E with this binding",
        }
    status = "structured_unavailable"
    reason = "real repository path is not available in current environment"
    if spec and spec.get("status") in {"needs_review", "structured_blocker", "structured_unavailable"}:
        status = str(spec["status"])
        reason = str(spec.get("reason") or reason)
    return {
        "project_id": name,
        "status": status,
        "path_status": "path_unavailable",
        "path_source": source,
        "path_fingerprint": None,
        "evidence_refs": [],
        "unresolved": [{"kind": status, "reason": reason, "next_action": "provide explicit real repository path"}],
        "reason": reason,
        "next_action": "provide explicit real repository path",
    }


def _candidate_path(name: str, spec: dict[str, Any] | None, search_roots: list[Path]) -> tuple[Path | None, str]:
    if spec and spec.get("path"):
        return Path(str(spec["path"])).expanduser(), "explicit"
    env_value = os.environ.get(f"{ENV_PREFIX}{_env_key(name)}")
    if env_value:
        return Path(env_value).expanduser(), "environment"
    for root in search_roots:
        candidate = root.expanduser() / name
        if candidate.exists():
            return candidate, "search_root"
    if name == "data_service":
        return Path.cwd(), "current_working_directory"
    return None, "not_provided"


def _env_key(name: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in name).upper()


def _fingerprint(path: Path) -> str:
    entries = sorted(item.name for item in path.iterdir())[:12]
    return f"entries:{len(entries)}:" + ",".join(entries)


def _evidence_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "project_id": row["project_id"],
        "status": row["status"],
        "path_status": row["path_status"],
        "path_source": row["path_source"],
        "path_fingerprint": row["path_fingerprint"],
        "evidence_refs": row["evidence_refs"],
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "project_count": len(rows),
        "accepted_count": sum(1 for row in rows if row.get("status") == "accepted"),
        "structured_unavailable_count": sum(1 for row in rows if row.get("status") == "structured_unavailable"),
        "needs_review_count": sum(1 for row in rows if row.get("status") == "needs_review"),
        "structured_blocker_count": sum(1 for row in rows if row.get("status") == "structured_blocker"),
    }


def _report(rows: list[dict[str, Any]]) -> str:
    lines = ["# External Repository Path Binding Report", ""]
    for row in rows:
        lines.append(f"- {row['project_id']}: {row['status']} ({row['path_status']}, source={row['path_source']}) - {row['reason']}")
    lines.append("")
    lines.append("Non-accepted path bindings must not be counted as real E2E acceptance.")
    return "\n".join(lines) + "\n"


def _bundle(workspace_id: str, codebase_id: str, matrix: dict[str, Any], evidence: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.63-70",
        "artifact_type": "external_repository_path_binding",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "path_binding_matrix": matrix,
        "path_binding_evidence": evidence,
        "path_binding_report": report,
        "summary": dict(matrix.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(matrix.get("warnings") or []),
        "unresolved": list(matrix.get("unresolved") or []),
        "next_actions": ["knowledge_code_external_e2e_portal_delivery_path_binding_read"],
    }
