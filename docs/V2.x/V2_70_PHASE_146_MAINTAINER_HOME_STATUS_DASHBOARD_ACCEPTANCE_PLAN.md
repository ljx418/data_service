# V2.70 Phase 146 Maintainer Home Status Dashboard Acceptance Plan

## Focused Tests

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_70_maintainer_home_status_dashboard.py
```

## Acceptance Criteria

- Dashboard has status panels for path binding, E2E, worktree delivery, surface baseline, and Portal V3.
- Non-accepted statuses remain visible.
- HTML states that statuses come from persisted artifacts.
- Readback returns persisted dashboard artifacts.

## E2E Criteria

Build upstream artifacts first, then build and read the dashboard.
