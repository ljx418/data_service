# V2.111-V2.115 Implementation Blueprint and Acceptance Spec

## 1. Implementation Boundary

All new code should live in an isolated package:

```text
backend/data_service/workspace_portfolio_final_acceptance/
  __init__.py
  shared.py
  persistence.py
  service.py
  media_execution.py
  source_trace.py
  ui_evidence.py
  build_runtime.py
  release_gate.py
```

Optional public adapters:

```text
backend/data_service/cli_portfolio_final_acceptance.py
backend/data_service/mcp_workspace_portfolio_final_acceptance_tools.py
backend/app/api/v1/workspace_portfolio_final_acceptance.py
```

Protected files:

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

These protected files must not be modified unless the user explicitly approves.

## 2. Shared Build / Read / Report Contract

Public commands:

```text
portfolio-final-acceptance plan
portfolio-final-acceptance build
portfolio-final-acceptance read
portfolio-final-acceptance report
```

Rules:

- `plan` reads current artifacts and returns planned actions only.
- `build` generates persisted artifacts under `portfolio_final_acceptance/`.
- `read` only reads persisted artifacts.
- `report` only reads persisted artifacts and renders report content.
- No public command may silently convert non-accepted statuses into accepted.

## 3. Phase Implementation Blueprint

### V2.111 Media Execution

Inputs:

- `v2_106_110_real/portfolio_final_evidence/media_evidence_matrix.json`
- `v2_106_110_real/portfolio_final_evidence/ocr_provider_health.json`

Implementation:

- Classify each row into text-extractable, OCR-required, conversion-required, unsupported, or unavailable.
- Before OCR execution, build `ocr_sample_qualification.json` from real workspace files. A qualified OCR sample must have a source ref, source hash, sample kind, expected text anchor source, and qualification status.
- Use allowlisted local provider commands only.
- Write extracted text or converted artifacts only under managed workspace.
- Store output hash and artifact ref.

No-Go:

- Provider availability is not OCR acceptance.
- Direct text extraction from PDF/PPT/DOCX is not OCR acceptance.
- If no qualified real OCR sample exists, OCR acceptance must remain `structured_unavailable` or `needs_review`.
- Failed OCR must be `structured_unavailable` or `failed`, never accepted.

### V2.112 Source Trace Closure

Inputs:

- media execution results.
- source candidate rows from V2.106-V2.110.
- existing source registry/query/source trace services.

Implementation:

- Import accepted text artifacts as sources.
- Run representative query or deterministic source lookup.
- Verify source trace refs link answer/query results back to source.

No-Go:

- File existence is not source trace evidence.
- Imported source without query/source trace remains non-accepted.

### V2.113 Headless UI Evidence

Inputs:

- running or launchable service.
- `/knowledge?view=portfolio`.
- final evidence artifacts.

Implementation:

- Prefer headless browser execution.
- Capture desktop and mobile viewports.
- Store screenshot refs, hashes, URL, viewport, timestamp, scenario.
- If browser dependencies fail, output structured unavailable with dependency diagnosis.

No-Go:

- HTML report is not screenshot evidence.
- Visible browser/focus-stealing flow requires prior human notice.

### V2.114 Safe Multi-project Build Runtime

Inputs:

- project registry.
- full build queue.
- user-approved command allowlist.

Implementation:

- Build queue includes every discovered buildable project.
- Execute only allowlisted safe commands.
- Use per-project timeout, bounded log capture, redaction, cache key, retry/resume metadata.
- Write outputs to managed workspace, not scanned project directories.

No-Go:

- Arbitrary shell scripts are not run by default.
- Timeout, skipped, unavailable, or unapproved command rows are not accepted.

### V2.115 Final Acceptance Gate

Inputs:

- V2.111-V2.114 artifacts.
- public surface guard results.
- PRD/spec review.
- false-green audit.

Implementation:

- Validate run_id, workspace_fingerprint, input hashes.
- Reject mixed-run evidence.
- Compute final status using status algebra.
- Generate JSON gate, Markdown audit, and HTML report.

No-Go:

- Any high-risk non-accepted row blocks final accepted unless explicitly approved out of scope.

## 4. Required Focused Tests

```text
backend/tests/test_v2_111_ocr_media_provider_execution.py
backend/tests/test_v2_112_source_trace_full_closure.py
backend/tests/test_v2_113_headless_ui_evidence.py
backend/tests/test_v2_114_safe_multi_project_build_runtime.py
backend/tests/test_v2_115_final_acceptance_gate.py
```

Each focused test must assert both successful paths and false-green rejection paths.

## 5. Acceptance Spec

Implementation can be accepted only if:

- all planned artifacts are generated;
- focused tests pass;
- real `/mnt/c/workspace` E2E produces accepted rows or structured blockers;
- PRD/spec review is recorded;
- false-green audit rejects docs-only, readiness-only, UI-only, bounded-build-only evidence;
- public surface guard passes;
- protected legacy files remain unchanged.

Portfolio final release can be accepted only if:

- all high-risk OCR/source trace/UI/build rows are accepted, or explicitly approved out of scope with evidence;
- OCR accepted rows include qualified real OCR sample evidence and OCR output evidence, not only conversion/text extraction evidence;
- final gate has no unresolved high-risk blocker;
- final HTML report visibly lists accepted and non-accepted evidence.
