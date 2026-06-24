# V2.56 / Phase 132 Doc-Code Evidence Loop False-green Audit Report

Date: 2026-06-23

## 1. False-green Checks

| Risk | Check | Result |
| --- | --- | --- |
| Upstream artifacts mutated | Focused tests and E2E require `hash_unchanged: true`. | pass |
| Revoked decisions hidden | Focused tests and E2E require visible `revoke` action and contradicted status. | pass |
| Unsupported or needs_review status hidden | Focused tests preserve unsupported and missing-input needs_review states. | pass |
| Missing governance inputs accepted | Missing-input test records warnings/unresolved and does not mark accepted. | pass |
| Public payload leaks local path or traceback | Focused tests reject local absolute path and traceback leakage. | pass |
| Documentation claim treated as code fact | Output is labelled governance evidence loop/readback, not proof of code fact. | pass |

## 2. Verification Evidence

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_56_doc_code_evidence_loop.py
```

Observed result: `2 passed`.

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_56_real_e2e.py
```

Observed result:

- `data_service`: accepted; findings 2; decisions 2; hash unchanged; statuses `supported`, `contradicted`; actions `approve`, `revoke`; structured blockers 0.
- `codexPat`: accepted; findings 2; decisions 2; hash unchanged; statuses `supported`, `contradicted`; actions `approve`, `revoke`; structured blockers 0.

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_54_human_portal_deepening.py backend/tests/test_v2_55_agent_task_workflow.py backend/tests/test_v2_56_doc_code_evidence_loop.py backend/tests/test_public_surface_guard.py
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend
git diff --check
git diff --name-only -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

Observed result:

- V2.54-V2.56/public surface set: `11 passed`.
- V2.46-V2.53 baseline runner: `23 passed`.
- `compileall`: passed.
- `git diff --check`: passed.
- protected legacy file diff: empty.

## 3. Verdict

False-green audit verdict: pass.
