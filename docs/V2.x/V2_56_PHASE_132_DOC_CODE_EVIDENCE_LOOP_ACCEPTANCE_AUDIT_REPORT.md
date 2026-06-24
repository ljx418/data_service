# V2.56 / Phase 132 Doc-Code Evidence Loop Acceptance Audit Report

Date: 2026-06-23

## 1. Acceptance Scope

Accepted phase:

```text
V2.56 / Phase 132 Doc-Code Governance Evidence Loop
```

This report accepts only V2.56.

## 2. Implemented Surfaces

Code modules:

- `backend/data_service/code_assets/human_agent_deepening/evidence_loop.py`
- `backend/scripts/v2_56_real_e2e.py`

Extended files:

- `backend/data_service/code_assets/human_agent_deepening/persistence.py`
- `backend/data_service/mcp_code_human_agent_deepening_tools.py`
- `backend/data_service/cli_code_human_agent_deepening.py`
- `backend/app/api/v1/code_assets_human_agent_deepening.py`
- `backend/tests/test_public_surface_guard.py`

Public surfaces:

- MCP: `knowledge_code_human_agent_deepening_evidence_loop_build`
- MCP: `knowledge_code_human_agent_deepening_evidence_loop_read`
- CLI: `python -m data_service code human-agent-deepening evidence-loop-build`
- CLI: `python -m data_service code human-agent-deepening evidence-loop`
- HTTP: `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/evidence-loop/build`
- HTTP: `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/evidence-loop`

## 3. Accepted Artifacts

```text
workspace/assets/codebase/{codebase_id}/human_agent_deepening/doc_code_evidence_loop/evidence_loop.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/doc_code_evidence_loop/decision_history.jsonl
workspace/assets/codebase/{codebase_id}/human_agent_deepening/doc_code_evidence_loop/rule_effect.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/doc_code_evidence_loop/evidence_loop_report.md
```

## 4. Real-project E2E

Command:

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_56_real_e2e.py
```

Results:

| Project | Result | Evidence summary |
| --- | --- | --- |
| data_service | accepted | finding_count 2; decision_count 2; hash_unchanged true; approve/revoke visible; structured blockers 0 |
| codexPat | accepted | finding_count 2; decision_count 2; hash_unchanged true; approve/revoke visible; structured blockers 0 |

## 5. Focused Tests and Regression Gates

- `backend/tests/test_v2_56_doc_code_evidence_loop.py`: `2 passed`.
- V2.54-V2.56 plus public surface set: `11 passed`.
- V2.46-V2.53 baseline runner: `23 passed`.
- `compileall`: passed.
- `git diff --check`: passed.
- protected legacy file diff: empty.

## 6. Supporting Reviews

- `docs/V2.x/V2_56_PHASE_132_DOC_CODE_EVIDENCE_LOOP_PRD_SPEC_REVIEW_REPORT.md`
- `docs/V2.x/V2_56_PHASE_132_DOC_CODE_EVIDENCE_LOOP_FALSE_GREEN_AUDIT_REPORT.md`

Both passed.

## 7. Acceptance Verdict

V2.56 / Phase 132 Doc-Code Governance Evidence Loop acceptance verdict: accepted.

Rows `V256-001`, `V256-002`, and `V256-003` may move from `planned` to `accepted`.
