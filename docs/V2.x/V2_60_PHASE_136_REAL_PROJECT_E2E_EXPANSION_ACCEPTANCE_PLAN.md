# V2.60 / Phase 136 Real Project E2E Expansion Acceptance Plan

Date: 2026-06-23

## 1. Required Artifacts

```text
e2e_expansion/project_e2e_matrix.json
e2e_expansion/project_failure_diagnosis.json
e2e_expansion/project_artifact_availability.json
e2e_expansion/e2e_expansion_report.md
```

## 2. Focused Tests

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_60_real_project_e2e_expansion.py
```

Required assertions:

- data_service accepted;
- unavailable projects are not accepted;
- mock-only evidence becomes `needs_review`;
- failure categories are valid;
- artifact refs exist for accepted projects or unresolved reason exists for unavailable projects.

## 3. Real E2E

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_60_real_e2e.py
```

Required result:

- data_service accepted.
- codexPat, HarnessOS, and Navia accepted or structured rationale.
- unavailable accepted count is 0.
- mock-only accepted count is 0.

## 4. Regression Gates

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_59_public_surface_stabilization.py backend/tests/test_v2_60_real_project_e2e_expansion.py backend/tests/test_public_surface_guard.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend
git diff --check
git diff --name-only -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 5. False-green Rejection

Reject V2.60 if unavailable projects are counted as accepted, mock-only evidence is accepted, or failure categories are invalid.
