"""Shared contracts for V2.116-V2.120 real evidence acceptance artifacts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from data_service.mcp_common import now


SCHEMA_VERSION = "v2.116-120"
PRODUCER_NAME = "workspace_portfolio_real_evidence_acceptance"
PRODUCER_VERSION = "1"
SCHEMA_BUNDLE_PATH = Path("docs/V2.x/V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_SCHEMA_BUNDLE.json")

ARTIFACT_STATUSES = {
    "accepted",
    "needs_review",
    "structured_unavailable",
    "structured_blocker",
    "failed",
}
STATUS_PRIORITY = {
    "failed": 0,
    "structured_blocker": 1,
    "structured_unavailable": 2,
    "needs_review": 3,
    "accepted": 4,
}


def slug(value: object) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip().lower()).strip("-")
    return text[:80] or "item"


def digest_value(value: Any, *, length: int = 16) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:length]


def full_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


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


def artifact_ref(filename: str, *, run_id: str | None = None) -> str:
    prefix = f"runs/{run_id}/" if run_id else ""
    return f"portfolio_real_evidence_acceptance/{prefix}{filename}"


def unresolved(kind: str, reason: str, *, item_id: str, next_action: str, evidence_refs: list[Any] | None = None) -> dict[str, Any]:
    safe_kind = kind if kind in {"needs_review", "structured_unavailable", "structured_blocker"} else "needs_review"
    return {
        "kind": safe_kind,
        "item_id": item_id,
        "reason": reason,
        "next_action": next_action,
        "evidence_refs": [str(item) for item in list(evidence_refs or [])],
    }


def worst_status(statuses: list[str]) -> str:
    normalized = [item if item in ARTIFACT_STATUSES else "needs_review" for item in statuses]
    if not normalized:
        return "needs_review"
    return min(normalized, key=lambda item: STATUS_PRIORITY[item])


def status_counts(rows: list[dict[str, Any]], *, field: str = "row_acceptance_status") -> dict[str, int]:
    statuses = [str(row.get(field) or row.get("artifact_status") or "needs_review") for row in rows]
    return {
        "accepted_count": sum(1 for item in statuses if item == "accepted"),
        "needs_review_count": sum(1 for item in statuses if item == "needs_review"),
        "structured_unavailable_count": sum(1 for item in statuses if item == "structured_unavailable"),
        "structured_blocker_count": sum(1 for item in statuses if item == "structured_blocker"),
        "failed_count": sum(1 for item in statuses if item == "failed"),
    }


def run_id_for(*, workspace_id: str, run_type: str, lineage_root_id: str, input_hashes: dict[str, Any]) -> str:
    return f"v2116-{run_type}-{slug(workspace_id)}-{digest_value({'lineage_root_id': lineage_root_id, 'input_hashes': input_hashes}, length=12)}"


def base_artifact(
    *,
    workspace_id: str,
    run_id: str,
    run_type: str,
    lineage_root_id: str,
    parent_run_ids: list[str] | None,
    source_run_refs: list[dict[str, Any]] | None,
    artifact_id: str,
    artifact_type: str,
    phase: str,
    artifact_status: str,
    input_manifest_ref: str,
    input_hashes: dict[str, Any] | None = None,
    artifact_refs: list[Any] | None = None,
    evidence_refs: list[Any] | None = None,
    warnings: list[str] | None = None,
    unresolved_items: list[dict[str, Any]] | None = None,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "run_id": run_id,
        "run_type": run_type,
        "lineage_root_id": lineage_root_id,
        "parent_run_ids": list(parent_run_ids or []),
        "source_run_refs": list(source_run_refs or []),
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "phase": phase,
        "generated_at": now(),
        "producer": {"name": PRODUCER_NAME, "version": PRODUCER_VERSION},
        "input_manifest_ref": input_manifest_ref,
        "input_hashes": dict(input_hashes or {}),
        "artifact_refs": list(artifact_refs or []),
        "evidence_refs": list(evidence_refs or []),
        "artifact_status": artifact_status,
        "warnings": list(warnings or []),
        "unresolved": list(unresolved_items or []),
        "data": dict(data or {}),
    }


def public_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return json.loads(json.dumps(payload, ensure_ascii=False, default=str))
