# V2.57 / Phase 133 Multi-project Regression Expansion Acceptance Plan

Date: 2026-06-23

## 1. Required Assertions

Focused tests must verify:

- `expanded_matrix.json` contains exactly the configured project set.
- Each project status is one of `accepted`, `needs_review`, `structured_unavailable`, or `structured_blocker`.
- `structured_unavailable` and `structured_blocker` are never counted as accepted.
- Mock-only evidence is rejected as real E2E.
- `artifact_diff.json` contains baseline/current refs, diff items, status, and false-green risk.
- `failure_diagnosis.json` uses only allowed categories.
- Public payload contains no local absolute path, secret, token, or raw traceback.

## 2. Required Commands

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_57_multi_project_regression.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_public_surface_guard.py
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend
git diff --check
git diff --name-only -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 3. Real-project E2E

Required projects:

- `data_service`
- `HarnessOS`
- `Navia`
- `codexPat`

Each must have an accepted result or a structured unavailable reason. Unavailable projects must not be counted as accepted.

## 4. False-green Rejection Rules

Reject acceptance if:

- any unavailable project is counted as accepted;
- mock-only evidence is marked accepted;
- failure category is outside the allowed set;
- artifact diff claims semantic equivalence without evidence;
- local absolute paths leak into public payloads;
- V2.57 is used as evidence for V2.58.

## 5. Required Post-implementation Documents

```text
docs/V2.x/V2_57_PHASE_133_MULTI_PROJECT_REGRESSION_PRD_SPEC_REVIEW_REPORT.md
docs/V2.x/V2_57_PHASE_133_MULTI_PROJECT_REGRESSION_FALSE_GREEN_AUDIT_REPORT.md
docs/V2.x/V2_57_PHASE_133_MULTI_PROJECT_REGRESSION_ACCEPTANCE_AUDIT_REPORT.md
```
