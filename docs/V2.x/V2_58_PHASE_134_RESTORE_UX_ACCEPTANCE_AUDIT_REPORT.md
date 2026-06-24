# V2.58 / Phase 134 Developer Onboarding Restore UX Acceptance Audit Report

Date: 2026-06-23

## 1. Acceptance Scope

Accepted phase:

```text
V2.58 / Phase 134 Developer Onboarding Restore UX
```

This report accepts only V2.58.

## 2. Implemented Surfaces

Code modules:

- `backend/data_service/code_assets/human_agent_deepening/restore_ux.py`
- `backend/scripts/v2_58_real_e2e.py`

Extended files:

- `backend/data_service/code_assets/human_agent_deepening/persistence.py`
- `backend/data_service/mcp_code_human_agent_deepening_tools.py`
- `backend/data_service/cli_code_human_agent_deepening.py`
- `backend/app/api/v1/code_assets_human_agent_deepening.py`
- `backend/tests/test_public_surface_guard.py`

Public surfaces:

- MCP: `knowledge_code_human_agent_deepening_restore_build`
- MCP: `knowledge_code_human_agent_deepening_restore_read`
- CLI: `python -m data_service code human-agent-deepening restore-build`
- CLI: `python -m data_service code human-agent-deepening restore`
- HTTP: `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/restore/build`
- HTTP: `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/restore`

## 3. Accepted Artifacts

```text
workspace/assets/codebase/{codebase_id}/human_agent_deepening/restore_ux/restore_checklist.md
workspace/assets/codebase/{codebase_id}/human_agent_deepening/restore_ux/troubleshooting.md
workspace/assets/codebase/{codebase_id}/human_agent_deepening/restore_ux/onboarding_report.json
```

## 4. Real-project E2E

Command:

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_58_real_e2e.py
```

Results:

| Project | Result | Evidence summary |
| --- | --- | --- |
| data_service | accepted | canonical runner present; failure categories complete; redaction passed; no absolute path leak |

## 5. Focused Tests and Regression Gates

- `backend/tests/test_v2_58_restore_ux.py`: `2 passed`.
- V2.54-V2.58 plus public surface set: `15 passed`.
- V2.46-V2.53 baseline runner: `23 passed`.
- `compileall`: passed.
- `git diff --check`: passed.
- protected legacy file diff: empty.

## 6. Supporting Reviews

- `docs/V2.x/V2_58_PHASE_134_RESTORE_UX_PRD_SPEC_REVIEW_REPORT.md`
- `docs/V2.x/V2_58_PHASE_134_RESTORE_UX_FALSE_GREEN_AUDIT_REPORT.md`

Both passed.

## 7. Acceptance Verdict

V2.58 / Phase 134 Developer Onboarding Restore UX acceptance verdict: accepted.

Rows `V258-001`, `V258-002`, and `V258-003` may move from `planned` to `accepted`.
