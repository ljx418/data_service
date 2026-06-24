# V2.61 / Phase 137 Acceptance Packaging Acceptance Plan

Date: 2026-06-23

## 1. Required Artifacts

```text
packaging/package_manifest.json
packaging/cleanup_plan.md
packaging/handoff_checklist.md
packaging/package_audit_report.md
```

## 2. Focused Tests

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_61_acceptance_packaging.py
```

Required assertions:

- manifest classifies source/test/doc/script/evidence/local_tmp/needs_review where applicable;
- cleanup plan is advisory;
- destructive action is false;
- handoff checklist includes canonical runner and V2.59-V2.62 focused command;
- public payload is redacted.

## 3. Real E2E

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_61_real_e2e.py
```

Required result:

- data_service accepted;
- package artifacts generated;
- `.tmp/` classified as local_tmp or needs_review;
- no deletion occurred.

## 4. False-green Rejection

Reject V2.61 if cleanup deletes unconfirmed files, destructive action is true without explicit approval, or local paths leak.
