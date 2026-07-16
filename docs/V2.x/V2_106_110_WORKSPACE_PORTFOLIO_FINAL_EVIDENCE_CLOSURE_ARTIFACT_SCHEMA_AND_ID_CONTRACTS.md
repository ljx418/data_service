# V2.106-V2.110 Artifact Schema and Stable ID Contracts

## 1. Contract Status

This document freezes the P0 artifact contract for V2.106-V2.110 implementation guidance. It is not implementation evidence.

All JSON artifacts must use deterministic IDs, run lineage fields and evidence references. Implementations may add optional fields, but must not remove required fields or weaken status/evidence rules.

## 2. Common Artifact Envelope

Required fields for every JSON artifact:

```json
{
  "schema_version": "v2.106-110.<artifact_name>.1",
  "artifact_id": "repo-relative artifact id",
  "workspace_id": "string",
  "run_id": "run_YYYYMMDDTHHMMSSZ_<short_hash>",
  "producer_name": "workspace_portfolio_final_evidence",
  "producer_version": "v2.106-110",
  "generated_at": "ISO-8601 UTC timestamp",
  "input_artifact_refs": ["repo-relative path"],
  "input_hashes": {"repo-relative path": "sha256 hex"},
  "workspace_fingerprint": "sha256 hex",
  "status": "accepted|needs_review|structured_unavailable|structured_blocker|out_of_scope",
  "artifact_refs": ["repo-relative path"],
  "evidence_refs": ["repo-relative path or evidence id"],
  "warnings": ["string"],
  "unresolved": [
    {
      "id": "stable unresolved id",
      "kind": "needs_review|structured_unavailable|structured_blocker",
      "reason": "string",
      "next_action": "string"
    }
  ],
  "data": {}
}
```

Forbidden in public artifacts:

- local absolute paths unless explicitly marked debug-only and redacted in public output
- secret, token, credential, private key, raw traceback, virtualenv path
- accepted claim without evidence refs

## 3. Stable ID Rules

| Object | ID rule |
| --- | --- |
| `run_id` | `run_` + UTC timestamp + 8-char hash of workspace root, input artifact hashes and phase |
| `requirement_id` | `REQ-V2xxx-<capability_slug>` |
| `project_id` | normalized directory name plus 8-char path hash |
| `media_row_id` | `media:` + project_id + relative path hash |
| `source_row_id` | `source:` + project_id + relative path hash |
| `build_job_id` | `build:` + project_id + build profile hash |
| `evidence_id` | `evidence:` + artifact path hash + row id |
| `gate_row_id` | `gate:` + requirement_id + evidence row id |

Stable IDs must not depend on row order.

## 4. Artifact Schemas

### 4.1 `coverage_state_closure.json`

Required `data` fields:

```json
{
  "requirements": [
    {
      "requirement_id": "REQ-V2106-coverage-state",
      "source_doc_ref": "repo-relative path",
      "previous_status": "planned|accepted|needs_review|structured_unavailable|structured_blocker",
      "current_status": "accepted|needs_review|structured_unavailable|structured_blocker|out_of_scope",
      "evidence_refs": ["repo-relative path"],
      "reason": "string"
    }
  ],
  "non_accepted_count": 0,
  "accepted_count": 0
}
```

Negative example: a row with `current_status=accepted` and empty `evidence_refs`.

### 4.2 `architecture_state_closure.json`

Required `data` fields:

```json
{
  "entities": [
    {
      "entity_id": "arch:<slug>",
      "entity_name": "string",
      "entity_kind": "module|adapter|artifact|ui|audit|gate",
      "implementation_state": "implemented|needs_change|planned|out_of_scope",
      "code_refs": ["repo-relative path"],
      "doc_refs": ["repo-relative path"],
      "drawio_refs": ["page name or cell id"],
      "evidence_refs": ["repo-relative path"]
    }
  ],
  "conflicts": [
    {
      "conflict_id": "string",
      "sources": ["code|acceptance_audit|coverage_matrix|target_architecture|drawio|prd"],
      "resolution": "string"
    }
  ]
}
```

### 4.3 `ocr_provider_health.json`

Required `data` fields:

```json
{
  "providers": [
    {
      "provider_id": "ocr:tesseract",
      "provider_type": "ocr|conversion|browser",
      "execution_status": "succeeded|failed|unavailable",
      "acceptance_status": "accepted|structured_unavailable|structured_blocker",
      "version": "string|null",
      "command_ref": "string|null",
      "evidence_refs": ["repo-relative path"],
      "failure_category": "missing_binary|missing_library|permission_denied|timeout|not_configured|null"
    }
  ]
}
```

### 4.4 `media_evidence_matrix.json`

Required `data` fields:

```json
{
  "media_rows": [
    {
      "media_row_id": "media:<id>",
      "project_id": "string",
      "repo_relative_path": "string",
      "format": "png|jpg|pdf|ppt|pptx|docx|other",
      "requires_ocr": true,
      "extractor_status": "supported|unsupported|needs_ocr|failed",
      "execution_status": "pending|succeeded|failed|timeout|skipped|unavailable",
      "acceptance_status": "accepted|needs_review|structured_unavailable|structured_blocker|out_of_scope",
      "evidence_refs": ["repo-relative path"],
      "failure_category": "none|ocr_missing|conversion_missing|unsupported_format|timeout|permission_denied|needs_review",
      "next_action": "string"
    }
  ]
}
```

### 4.5 `full_build_queue.json`

Required `data` fields:

```json
{
  "build_profile": {
    "profile_id": "string",
    "max_code_projects": 3,
    "timeout_seconds": 120,
    "command_allowlist_ref": "string",
    "sandbox_mode": "read_only_input_with_external_output"
  },
  "jobs": [
    {
      "build_job_id": "build:<id>",
      "project_id": "string",
      "project_ref": "repo-relative or redacted path ref",
      "queue_state": "pending|queued|running|completed|deferred_by_limit|blocked",
      "execution_status": "pending|succeeded|failed|timeout|skipped|unavailable",
      "acceptance_status": "accepted|needs_review|structured_unavailable|structured_blocker|out_of_scope",
      "command_refs": ["string"],
      "artifact_refs": ["repo-relative path"],
      "failure_category": "none|dependency_drift|sandbox_limit|timeout|permission_denied|unsafe_command|needs_review",
      "next_action": "string"
    }
  ]
}
```

### 4.6 `project_build_diagnosis.json`

Required `data` fields:

```json
{
  "diagnoses": [
    {
      "build_job_id": "build:<id>",
      "diagnosis_status": "accepted|needs_review|structured_unavailable|structured_blocker",
      "reason": "string",
      "evidence_refs": ["repo-relative path"],
      "safe_to_retry": true,
      "next_action": "string"
    }
  ]
}
```

### 4.7 `document_source_trace_closure.json`

Required `data` fields:

```json
{
  "source_rows": [
    {
      "source_row_id": "source:<id>",
      "project_id": "string",
      "repo_relative_path": "string",
      "source_import_ref": "repo-relative path|null",
      "query_result_ref": "repo-relative path|null",
      "source_trace_refs": ["repo-relative path"],
      "execution_status": "pending|succeeded|failed|timeout|skipped|unavailable",
      "acceptance_status": "accepted|needs_review|structured_unavailable|structured_blocker|out_of_scope",
      "failure_category": "none|import_failed|query_failed|trace_missing|unsupported_format|needs_review",
      "next_action": "string"
    }
  ]
}
```

### 4.8 `ui_evidence_capture.json`

Required `data` fields:

```json
{
  "captures": [
    {
      "capture_id": "ui:<id>",
      "route": "/knowledge?view=portfolio",
      "execution_status": "succeeded|failed|timeout|unavailable",
      "acceptance_status": "accepted|structured_unavailable|structured_blocker",
      "screenshot_refs": ["repo-relative path"],
      "browser_provider": "chromium|chrome|chrome-cli|none",
      "failure_category": "none|missing_browser|missing_library|timeout|permission_denied",
      "next_action": "string"
    }
  ]
}
```

### 4.9 `final_release_gate.json`

Required `data` fields:

```json
{
  "gate_rows": [
    {
      "gate_row_id": "gate:<id>",
      "requirement_id": "REQ-V2xxx-<slug>",
      "high_risk": true,
      "execution_status": "succeeded|failed|timeout|skipped|unavailable",
      "acceptance_status": "accepted|needs_review|structured_unavailable|structured_blocker|out_of_scope",
      "evidence_refs": ["repo-relative path"],
      "blocking_final_acceptance": true,
      "reason": "string"
    }
  ],
  "implementation_status": "accepted|needs_review|structured_unavailable|structured_blocker",
  "portfolio_final_status": "accepted|needs_review|structured_unavailable|structured_blocker",
  "decision_rule": "worst_high_risk_acceptance_status"
}
```

## 5. Cross-artifact Foreign Keys

- `project_id` must match the V2.101-V2.105 project registry or a V2.108 queue row.
- `media_row_id` and `source_row_id` must reference a valid `project_id`.
- `build_job_id` must reference a valid `project_id`.
- `gate_row_id` must reference a valid `requirement_id` and at least one artifact or evidence ref.
- Final gate must reject mixed-run artifacts unless `run_id` compatibility is explicitly recorded.

