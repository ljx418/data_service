# V2.102 / Phase 178 Development Plan

## Scope

- Implement bounded project knowledge build orchestration for discovered `code_project` rows.
- Generate `project_build_runs.json`, `portfolio_index.json`, and project brief artifacts.
- Keep context pack, overview, and source trace as optional enhancement evidence, not default full-depth requirements.

## Implementation Targets

- Reuse code asset services for codebase import, snapshot, inventory, and symbols.
- Generate a project brief from persisted code asset artifacts.
- Record deferred or unavailable projects as `needs_review` or `structured_unavailable` with next actions.

## Constraints

- Default build is bounded by `--max-code-projects`; projects outside the bound cannot be counted as accepted.
- Do not claim full call graph, runtime topology, data/control flow, type inference, or full design intent recovery.
- Do not modify `backend/app/api/v1/data_service.py` or `backend/data_service/service.py`.
