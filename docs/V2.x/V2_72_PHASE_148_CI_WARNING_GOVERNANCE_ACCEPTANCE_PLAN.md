# V2.72 / Phase 148 Acceptance Plan

## Acceptance Criteria

- Warning budget artifact includes observed count, budget, status, and next action.
- Failure diagnosis categories are from the approved enum only.
- Warning over budget is not accepted.

## Commands

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_72_ci_warning_governance.py backend/tests/test_public_surface_guard.py
```

