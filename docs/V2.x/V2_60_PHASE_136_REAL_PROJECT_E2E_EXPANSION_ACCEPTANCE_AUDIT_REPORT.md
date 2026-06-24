# V2.60 / Phase 136 Real Project E2E Expansion Acceptance Audit Report

Date: 2026-06-23

## 1. Acceptance Scope

Accepted phase:

```text
V2.60 / Phase 136 Real Project E2E Expansion
```

This report accepts only V2.60.

## 2. Implemented Surfaces

Code modules:

- `backend/data_service/code_assets/stabilization_e2e_portal/e2e_expansion.py`
- `backend/scripts/v2_60_real_e2e.py`

Public surfaces:

- MCP: `knowledge_code_stabilization_e2e_build`
- MCP: `knowledge_code_stabilization_e2e_read`
- CLI: `python -m data_service code stabilization-e2e-portal e2e-build`
- CLI: `python -m data_service code stabilization-e2e-portal e2e`
- HTTP: `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/e2e/build`
- HTTP: `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/e2e`

## 3. Accepted Artifacts

```text
workspace/assets/codebase/{codebase_id}/stabilization_e2e_portal/e2e_expansion/project_e2e_matrix.json
workspace/assets/codebase/{codebase_id}/stabilization_e2e_portal/e2e_expansion/project_failure_diagnosis.json
workspace/assets/codebase/{codebase_id}/stabilization_e2e_portal/e2e_expansion/project_artifact_availability.json
workspace/assets/codebase/{codebase_id}/stabilization_e2e_portal/e2e_expansion/e2e_expansion_report.md
```

## 4. Real-project E2E

Command:

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_60_real_e2e.py
```

Result:

| Project | Result | Evidence summary |
| --- | --- | --- |
| data_service | accepted | bounded real E2E generated V2.60 artifacts |
| codexPat | structured_unavailable | full external artifact preparation not executed in bounded run |
| HarnessOS | structured_unavailable | full external artifact preparation not executed in bounded run |
| Navia | structured_unavailable | full external artifact preparation not executed in bounded run |

## 5. Test and Regression Gates

- V2.60 focused test: `2 passed`.
- V2.59+V2.60+public surface guard: `9 passed`.
- V2.46-V2.53 baseline runner: `23 passed`.
- compileall: passed.
- `git diff --check`: passed.
- protected legacy file diff: empty.

## 6. Supporting Reviews

- `docs/V2.x/V2_60_PHASE_136_REAL_PROJECT_E2E_EXPANSION_PRD_SPEC_REVIEW_REPORT.md`
- `docs/V2.x/V2_60_PHASE_136_REAL_PROJECT_E2E_EXPANSION_FALSE_GREEN_AUDIT_REPORT.md`

Both passed.

## 7. Acceptance Verdict

V2.60 / Phase 136 Real Project E2E Expansion verdict: accepted.

Rows `V260-001`, `V260-002`, and `V260-003` may move from `planned` to `accepted`.
