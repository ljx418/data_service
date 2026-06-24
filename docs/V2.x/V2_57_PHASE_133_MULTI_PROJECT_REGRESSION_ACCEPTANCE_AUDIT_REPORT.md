# V2.57 / Phase 133 Multi-project Regression Acceptance Audit Report

Date: 2026-06-23

## 1. Acceptance Scope

Accepted phase:

```text
V2.57 / Phase 133 Multi-project Regression Expansion
```

This report accepts only V2.57.

## 2. Implemented Surfaces

Code modules:

- `backend/data_service/code_assets/human_agent_deepening/regression.py`
- `backend/scripts/v2_57_real_e2e.py`

Extended files:

- `backend/data_service/code_assets/human_agent_deepening/persistence.py`
- `backend/data_service/mcp_code_human_agent_deepening_tools.py`
- `backend/data_service/cli_code_human_agent_deepening.py`
- `backend/app/api/v1/code_assets_human_agent_deepening.py`
- `backend/tests/test_public_surface_guard.py`

Public surfaces:

- MCP: `knowledge_code_human_agent_deepening_regression_build`
- MCP: `knowledge_code_human_agent_deepening_regression_read`
- CLI: `python -m data_service code human-agent-deepening regression-build`
- CLI: `python -m data_service code human-agent-deepening regression`
- HTTP: `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/regression/build`
- HTTP: `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/regression`

## 3. Accepted Artifacts

```text
workspace/assets/codebase/{codebase_id}/human_agent_deepening/regression_expansion/expanded_matrix.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/regression_expansion/artifact_diff.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/regression_expansion/failure_diagnosis.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/regression_expansion/regression_report.md
```

## 4. Real-project E2E

Command:

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_57_real_e2e.py
```

Results:

| Project | Result | Evidence summary |
| --- | --- | --- |
| data_service | accepted | artifact refs 7; missing refs 0 |
| codexPat | accepted | artifact refs 7; missing refs 0 |
| HarnessOS | structured_unavailable | bounded E2E time budget; not counted accepted |
| Navia | structured_unavailable | bounded E2E time budget; not counted accepted |

## 5. Focused Tests and Regression Gates

- `backend/tests/test_v2_57_multi_project_regression.py`: `2 passed`.
- V2.54-V2.57 plus public surface set: `13 passed`.
- V2.46-V2.53 baseline runner: `23 passed`.
- `compileall`: passed.
- `git diff --check`: passed.
- protected legacy file diff: empty.

## 6. Supporting Reviews

- `docs/V2.x/V2_57_PHASE_133_MULTI_PROJECT_REGRESSION_PRD_SPEC_REVIEW_REPORT.md`
- `docs/V2.x/V2_57_PHASE_133_MULTI_PROJECT_REGRESSION_FALSE_GREEN_AUDIT_REPORT.md`

Both passed.

## 7. Acceptance Verdict

V2.57 / Phase 133 Multi-project Regression Expansion acceptance verdict: accepted.

Rows `V257-001`, `V257-002`, and `V257-003` may move from `planned` to `accepted`.
