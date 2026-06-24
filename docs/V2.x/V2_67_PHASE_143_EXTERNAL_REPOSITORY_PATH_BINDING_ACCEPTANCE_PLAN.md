# V2.67 Phase 143 External Repository Path Binding Acceptance Plan

## Focused Tests

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_67_external_repository_path_binding.py
```

## Acceptance Criteria

- Real readable project paths are `accepted`.
- Missing external project paths are `structured_unavailable`.
- Public payloads do not include local absolute paths.
- Readback returns persisted path binding artifacts.

## E2E Criteria

Run against current local `data_service`. External projects without provided paths are not accepted.
