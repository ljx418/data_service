# V2.71 / Phase 147 Acceptance Plan

## Acceptance Criteria

- `data_service` closure row is accepted only with real evidence refs.
- `codexPat`, `HarnessOS`, and `Navia` are not accepted without real readable paths.
- `unavailable_accepted_count` is 0.
- Public payload contains no local absolute path, secret, token, or raw traceback.

## Commands

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_71_external_project_binding_closure.py backend/tests/test_public_surface_guard.py
```

