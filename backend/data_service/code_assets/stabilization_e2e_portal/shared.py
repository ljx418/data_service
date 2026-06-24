"""Shared helpers for V2.59-V2.62 stabilization stage."""

from __future__ import annotations

import json
import re
from typing import Any


STABILIZATION_SCHEMA_VERSION = "v2.59-62"
ABSOLUTE_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])(?:/(?:mnt|home|Users|tmp|var|etc|opt|root|workspaces?)(?:/[A-Za-z0-9._ -]+)+)|[A-Za-z]:\\\\")
SECRET_RE = re.compile(r"(?i)(api[_-]?key|authorization|bearer\s+[A-Za-z0-9._-]+|secret[_-](?:key|value)|(?:access|refresh|id)[_-]?token)")


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
) -> dict[str, Any]:
    return {
        "schema_version": STABILIZATION_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "phase": phase,
        "artifact_type": artifact_type,
        "generated_at": generated_at,
        "artifact_refs": list(artifact_refs),
        "evidence_refs": list(evidence_refs),
        "warnings": list(warnings or []),
        "unresolved": list(unresolved or []),
    }


def unresolved_item(item_id: str, status: str, reason: str, *, evidence_refs: list[Any] | None = None) -> dict[str, Any]:
    return {"id": item_id, "status": status, "reason": reason, "evidence_refs": list(evidence_refs or [])}


def structured_unavailable(item_id: str, reason: str, *, evidence_refs: list[Any] | None = None) -> dict[str, Any]:
    return unresolved_item(item_id, "structured_unavailable", reason, evidence_refs=evidence_refs)


def structured_blocker(item_id: str, reason: str, *, evidence_refs: list[Any] | None = None) -> dict[str, Any]:
    return unresolved_item(item_id, "structured_blocker", reason, evidence_refs=evidence_refs)


def needs_review(item_id: str, reason: str, *, evidence_refs: list[Any] | None = None) -> dict[str, Any]:
    return unresolved_item(item_id, "needs_review", reason, evidence_refs=evidence_refs)


def redaction_findings(payload: Any) -> list[dict[str, str]]:
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    findings = []
    if "Traceback (most recent call last)" in raw:
        findings.append(structured_blocker("raw_traceback", "public payload contains raw traceback marker"))
    if SECRET_RE.search(raw):
        findings.append(structured_blocker("secret_literal", "public payload contains secret-like literal"))
    cleaned = (
        raw.replace("repo://", "repo_ref://")
        .replace("agent_productization://", "artifact_ref://")
        .replace("human_agent_deepening://", "artifact_ref://")
        .replace("stabilization_e2e_portal://", "artifact_ref://")
    )
    if ABSOLUTE_PATH_RE.search(cleaned):
        findings.append(structured_blocker("absolute_path", "public payload contains local absolute path"))
    return findings


def artifact_uri(codebase_id: str, section: str, filename: str) -> str:
    return f"stabilization_e2e_portal://{codebase_id}/{section}/{filename}"
