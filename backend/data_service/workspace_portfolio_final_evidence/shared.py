"""Shared contracts for V2.106-V2.110 final evidence artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from data_service.mcp_common import now


SCHEMA_VERSION = "v2.106-110"
PRODUCER_NAME = "workspace_portfolio_final_evidence"
PRODUCER_VERSION = "1"

EXECUTION_STATUSES = {
    "pending",
    "queued",
    "running",
    "succeeded",
    "failed",
    "timeout",
    "skipped",
    "unavailable",
}
ACCEPTANCE_STATUSES = {
    "accepted",
    "needs_review",
    "structured_unavailable",
    "structured_blocker",
    "out_of_scope",
    "failed",
}
ACCEPTANCE_PRIORITY = {
    "structured_blocker": 0,
    "failed": 1,
    "structured_unavailable": 2,
    "needs_review": 3,
    "out_of_scope": 4,
    "accepted": 5,
}


def slug(value: object) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip().lower()).strip("-")
    return text[:80] or "item"


def digest_value(value: Any, *, length: int = 16) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:length]


def file_hash(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def safe_path_ref(path: Path, root: Path | None = None) -> str:
    resolved = Path(path).expanduser().resolve()
    if root is not None:
        try:
            return f"<workspace-root>/{resolved.relative_to(Path(root).expanduser().resolve()).as_posix()}"
        except ValueError:
            pass
    return f"path-ref://{slug(resolved.name)}-{digest_value(str(resolved), length=8)}"


def artifact_ref(kind: str, filename: str) -> dict[str, str]:
    return {"type": kind, "artifact_ref": f"workspace_portfolio_final_evidence://portfolio_final_evidence/{filename}"}


def unresolved(kind: str, reason: str, *, item_id: str, next_action: str, evidence_refs: list[Any] | None = None) -> dict[str, Any]:
    safe_kind = kind if kind in {"needs_review", "structured_unavailable", "structured_blocker"} else "needs_review"
    return {
        "id": item_id,
        "kind": safe_kind,
        "status": safe_kind,
        "reason": reason,
        "next_action": next_action,
        "evidence_refs": list(evidence_refs or []),
    }


def status_counts(rows: list[dict[str, Any]], *, field: str = "acceptance_status") -> dict[str, int]:
    statuses = [str(row.get(field) or row.get("status") or "needs_review") for row in rows]
    return {
        "accepted_count": sum(1 for item in statuses if item == "accepted"),
        "needs_review_count": sum(1 for item in statuses if item == "needs_review"),
        "structured_unavailable_count": sum(1 for item in statuses if item == "structured_unavailable"),
        "structured_blocker_count": sum(1 for item in statuses if item == "structured_blocker"),
        "out_of_scope_count": sum(1 for item in statuses if item == "out_of_scope"),
        "failed_count": sum(1 for item in statuses if item == "failed"),
    }


def worst_acceptance_status(statuses: list[str]) -> str:
    normalized = [item if item in ACCEPTANCE_STATUSES else "needs_review" for item in statuses]
    if not normalized:
        return "needs_review"
    return min(normalized, key=lambda item: ACCEPTANCE_PRIORITY[item])


def run_id_for(*, workspace_id: str, root_ref: str, input_hashes: dict[str, Any]) -> str:
    return f"v2106-{slug(workspace_id)}-{digest_value({'root_ref': root_ref, 'input_hashes': input_hashes}, length=12)}"


def base_artifact(
    *,
    workspace_id: str,
    phase: str,
    artifact_type: str,
    artifact_id: str,
    run_id: str,
    status: str,
    input_artifact_refs: list[Any] | None = None,
    input_hashes: dict[str, Any] | None = None,
    evidence_refs: list[Any] | None = None,
    artifact_refs: list[Any] | None = None,
    workspace_fingerprint: str = "",
) -> dict[str, Any]:
    return {
        "ok": status == "accepted",
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "phase": phase,
        "artifact_type": artifact_type,
        "artifact_id": artifact_id,
        "run_id": run_id,
        "producer_name": PRODUCER_NAME,
        "producer_version": PRODUCER_VERSION,
        "generated_at": now(),
        "source_snapshot_id": workspace_fingerprint or run_id,
        "workspace_fingerprint": workspace_fingerprint or run_id,
        "status": status,
        "acceptance_status": status,
        "input_artifact_refs": list(input_artifact_refs or []),
        "input_hashes": dict(input_hashes or {}),
        "artifact_refs": list(artifact_refs or []),
        "evidence_refs": list(evidence_refs or []),
        "warnings": [],
        "unresolved": [],
        "next_actions": [],
        "data": {},
    }
