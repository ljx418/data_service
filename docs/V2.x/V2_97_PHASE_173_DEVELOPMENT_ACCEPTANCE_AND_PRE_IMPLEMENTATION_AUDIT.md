# V2.97 / Phase 173 Route A Evidence Automation Plan, Acceptance, and Audit

## Development Plan

- Implement `RouteAEvidenceAutomator` under `backend/data_service/code_assets/automated_evidence_closure/`.
- Persist `route_a_evidence/material_scan.json`, `redaction_audit.json`, `evidence_capture_manifest.json`, and `manual_confirmation_queue.md`.
- Expose build/read through CLI, MCP, and HTTP under `automated-evidence-closure`.

## Acceptance Plan

- Missing representative material must remain `needs_review`.
- Accepted requires real material refs, accepted redaction audit, screenshot/headless evidence refs, and manual confirmation.
- Route B, Full Corpus, mock-only, sample-only, and path-only evidence cannot replace Route A.

## Pre-implementation Audit

- Fatal findings: none.
- Major findings: none.
- Guardrails: no protected legacy file modification; no `needs_review` counted as `accepted`; public artifacts must not leak absolute paths, secrets, tokens, or raw traceback.

## Implementation Acceptance Result

- Focused test: `PYTHONPATH=backend pytest -q backend/tests/test_v2_97_route_a_evidence_automation.py`
- Result: passed.
- PRD/spec review: pass for implementation behavior; project-level Route A final acceptance still depends on representative material and human confirmation.
- False-green audit: pass; missing material remains `needs_review`.

