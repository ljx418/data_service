# V2.54-V2.58 Full Coverage Matrix

This matrix is the planning baseline for V2.54-V2.58. A row can only move to `accepted` after implementation evidence exists.

| ID | Capability | Phase | Planned Artifact | Acceptance Status | Required Evidence |
| --- | --- | --- | --- | --- | --- |
| V254-001 | Human portal project story | V2.54 | `human_portal_deepening/project_story.json` | accepted | focused test `backend/tests/test_v2_54_human_portal_deepening.py` = 2 passed; real projects data_service and codexPat accepted; acceptance audit `docs/V2.x/V2_54_PHASE_130_HUMAN_PORTAL_DEEPENING_ACCEPTANCE_AUDIT_REPORT.md` |
| V254-002 | Risk priority and next actions | V2.54 | `human_portal_deepening/risk_priority.json` | accepted | evidence refs or unresolved reason covered by focused test; real-project HTML smoke accepted; PRD review `docs/V2.x/V2_54_PHASE_130_HUMAN_PORTAL_DEEPENING_PRD_SPEC_REVIEW_REPORT.md` |
| V254-003 | Portal chart quality audit | V2.54 | `human_portal_deepening/chart_audit.json` | accepted | `raw_mermaid_visible: false` verified; artifact refs and redaction checked; false-green audit `docs/V2.x/V2_54_PHASE_130_HUMAN_PORTAL_DEEPENING_FALSE_GREEN_AUDIT_REPORT.md` |
| V255-001 | Agent task workflow bundle | V2.55 | `agent_task_workflow/{task_id}/workflow_bundle.json` | accepted | focused test `backend/tests/test_v2_55_agent_task_workflow.py` = 2 passed; real projects data_service and codexPat accepted by `backend/scripts/v2_55_real_e2e.py`; acceptance audit `docs/V2.x/V2_55_PHASE_131_AGENT_TASK_WORKFLOW_ACCEPTANCE_AUDIT_REPORT.md` |
| V255-002 | Stop conditions and constraints | V2.55 | `agent_task_workflow/{task_id}/stop_conditions.json` | accepted | no full call graph/runtime claim verified; protected file/mock-only/private path/static-overclaim stop conditions covered; false-green audit `docs/V2.x/V2_55_PHASE_131_AGENT_TASK_WORKFLOW_FALSE_GREEN_AUDIT_REPORT.md` |
| V255-003 | Suggested tests with confidence | V2.55 | `agent_task_workflow/{task_id}/suggested_tests.json` | accepted | evidence_refs or needs_review invariant tested; real E2E bad test status count 0 for data_service and codexPat; PRD review `docs/V2.x/V2_55_PHASE_131_AGENT_TASK_WORKFLOW_PRD_SPEC_REVIEW_REPORT.md` |
| V256-001 | Doc-code evidence loop | V2.56 | `doc_code_evidence_loop/evidence_loop.json` | accepted | focused test `backend/tests/test_v2_56_doc_code_evidence_loop.py` = 2 passed; real projects data_service and codexPat accepted by `backend/scripts/v2_56_real_e2e.py`; acceptance audit `docs/V2.x/V2_56_PHASE_132_DOC_CODE_EVIDENCE_LOOP_ACCEPTANCE_AUDIT_REPORT.md` |
| V256-002 | Decision history | V2.56 | `doc_code_evidence_loop/decision_history.jsonl` | accepted | approve/revoke visible in focused tests and real E2E; PRD review `docs/V2.x/V2_56_PHASE_132_DOC_CODE_EVIDENCE_LOOP_PRD_SPEC_REVIEW_REPORT.md` |
| V256-003 | Rule effect report | V2.56 | `doc_code_evidence_loop/rule_effect.json` | accepted | upstream hash unchanged in focused tests and real E2E; false-green audit `docs/V2.x/V2_56_PHASE_132_DOC_CODE_EVIDENCE_LOOP_FALSE_GREEN_AUDIT_REPORT.md` |
| V257-001 | Expanded regression matrix | V2.57 | `regression_expansion/expanded_matrix.json` | accepted | focused test `backend/tests/test_v2_57_multi_project_regression.py` = 2 passed; real E2E accepted data_service/codexPat and recorded HarnessOS/Navia as structured_unavailable; acceptance audit `docs/V2.x/V2_57_PHASE_133_MULTI_PROJECT_REGRESSION_ACCEPTANCE_AUDIT_REPORT.md` |
| V257-002 | Artifact diff summary | V2.57 | `regression_expansion/artifact_diff.json` | accepted | no mock-only accepted evidence; semantic equivalence not claimed; false-green audit `docs/V2.x/V2_57_PHASE_133_MULTI_PROJECT_REGRESSION_FALSE_GREEN_AUDIT_REPORT.md` |
| V257-003 | Failure diagnosis | V2.57 | `regression_expansion/failure_diagnosis.json` | accepted | allowed failure categories verified; unavailable not accepted; PRD review `docs/V2.x/V2_57_PHASE_133_MULTI_PROJECT_REGRESSION_PRD_SPEC_REVIEW_REPORT.md` |
| V258-001 | Restore checklist | V2.58 | `restore_ux/restore_checklist.md` | accepted | focused test `backend/tests/test_v2_58_restore_ux.py` = 2 passed; real E2E data_service accepted by `backend/scripts/v2_58_real_e2e.py`; acceptance audit `docs/V2.x/V2_58_PHASE_134_RESTORE_UX_ACCEPTANCE_AUDIT_REPORT.md` |
| V258-002 | Acceptance troubleshooting | V2.58 | `restore_ux/troubleshooting.md` | accepted | required failure categories covered; TestClient sandbox limitation documented; false-green audit `docs/V2.x/V2_58_PHASE_134_RESTORE_UX_FALSE_GREEN_AUDIT_REPORT.md` |
| V258-003 | Onboarding report | V2.58 | `restore_ux/onboarding_report.json` | accepted | canonical runner reference verified; `path_redaction_passed: true`; PRD review `docs/V2.x/V2_58_PHASE_134_RESTORE_UX_PRD_SPEC_REVIEW_REPORT.md` |

## Status Rules

- `planned`: planning baseline only; not implementation evidence.
- `accepted`: implementation exists and real evidence is attached.
- `structured_blocker`: implementation attempted, blocker is explicit and evidence-backed.
- `structured_unavailable`: project/provider/environment unavailable with explicit reason; not accepted.
- `needs_review`: evidence or confidence is insufficient for accepted status.
- `out_of_scope`: explicitly excluded by PRD.

## Rejection Rules

- No row may be accepted with mock-only evidence.
- No row may be accepted without artifact path.
- No row may be accepted without focused test result.
- No row may be accepted without real repo result or structured unavailable rationale.
- No row may be accepted if it leaks local absolute path, secret, token, or raw traceback.
- No row may be accepted if it violates the claim boundary.
