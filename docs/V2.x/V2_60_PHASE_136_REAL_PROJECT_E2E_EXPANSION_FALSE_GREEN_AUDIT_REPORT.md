# V2.60 / Phase 136 Real Project E2E Expansion False-green Audit Report

Date: 2026-06-23

## 1. False-green Checks

| Risk | Check | Result |
| --- | --- | --- |
| Unavailable project counted as accepted | Focused test and real E2E verify unavailable accepted count 0. | pass |
| Mock-only evidence accepted | Focused test verifies mock-only evidence becomes needs_review. | pass |
| Invalid failure category | Real E2E reports invalid category count 0. | pass |
| External path presence overclaimed as full accepted E2E | Real E2E records external full artifact preparation as structured_unavailable. | pass |
| Protected legacy files changed | Protected diff command returned empty output. | pass |

## 2. Verification Evidence

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_60_real_project_e2e_expansion.py
```

Observed result: `2 passed`.

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_60_real_e2e.py
```

Observed result:

- data_service: accepted.
- codexPat: structured_unavailable, not accepted.
- HarnessOS: structured_unavailable, not accepted.
- Navia: structured_unavailable, not accepted.
- unavailable accepted count: 0.
- mock-only accepted count: 0.
- invalid category count: 0.

## 3. Verdict

False-green audit verdict: pass.
