# V2.74 / Phase 150 Acceptance Plan

## Acceptance Criteria

- Each panel has status and artifact/evidence/unresolved data.
- HTML does not hide `needs_review`, `structured_unavailable`, or `structured_blocker`.
- HTML does not hardcode artifact-external accepted claims.

## Commands

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_74_interactive_maintainer_console.py backend/tests/test_public_surface_guard.py
```

