# V2.69 Phase 145 Public Surface Baseline Versioning Acceptance Plan

## Focused Tests

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_69_public_surface_baseline_versioning.py
```

## Acceptance Criteria

- Baseline source is `adapter_registry_inspection`.
- MCP, CLI, and HTTP surfaces are non-empty.
- Breaking count is zero in the focused local environment.
- Readback returns persisted baseline artifacts.

## E2E Criteria

Run with the current adapter registry and include public surface guard.
