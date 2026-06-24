# V2.57 / Phase 133 Multi-project Regression Expansion Development Plan

Date: 2026-06-23

## 1. Phase Goal

V2.57 expands continuous acceptance from a single closure summary into a multi-project regression package with:

- per-project status matrix;
- artifact availability and diff summary;
- failure diagnosis categories;
- markdown regression report.

Unavailable projects must be recorded as `structured_unavailable` and must not be counted as accepted.

## 2. Implementation Scope

New implementation file:

```text
backend/data_service/code_assets/human_agent_deepening/regression.py
```

Existing adapter files may be extended:

```text
backend/data_service/code_assets/human_agent_deepening/persistence.py
backend/data_service/mcp_code_human_agent_deepening_tools.py
backend/data_service/cli_code_human_agent_deepening.py
backend/app/api/v1/code_assets_human_agent_deepening.py
```

Focused test:

```text
backend/tests/test_v2_57_multi_project_regression.py
```

Real E2E script:

```text
backend/scripts/v2_57_real_e2e.py
```

Protected files must not be modified:

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 3. Required Artifacts

```text
workspace/assets/codebase/{codebase_id}/human_agent_deepening/regression_expansion/expanded_matrix.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/regression_expansion/artifact_diff.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/regression_expansion/failure_diagnosis.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/regression_expansion/regression_report.md
```

## 4. Development Steps

1. Add persistence helpers and artifact refs.
2. Implement `MultiProjectRegressionService`.
3. Evaluate `data_service`, `HarnessOS`, `Navia`, and `codexPat` from supplied project paths or local path discovery.
4. Classify each project as `accepted`, `needs_review`, `structured_unavailable`, or `structured_blocker`.
5. Build artifact diff from available V2.54-V2.56 artifacts without claiming semantic equivalence.
6. Build failure diagnosis with allowed categories only.
7. Add MCP/CLI/HTTP build/read parity.
8. Add focused tests for unavailable-not-accepted, mock-only rejection, allowed categories, redaction, and public surface parity.

## 5. Exit Criteria

- Focused tests pass.
- Public surface guard passes.
- V2.46-V2.56 accepted gates still pass.
- Real-project E2E covers `data_service`, `HarnessOS`, `Navia`, and `codexPat` with accepted or structured unavailable results.
- PRD/spec review passes.
- False-green audit passes.
- Acceptance audit is written.
