# V2.101 / Phase 177 Acceptance Plan

## Acceptance Criteria

- Real `/mnt/c/workspace` scan produces `project_registry.json`.
- `data_service` is classified as `code_project`.
- At least one document/media directory is classified as `doc_project` or `media_corpus` when present.
- Ignored/cache/generated directories carry an ignored reason.
- No `needs_review` or `structured_unavailable` row is counted as accepted.

## Commands

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_101_workspace_portfolio_discovery.py
PYTHONPATH=backend python3 -m data_service portfolio scan --workspace-id v2_101_105_real --root /mnt/c/workspace
```
