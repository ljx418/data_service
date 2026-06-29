# V2.75 / Phase 151 Acceptance Plan

## Acceptance Criteria

- Redaction check passes.
- Smoke commands cover MCP, CLI, HTTP, and focused tests.
- Release readiness does not convert unavailable external projects to accepted.

## Commands

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_75_release_restore_packaging.py backend/tests/test_public_surface_guard.py
```

