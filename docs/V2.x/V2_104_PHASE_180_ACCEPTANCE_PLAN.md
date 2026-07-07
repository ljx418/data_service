# V2.104 / Phase 180 Acceptance Plan

## Acceptance Criteria

- HTTP read model exposes all fields needed by `/knowledge` portfolio panel.
- `/knowledge?view=portfolio` shows real API-derived statuses and non-accepted states.
- Project rows, media readiness, and release gate findings are visible.
- UI has no fallback success state when artifacts are missing.

## Commands

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_104_knowledge_console_portfolio.py
npm --prefix frontend run build
```
