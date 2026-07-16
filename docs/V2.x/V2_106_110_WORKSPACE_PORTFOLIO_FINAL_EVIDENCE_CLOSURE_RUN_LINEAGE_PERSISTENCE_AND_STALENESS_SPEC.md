# V2.106-V2.110 Run Lineage, Persistence and Staleness Spec

## 1. Purpose

This document closes the P0 evidence lineage gap. V2.106-V2.110 artifacts must be traceable to one compatible run lineage, or final gate must reject them.

## 2. Run Metadata

Every build/closure run must create run metadata:

```json
{
  "run_id": "run_YYYYMMDDTHHMMSSZ_<short_hash>",
  "workspace_id": "string",
  "root_ref": "redacted or configured root ref",
  "workspace_fingerprint": "sha256 hex",
  "started_at": "ISO-8601 UTC",
  "completed_at": "ISO-8601 UTC|null",
  "producer_name": "workspace_portfolio_final_evidence",
  "producer_version": "v2.106-110",
  "input_artifact_refs": ["repo-relative path"],
  "input_hashes": {"repo-relative path": "sha256 hex"},
  "command_refs": ["command id"],
  "status": "accepted|needs_review|structured_unavailable|structured_blocker|failed"
}
```

## 3. Atomic Write Rules

- Write artifacts to temp path first.
- Validate JSON schema before publish.
- Rename temp path atomically into artifact path.
- Write a sidecar hash file or include hash in run manifest.
- On interrupted write, mark run `structured_blocker` and preserve recovery metadata.

## 4. Locking Rules

- A workspace may have only one active final evidence build run unless explicitly requested as dry-run.
- Lock record must include `run_id`, pid/process ref where available, started_at and stale-after timestamp.
- Stale lock cleanup must be explicit and recorded.

## 5. Staleness Rules

An artifact is stale if any condition is true:

- input artifact hash changed
- workspace fingerprint changed
- schema version changed
- run lineage is not compatible with current final gate
- required artifact is missing
- artifact generated_at is older than the configured freshness window and no override evidence exists

Stale high-risk artifact rows must be `needs_review` or `structured_blocker`; they must not be accepted.

## 6. Mixed-run Rejection

Final gate must reject mixed runs unless a compatibility manifest explicitly declares them compatible:

```json
{
  "compatibility_manifest_id": "string",
  "included_run_ids": ["run_..."],
  "input_hashes_verified": true,
  "reason": "string",
  "evidence_refs": ["repo-relative path"]
}
```

Without this manifest, mixed-run input maps to:

```text
acceptance_status=structured_blocker
failure_category=mixed_run_rejected
```

## 7. Evidence Reference Integrity

Every `evidence_ref` must resolve to:

- an existing committed repo-relative path, or
- a persisted artifact path under workspace storage, or
- a command/API/MCP result id recorded in run metadata.

Missing evidence refs block accepted status.

