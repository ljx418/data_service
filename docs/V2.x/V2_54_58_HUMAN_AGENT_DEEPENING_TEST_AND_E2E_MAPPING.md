# V2.54-V2.58 Test and Real-project E2E Mapping

## 1. Purpose

This document maps planned capabilities to focused tests and real-project checks. It is a planning artifact only; commands may be adjusted during implementation if code organization requires it.

## 2. Shared Test Baseline

The V2.53 canonical runner remains the baseline restore and regression command:

```bash
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
```

Stage implementation must add focused tests without weakening V2.46-V2.53 acceptance coverage.

## 3. Phase Test Mapping

| Phase | Focused Test Target | Real-project E2E Target | False-green Audit |
| --- | --- | --- | --- |
| V2.54 | `backend/tests/test_v2_54_human_portal_deepening.py` | data_service plus one available external project portal artifact | No raw Mermaid, no artifact-external fact, evidence refs present |
| V2.55 | `backend/tests/test_v2_55_agent_task_workflow.py` | task workflow generated for a real task in data_service and one available external project | No full call graph/runtime claim, low confidence becomes needs_review |
| V2.56 | `backend/tests/test_v2_56_doc_code_evidence_loop.py` | governance readback over real doc-code findings | approve/revoke tested, upstream hashes unchanged |
| V2.57 | `backend/tests/test_v2_57_multi_project_regression.py` | data_service, HarnessOS, Navia, codexPat result or structured_unavailable | unavailable not accepted, mock-only not accepted |
| V2.58 | `backend/tests/test_v2_58_restore_ux.py` | clean restore runbook inspection with canonical runner reference | no private path leak, failure classes covered |

## 4. Real-project Status Semantics

Allowed real-project statuses:

- `accepted`: real artifact and test evidence exists.
- `needs_review`: evidence exists but confidence is insufficient.
- `structured_unavailable`: project, provider, or environment is unavailable with explicit reason.
- `structured_blocker`: implementation or validation was attempted and blocked with evidence.

Rejected closure patterns:

- unavailable project counted as accepted.
- mock-only result counted as real-project E2E.
- doc-only claim counted as code behavior.
- artifact path missing from accepted evidence.

## 5. Minimum Phase Exit Evidence

Each phase must produce:

- focused test command and result;
- real-project E2E command or structured unavailable rationale;
- PRD/spec review result;
- false-green audit result;
- acceptance audit report;
- updated coverage matrix rows with evidence refs.

## 6. Sandbox and Dependency Notes

FastAPI `TestClient` may require non-sandbox execution in the current environment. This is a validation environment constraint, not product evidence. If it occurs during a phase, record it as a test-environment note and rerun through the approved non-sandbox path before closing acceptance.
