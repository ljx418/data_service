"""Shared helpers for V2.76-V2.80 project acceptance hardening artifacts."""

from __future__ import annotations

import json
import re
from typing import Any


PROJECT_ACCEPTANCE_HARDENING_SCHEMA_VERSION = "v2.76-80"
STATUSES = {"accepted", "needs_review", "structured_unavailable", "structured_blocker", "out_of_scope"}
FAILURE_CATEGORIES = {
    "dependency_drift",
    "sandbox_limit",
    "artifact_missing",
    "public_surface_drift",
    "real_regression",
    "needs_review",
}
ABSOLUTE_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])(?:/(?:mnt|home|Users|tmp|var|etc|opt|root|workspaces?)(?:/[A-Za-z0-9._ -]+)+)|[A-Za-z]:\\\\")
SECRET_RE = re.compile(r"(?i)(api[_-]?key|authorization|bearer\s+[A-Za-z0-9._-]+|secret[_-](?:key|value)|(?:access|refresh|id)[_-]?token)")


def artifact_uri(codebase_id: str, section: str, filename: str) -> str:
    return f"project_acceptance_hardening://{codebase_id}/{section}/{filename}"


def base_artifact(
    *,
    workspace_id: str,
    codebase_id: str,
    phase: str,
    artifact_type: str,
    generated_at: str,
    artifact_refs: list[Any],
    evidence_refs: list[Any],
    warnings: list[Any] | None = None,
    unresolved: list[Any] | None = None,
    next_actions: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": PROJECT_ACCEPTANCE_HARDENING_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "phase": phase,
        "artifact_type": artifact_type,
        "generated_at": generated_at,
        "artifact_refs": list(artifact_refs),
        "evidence_refs": list(evidence_refs),
        "warnings": list(warnings or []),
        "unresolved": list(unresolved or []),
        "next_actions": list(next_actions or []),
    }


def unresolved_item(kind: str, reason: str, *, item_id: str | None = None, evidence_refs: list[Any] | None = None, next_action: str = "review") -> dict[str, Any]:
    return {
        "id": item_id or kind,
        "kind": kind,
        "status": kind,
        "reason": reason,
        "evidence_refs": list(evidence_refs or []),
        "next_action": next_action,
    }


def redaction_findings(payload: Any) -> list[dict[str, Any]]:
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    findings: list[dict[str, Any]] = []
    if "Traceback (most recent call last)" in raw:
        findings.append(unresolved_item("structured_blocker", "public payload contains raw traceback marker", item_id="raw_traceback"))
    if SECRET_RE.search(raw):
        findings.append(unresolved_item("structured_blocker", "public payload contains secret-like literal", item_id="secret_literal"))
    cleaned = (
        raw.replace("repo://", "repo_ref://")
        .replace("project_acceptance_hardening://", "artifact_ref://")
        .replace("agent_memory_release://", "artifact_ref://")
        .replace("external_e2e_portal_delivery://", "artifact_ref://")
        .replace("stabilization_e2e_portal://", "artifact_ref://")
        .replace("human_agent_deepening://", "artifact_ref://")
    )
    if ABSOLUTE_PATH_RE.search(cleaned):
        findings.append(unresolved_item("structured_blocker", "public payload contains local absolute path", item_id="absolute_path"))
    return findings


def status_summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "accepted_count": sum(1 for row in rows if row.get("status") == "accepted"),
        "needs_review_count": sum(1 for row in rows if row.get("status") == "needs_review"),
        "structured_unavailable_count": sum(1 for row in rows if row.get("status") == "structured_unavailable"),
        "structured_blocker_count": sum(1 for row in rows if row.get("status") == "structured_blocker"),
    }


def worst_status(statuses: list[str]) -> str:
    if "structured_blocker" in statuses:
        return "structured_blocker"
    if "structured_unavailable" in statuses:
        return "structured_unavailable"
    if "needs_review" in statuses:
        return "needs_review"
    return "accepted" if statuses and set(statuses) == {"accepted"} else "needs_review"
