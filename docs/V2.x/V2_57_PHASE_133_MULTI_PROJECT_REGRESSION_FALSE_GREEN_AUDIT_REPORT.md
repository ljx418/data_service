# V2.57 / Phase 133 Multi-project Regression False-green Audit Report

Date: 2026-06-23

## 1. False-green Checks

| Risk | Check | Result |
| --- | --- | --- |
| Unavailable project counted as accepted | Focused test and E2E verify structured unavailable entries are not accepted. | pass |
| Mock-only evidence accepted | Focused test verifies mock-only evidence becomes `needs_review`. | pass |
| Accepted row without evidence | E2E reports accepted_without_evidence_count 0. | pass |
| Invalid failure category | E2E reports invalid_category_count 0. | pass |
| Artifact diff overclaims semantic equivalence | `semantic_equivalence_claimed` is false. | pass |
| Local path or traceback leak | Focused tests reject workspace absolute path and traceback leakage. | pass |

## 2. Verification Evidence

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_57_multi_project_regression.py
```

Observed result: `2 passed`.

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_57_real_e2e.py
```

Observed result:

- `data_service`: accepted, artifact refs 7, missing refs 0.
- `codexPat`: accepted, artifact refs 7, missing refs 0.
- `HarnessOS`: structured_unavailable, not accepted.
- `Navia`: structured_unavailable, not accepted.
- invalid category count 0.
- unavailable accepted count 0.
- accepted without evidence count 0.

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_54_human_portal_deepening.py backend/tests/test_v2_55_agent_task_workflow.py backend/tests/test_v2_56_doc_code_evidence_loop.py backend/tests/test_v2_57_multi_project_regression.py backend/tests/test_public_surface_guard.py
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend
git diff --check
git diff --name-only -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

Observed result:

- V2.54-V2.57/public surface set: `13 passed`.
- V2.46-V2.53 baseline runner: `23 passed`.
- `compileall`: passed.
- `git diff --check`: passed.
- protected legacy file diff: empty.

## 3. Verdict

False-green audit verdict: pass.
