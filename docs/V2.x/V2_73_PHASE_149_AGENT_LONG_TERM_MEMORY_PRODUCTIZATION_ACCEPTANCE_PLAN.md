# V2.73 / Phase 149 Acceptance Plan

## Acceptance Criteria

- Every memory item has `source_artifact_ref`.
- Recommendations have evidence refs or `needs_review`.
- Missing evidence remains visible.

## Commands

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_73_agent_long_term_memory_productization.py backend/tests/test_public_surface_guard.py
```

