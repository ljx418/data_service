"""Shared helpers for V2.54-V2.58 Human / Agent Deepening."""

from __future__ import annotations

import json
import re
from typing import Any


HUMAN_AGENT_DEEPENING_SCHEMA_VERSION = "v2.54-58"
ABSOLUTE_PATH_RE = re.compile(r"(?<![A-Za-z0-9_])(?:/(?:mnt|home|Users|tmp|var|etc|opt|root|workspaces?)(?:/[A-Za-z0-9._ -]+)+)|[A-Za-z]:\\\\")
SECRET_RE = re.compile(r"(?i)(api[_-]?key|authorization|bearer\s+[A-Za-z0-9._-]+|secret[_-](?:key|value)|(?:access|refresh|id)[_-]?token)")


def base_artifact(*, workspace_id: str, codebase_id: str, phase: str, artifact_type: str, generated_at: str, artifact_refs: list[Any], evidence_refs: list[Any], warnings: list[Any] | None = None, unresolved: list[Any] | None = None) -> dict[str, Any]:
    return {
        "schema_version": HUMAN_AGENT_DEEPENING_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "phase": phase,
        "artifact_type": artifact_type,
        "generated_at": generated_at,
        "artifact_refs": artifact_refs,
        "evidence_refs": evidence_refs,
        "warnings": list(warnings or []),
        "unresolved": list(unresolved or []),
    }


def structured_unavailable(item_id: str, reason: str, *, evidence_refs: list[Any] | None = None) -> dict[str, Any]:
    return {
        "id": item_id,
        "status": "structured_unavailable",
        "reason": reason,
        "evidence_refs": list(evidence_refs or []),
    }


def needs_review(item_id: str, reason: str, *, evidence_refs: list[Any] | None = None) -> dict[str, Any]:
    return {
        "id": item_id,
        "status": "needs_review",
        "reason": reason,
        "evidence_refs": list(evidence_refs or []),
    }


def redaction_findings(payload: Any) -> list[dict[str, str]]:
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    findings = []
    if "Traceback (most recent call last)" in raw:
        findings.append({"id": "raw_traceback", "status": "structured_blocker", "reason": "public payload contains raw traceback marker"})
    if SECRET_RE.search(raw):
        findings.append({"id": "secret_literal", "status": "structured_blocker", "reason": "public payload contains secret-like literal"})
    # Artifact URIs such as repo:// are allowed; local absolute paths are not.
    cleaned = raw.replace("repo://", "repo_ref://").replace("agent_productization://", "artifact_ref://").replace("human_agent_deepening://", "artifact_ref://")
    if ABSOLUTE_PATH_RE.search(cleaned):
        findings.append({"id": "absolute_path", "status": "structured_blocker", "reason": "public payload contains local absolute path"})
    return findings
