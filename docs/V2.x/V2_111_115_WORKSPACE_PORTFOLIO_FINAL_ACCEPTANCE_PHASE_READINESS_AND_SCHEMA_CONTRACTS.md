# V2.111-V2.115 Phase Readiness and Schema Contracts

## 1. Unified Public Envelope

Every public build/read/report payload must include:

```json
{
  "ok": false,
  "schema_version": "v2.111-115",
  "workspace_id": "string",
  "phase": "V2.111|V2.112|V2.113|V2.114|V2.115",
  "status": "accepted|needs_review|structured_unavailable|structured_blocker|failed|out_of_scope",
  "run_id": "string",
  "workspace_fingerprint": "string",
  "input_artifact_refs": ["repo-relative or artifact ref"],
  "input_hashes": {},
  "artifact_refs": ["repo-relative or artifact ref"],
  "evidence_refs": ["repo-relative or artifact ref"],
  "warnings": ["string"],
  "unresolved": [
    {
      "id": "string",
      "kind": "needs_review|structured_unavailable|structured_blocker",
      "reason": "string",
      "next_action": "string",
      "evidence_refs": []
    }
  ],
  "next_actions": ["string"],
  "data": {}
}
```

## 2. Status Algebra

Execution status:

```text
pending | queued | running | succeeded | failed | timeout | skipped | unavailable
```

Acceptance status:

```text
accepted | needs_review | structured_unavailable | structured_blocker | failed | out_of_scope
```

Priority for final gate:

```text
structured_blocker > failed > structured_unavailable > needs_review > out_of_scope > accepted
```

Rules:

- `needs_review`, `structured_unavailable`, `structured_blocker`, and `failed` are not accepted.
- `out_of_scope` requires explicit approval evidence.
- Final gate must reject mixed-run artifacts.
- OCR rows cannot be accepted unless they reference a qualified OCR sample row.

## 3. Artifact Schemas

### ocr_sample_qualification.json

Required fields:

```json
{
  "rows": [
    {
      "stable_id": "ocr-sample:<project_id>:<source_format>:<index>",
      "project_id": "string",
      "source_ref": "string",
      "source_hash": "sha256|string",
      "source_format": "png|jpg|jpeg|tiff|bmp|pdf|pptx|docx|other",
      "sample_kind": "text_image|scanned_pdf|direct_text_pdf|direct_text_ppt|direct_text_docx|non_text_media|unknown",
      "ocr_required": true,
      "expected_text_anchor": "string",
      "expected_text_anchor_source": "human_review|filename_hint|existing_metadata|not_available",
      "qualification_status": "qualified|needs_review|structured_unavailable|unsupported",
      "qualification_reason": "string",
      "evidence_refs": []
    }
  ],
  "summary": {
    "qualified_ocr_sample_count": 0,
    "direct_text_extraction_count": 0,
    "structured_unavailable_count": 0
  }
}
```

Rules:

- `sample_kind=direct_text_pdf|direct_text_ppt|direct_text_docx` cannot satisfy OCR accepted.
- OCR accepted requires at least one `qualification_status=qualified` row and corresponding OCR output evidence.
- If no qualified OCR sample exists, V2.111 OCR acceptance must be `structured_unavailable` or `needs_review`.

### media_execution_results.json

Required fields:

```json
{
  "rows": [
    {
      "stable_id": "media:<project_id>:<source_format>:<index>",
      "project_id": "string",
      "source_ref": "string",
      "source_format": "string",
      "sample_qualification_ref": "stable_id or empty",
      "execution_kind": "ocr|conversion|direct_text_extraction|metadata_only|unsupported",
      "provider": "string",
      "provider_version": "string",
      "execution_status": "succeeded|failed|timeout|skipped|unavailable",
      "acceptance_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
      "output_ref": "string",
      "output_hash": "sha256|string",
      "failure_category": "provider_missing|conversion_failed|ocr_failed|timeout|unsupported|needs_review",
      "evidence_refs": []
    }
  ],
  "summary": {}
}
```

### source_trace_execution.json

Required fields:

```json
{
  "rows": [
    {
      "stable_id": "source-trace:<source_id>",
      "source_id": "string",
      "import_ref": "string",
      "query_ref": "string",
      "source_trace_refs": [],
      "execution_status": "succeeded|failed|timeout|skipped|unavailable",
      "acceptance_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
      "missing_links": ["import|query|source_trace"],
      "evidence_refs": []
    }
  ],
  "summary": {}
}
```

### ui_evidence_capture.json

Required fields:

```json
{
  "rows": [
    {
      "stable_id": "ui:<scenario>",
      "scenario": "string",
      "url": "string",
      "viewport": {"width": 1280, "height": 900},
      "execution_status": "succeeded|failed|timeout|skipped|unavailable",
      "acceptance_status": "accepted|structured_unavailable|structured_blocker|failed",
      "screenshot_ref": "string",
      "screenshot_hash": "sha256|string",
      "browser_diagnosis": "string",
      "evidence_refs": []
    }
  ],
  "summary": {}
}
```

### safe_build_execution.json

Required fields:

```json
{
  "rows": [
    {
      "stable_id": "build:<project_id>",
      "project_id": "string",
      "command_ref": "string",
      "allowlist_status": "approved|rejected|needs_review",
      "cache_key": "string",
      "execution_status": "succeeded|failed|timeout|skipped|unavailable",
      "acceptance_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
      "exit_code": 0,
      "duration_ms": 0,
      "log_ref": "string",
      "log_hash": "sha256|string",
      "failure_category": "timeout|command_rejected|dependency_missing|real_failure|needs_review",
      "evidence_refs": []
    }
  ],
  "summary": {}
}
```

### final_acceptance_gate.json

Required fields:

```json
{
  "implementation_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "portfolio_final_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "phase_statuses": {},
  "high_risk_unresolved_count": 0,
  "mixed_run_rejected": false,
  "false_green_rejections": [],
  "accepted_evidence_refs": [],
  "blocking_unresolved": []
}
```

## 4. Public Surface Contract

CLI:

- `plan`: accepts `--workspace-id`, `--root`, optional limits; does not execute OCR/build/UI.
- `build`: accepts `--workspace-id`, `--root`, `--max-code-projects`, `--timeout-seconds`, `--headless`.
- `read`: accepts `--workspace-id`; reads persisted artifacts only.
- `report`: accepts `--workspace-id`; reads persisted report only.

MCP and HTTP must provide parity with CLI.

Error behavior:

- Missing artifact: 404/blocked with next action build.
- Missing dependency: structured unavailable with provider/browser/build diagnosis.
- Invalid path: structured blocker.
- Unapproved command: needs_review or structured_blocker, never executed.

## 5. Phase Readiness Gate

Before each implementation subphase:

- phase-specific development plan exists;
- phase-specific acceptance plan exists;
- pre-implementation audit has no fatal or major finding;
- artifact schema for that phase is frozen;
- no protected legacy file change is required.
