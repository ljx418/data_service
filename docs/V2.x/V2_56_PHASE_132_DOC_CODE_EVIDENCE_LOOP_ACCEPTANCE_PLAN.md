# V2.56 / Phase 132 Doc-Code Governance Evidence Loop Acceptance Plan

Date: 2026-06-23

## 1. Required Assertions

Focused tests must verify:

- evidence loop includes findings, decisions, rule effects, and readback;
- approved rules appear as active read-time effects;
- revoked rules remain visible but inactive;
- upstream artifact hashes are unchanged;
- weak, unsupported, contradicted, and needs_review statuses are preserved when present;
- public payload contains no local absolute path, secret, token, or raw traceback;
- missing governance inputs become `warnings` or `unresolved`, not accepted.

## 2. Required Commands

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_56_doc_code_evidence_loop.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_public_surface_guard.py
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend
git diff --check
git diff --name-only -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 3. Real-project E2E

Required:

- data_service evidence loop build/read with at least one governance feedback/rule/review flow.
- one available external project with the same flow or structured unavailable.

## 4. False-green Rejection Rules

Reject acceptance if:

- upstream hashes change;
- revoked decisions disappear;
- unsupported or needs_review findings are hidden;
- unavailable governance inputs are counted as accepted;
- public payload leaks private paths or traceback;
- documentation claims are treated as code facts.

## 5. Required Post-implementation Documents

```text
docs/V2.x/V2_56_PHASE_132_DOC_CODE_EVIDENCE_LOOP_PRD_SPEC_REVIEW_REPORT.md
docs/V2.x/V2_56_PHASE_132_DOC_CODE_EVIDENCE_LOOP_FALSE_GREEN_AUDIT_REPORT.md
docs/V2.x/V2_56_PHASE_132_DOC_CODE_EVIDENCE_LOOP_ACCEPTANCE_AUDIT_REPORT.md
```
