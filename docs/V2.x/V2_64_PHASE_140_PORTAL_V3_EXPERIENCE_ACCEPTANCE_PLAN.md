# V2.64 / Phase 140 Acceptance Plan：Portal V3+ Experience

## Focused test

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_64_portal_v3_experience.py
```

## Gates

- Portal includes stage overview, external E2E, contract, delivery, risk, and exit status panels.
- Each panel includes status, artifact refs, evidence refs or unresolved reason, and next action.
- `needs_review`, `structured_unavailable`, and `structured_blocker` remain visible.
- HTML does not expose raw Mermaid source, secrets, raw traceback, or local absolute paths.
