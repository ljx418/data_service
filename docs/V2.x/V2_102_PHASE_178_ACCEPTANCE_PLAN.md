# V2.102 / Phase 178 Acceptance Plan

## Acceptance Criteria

- At least one real code project, preferably `/mnt/c/workspace/data_service`, has codebase import, snapshot, inventory/symbols, and project brief refs.
- Every build run has command refs, artifact refs, or structured unresolved reason.
- Deferred projects are `needs_review` and include next action.
- README-only or scan-only evidence is not accepted as project understanding.

## Commands

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_102_project_knowledge_builder.py
PYTHONPATH=backend python3 -m data_service portfolio build --workspace-id v2_101_105_real --root /mnt/c/workspace --limit 40 --max-code-projects 1
```
