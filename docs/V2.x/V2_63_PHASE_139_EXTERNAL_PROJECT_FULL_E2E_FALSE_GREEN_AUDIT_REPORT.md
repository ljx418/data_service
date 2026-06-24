# V2.63 / Phase 139 False-green Audit Report

## Verdict

Pass.

## Checks

- Mock-only evidence is converted to `needs_review`.
- Missing project paths are converted to `structured_unavailable`.
- `unavailable_accepted_count` remains `0`.
- `mock_only_accepted_count` remains `0`.
- Project rows require evidence refs or unresolved reasons.

## Focused evidence

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_63_external_project_full_e2e.py
```
