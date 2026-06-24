# V2.58 / Phase 134 Developer Onboarding Restore UX Acceptance Plan

Date: 2026-06-23

## 1. Required Assertions

Focused tests must verify:

- restore checklist references the canonical V2.53 acceptance runner;
- troubleshooting covers dependency drift, sandbox limit, artifact missing, public surface drift, real regression, and needs_review;
- onboarding report includes dependency baseline, acceptance commands, failure diagnosis, and `path_redaction_passed: true`;
- public payload contains no local absolute path, secret, token, or raw traceback;
- TestClient sandbox limitation is documented;
- missing optional docs become warnings/unresolved, not accepted.

## 2. Required Commands

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_58_restore_ux.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_public_surface_guard.py
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend
git diff --check
git diff --name-only -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 3. Real-project E2E

Required:

- Build/read restore UX for data_service.
- Verify canonical commands and failure categories are present.
- Verify redaction pass.

## 4. False-green Rejection Rules

Reject acceptance if:

- restore checklist does not include the canonical runner;
- troubleshooting omits required failure categories;
- `path_redaction_passed` is false;
- raw private path, secret, token, or traceback leaks;
- V2.58 is accepted without focused test and real E2E evidence.

## 5. Required Post-implementation Documents

```text
docs/V2.x/V2_58_PHASE_134_RESTORE_UX_PRD_SPEC_REVIEW_REPORT.md
docs/V2.x/V2_58_PHASE_134_RESTORE_UX_FALSE_GREEN_AUDIT_REPORT.md
docs/V2.x/V2_58_PHASE_134_RESTORE_UX_ACCEPTANCE_AUDIT_REPORT.md
```
