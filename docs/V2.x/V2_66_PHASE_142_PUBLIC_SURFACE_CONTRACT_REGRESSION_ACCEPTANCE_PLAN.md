# V2.66 / Phase 142 Acceptance Plan：Public Surface Contract Regression

## Focused test

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_66_public_surface_contract_regression.py backend/tests/test_public_surface_guard.py
```

## Gates

- Baseline/current surfaces come from real adapter registries.
- Diff covers MCP, CLI, HTTP, and artifact schema.
- Breaking changes cannot be silently accepted.
