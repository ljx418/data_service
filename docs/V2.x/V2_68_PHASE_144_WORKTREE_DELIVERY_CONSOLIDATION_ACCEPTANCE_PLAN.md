# V2.68 Phase 144 Worktree Delivery Consolidation Acceptance Plan

## Focused Tests

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_68_worktree_delivery_consolidation.py
```

## Acceptance Criteria

- Delivery manifest contains classified worktree rows.
- `safe_to_delete_true_count` is zero.
- Cleanup plan states that deletion is not authorized.
- Readback returns persisted delivery review artifacts.

## E2E Criteria

Run against the current data_service worktree and preserve dirty-tree review status.
