"""Shared helpers for V2.91-V2.95 real acceptance closure artifacts."""

from __future__ import annotations

import json
import re
from typing import Any


REAL_ACCEPTANCE_CLOSURE_SCHEMA_VERSION = "v2.91-95"
STATUSES = {"accepted", "needs_review", "structured_unavailable", "structured_blocker", "failed", "planned"}
ABSOLUTE_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])(?:/(?:mnt|home|Users|tmp|var|etc|opt|root|workspaces?)(?:/[A-Za-z0-9._ -]+)+)|[A-Za-z]:\\\\")
SECRET_RE = re.compile(r"(?i)(api[_-]?key|authorization|bearer\s+[A-Za-z0-9._-]+|secret[_-](?:key|value)|(?:access|refresh|id)[_-]?token)")


def artifact_uri(codebase_id: str, section: str, filename: str) -> str:
    return f"real_acceptance_closure://{codebase_id}/{section}/{filename}"


def base_artifact(
    *,
    workspace_id: str,
    codebase_id: str,
    phase: str,
    artifact_type: str,
    generated_at: str,
    artifact_refs: list[Any],
    evidence_refs: list[Any] | None = None,
    warnings: list[Any] | None = None,
    unresolved: list[Any] | None = None,
    next_actions: list[str] | None = None,
    status: str = "needs_review",
) -> dict[str, Any]:
    return {
        "schema_version": REAL_ACCEPTANCE_CLOSURE_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "phase": phase,
        "artifact_type": artifact_type,
        "generated_at": generated_at,
        "status": status if status in STATUSES else "needs_review",
        "artifact_refs": list(artifact_refs),
        "evidence_refs": list(evidence_refs or []),
        "warnings": list(warnings or []),
        "unresolved": list(unresolved or []),
        "next_actions": list(next_actions or []),
    }


def unresolved_item(
    kind: str,
    reason: str,
    *,
    item_id: str | None = None,
    evidence_refs: list[Any] | None = None,
    next_action: str = "review",
) -> dict[str, Any]:
    status = kind if kind in {"needs_review", "structured_unavailable", "structured_blocker"} else "needs_review"
    return {
        "id": item_id or status,
        "kind": status,
        "status": status,
        "reason": reason,
        "evidence_refs": list(evidence_refs or []),
        "next_action": next_action,
    }


def status_summary(rows: list[dict[str, Any]]) -> dict[str, int]:
    def status_of(row: dict[str, Any]) -> str:
        return str(row.get("status") or row.get("e2e_status") or row.get("decision_status") or row.get("decision") or "needs_review")

    statuses = [status_of(row) for row in rows]
    return {
        "accepted_count": sum(1 for status in statuses if status in {"accepted", "approved", "rejected", "revoked", "out_of_scope"}),
        "needs_review_count": sum(1 for status in statuses if status == "needs_review"),
        "structured_unavailable_count": sum(1 for status in statuses if status == "structured_unavailable"),
        "structured_blocker_count": sum(1 for status in statuses if status == "structured_blocker"),
        "failed_count": sum(1 for status in statuses if status == "failed"),
    }


def worst_status(statuses: list[str]) -> str:
    normalized = ["accepted" if status in {"approved", "rejected", "revoked", "out_of_scope"} else status for status in statuses]
    for status in ["structured_blocker", "failed", "structured_unavailable", "needs_review"]:
        if status in normalized:
            return status
    return "accepted" if normalized and set(normalized) == {"accepted"} else "needs_review"


def public_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": payload.get("artifact_type"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "phase": payload.get("phase"),
        "status": payload.get("status"),
        "data": dict(payload.get("data") or {}),
        "summary": dict(payload.get("summary") or {}),
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "evidence_refs": list(payload.get("evidence_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
        "next_actions": list(payload.get("next_actions") or []),
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
        .replace("source://", "source_ref://")
        .replace("manual://", "manual_ref://")
        .replace("review://", "review_ref://")
        .replace("command://", "command_ref://")
        .replace("real_document_acceptance://", "artifact_ref://")
        .replace("real_document_full_corpus_release://", "artifact_ref://")
        .replace("real_acceptance_closure://", "artifact_ref://")
    )
    if ABSOLUTE_PATH_RE.search(cleaned):
        findings.append(unresolved_item("structured_blocker", "public payload contains local absolute path", item_id="absolute_path"))
    return findings


def apply_redaction_guard(*payloads: Any) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for payload in payloads:
        findings.extend(redaction_findings(payload))
    if not findings:
        return []
    for payload in payloads:
        if isinstance(payload, dict):
            payload.setdefault("unresolved", []).extend(findings)
            payload["status"] = "structured_blocker"
            if "final_release_status" in payload:
                payload["final_release_status"] = "structured_blocker"
    return findings
