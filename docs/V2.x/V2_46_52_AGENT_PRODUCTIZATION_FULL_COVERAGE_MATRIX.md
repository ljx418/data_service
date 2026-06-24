# V2.46-V2.52 Full Coverage Matrix

This matrix is a closure scaffold. A row can only be marked accepted after implementation evidence exists.

| ID | Capability | Phase | Planned Artifact | Acceptance Status | Required Evidence |
| --- | --- | --- | --- | --- | --- |
| V246-001 | MCP tool catalog readable output | 123 | `mcp_tool_catalog_readable.json` | accepted | `pytest -q backend/tests/test_v2_46_agent_productization.py backend/tests/test_public_surface_guard.py`; `V2_46_PHASE_123_MCP_PRODUCTIZATION_ACCEPTANCE_AUDIT_REPORT.md` |
| V246-002 | Codex CLI MCP usage guide | 123 | `codex_mcp_usage_guide.md` | accepted | artifact inspection and `V2_46_PHASE_123_MCP_PRODUCTIZATION_ACCEPTANCE_AUDIT_REPORT.md` |
| V246-003 | Agent MCP workflow playbook | 123 | `mcp_agent_workflows.json` | accepted | workflow count, missing-tool unresolved, `V2_46_PHASE_123_MCP_PRODUCTIZATION_ACCEPTANCE_AUDIT_REPORT.md` |
| V247-001 | Project profile draft | 124 | `profile_draft.json` | accepted | `pytest -q backend/tests/test_v2_47_profile_onboarding.py backend/tests/test_public_surface_guard.py`; four-project E2E; `V2_47_PHASE_124_PROFILE_ONBOARDING_ACCEPTANCE_AUDIT_REPORT.md` |
| V247-002 | Taxonomy suggestions | 124 | `taxonomy_suggestions.json` | accepted | suggestions with repo-relative evidence refs; four-project E2E; `V2_47_PHASE_124_PROFILE_ONBOARDING_ACCEPTANCE_AUDIT_REPORT.md` |
| V247-003 | No-hardcode audit | 124 | `no_hardcode_audit.json` | accepted | production-module no-hardcode audit passed for data_service/HarnessOS/Navia/codexPat; `V2_47_PHASE_124_PROFILE_ONBOARDING_ACCEPTANCE_AUDIT_REPORT.md` |
| V248-001 | Human portal model | 125 | `portal_model.json` | accepted | `pytest -q backend/tests/test_v2_48_human_portal.py backend/tests/test_public_surface_guard.py`; four-project E2E; `V2_48_PHASE_125_HUMAN_PORTAL_ACCEPTANCE_AUDIT_REPORT.md` |
| V248-002 | Human portal HTML | 125 | `project_architecture_portal.html` | accepted | HTML inline SVG smoke; no raw Mermaid source; `V2_48_PHASE_125_HUMAN_PORTAL_ACCEPTANCE_AUDIT_REPORT.md` |
| V248-003 | Chart integrity | 125 | `charts/*` | accepted | portal model node/edge consistency test; `V2_48_PHASE_125_HUMAN_PORTAL_ACCEPTANCE_AUDIT_REPORT.md` |
| V248-004 | Direct UI route parity or exception | 125/129 | `public_contract_parity.json` | accepted | Historical Phase 125 blocker closed by Phase 129 parity / UI-only read exception evidence; `V2_52_PHASE_129_CONTINUOUS_ACCEPTANCE_ACCEPTANCE_AUDIT_REPORT.md` |
| V249-001 | Task reading order | 126 | `reading_order.json` | accepted | `pytest -q backend/tests/test_v2_49_task_navigation.py backend/tests/test_public_surface_guard.py`; four-project E2E; `V2_49_PHASE_126_TASK_NAVIGATION_ACCEPTANCE_AUDIT_REPORT.md` |
| V249-002 | Impact candidates | 126 | `task_impact.json` | accepted | forbidden claim count 0; heuristic candidate boundary; `V2_49_PHASE_126_TASK_NAVIGATION_ACCEPTANCE_AUDIT_REPORT.md` |
| V249-003 | Suggested tests | 126 | `suggested_tests.json` | accepted | evidence refs or needs_review verified; `V2_49_PHASE_126_TASK_NAVIGATION_ACCEPTANCE_AUDIT_REPORT.md` |
| V250-001 | Governance feedback | 127 | `feedback.jsonl` | accepted | `pytest -q backend/tests/test_v2_50_governance_workflow.py backend/tests/test_public_surface_guard.py`; four-project E2E; `V2_50_PHASE_127_GOVERNANCE_WORKFLOW_ACCEPTANCE_AUDIT_REPORT.md` |
| V250-002 | Rule review | 127 | `rules.jsonl`, `reviews.jsonl` | accepted | approve/revoke behavior verified; `V2_50_PHASE_127_GOVERNANCE_WORKFLOW_ACCEPTANCE_AUDIT_REPORT.md` |
| V250-003 | Read-time overlay | 127 | `applied_overlay.json` | accepted | source artifact hash unchanged; `V2_50_PHASE_127_GOVERNANCE_WORKFLOW_ACCEPTANCE_AUDIT_REPORT.md` |
| V251-001 | Maintainer playbook | 128 | `maintainer.json/.md` | accepted | four real repos generated role artifact, evidence invariant passed, `V2_51_PHASE_128_AGENT_PLAYBOOKS_ACCEPTANCE_AUDIT_REPORT.md` |
| V251-002 | Coding agent playbook | 128 | `coding_agent.json/.md` | accepted | task context workflow with evidence/needs_review invariant, token budget test passed |
| V251-003 | Documentation agent playbook | 128 | `documentation_agent.json/.md` | accepted | doc-code review workflow with HTTP/MCP/CLI parity |
| V251-004 | Architecture reviewer playbook | 128 | `architecture_reviewer.json/.md` | accepted | target/current/diff workflow, Markdown/JSON readback and redaction passed |
| V252-001 | Real repo matrix | 129 | `real_repo_matrix.json` | accepted | data_service / HarnessOS / Navia / codexPat accepted, 6 rows each, `V2_52_PHASE_129_CONTINUOUS_ACCEPTANCE_ACCEPTANCE_AUDIT_REPORT.md` |
| V252-002 | Public contract parity | 129 | `public_contract_parity.json` | accepted | HTTP/MCP/CLI stable fields covered by focused tests and closure parity summary |
| V252-003 | Public redaction audit | 129 | `redaction_audit.json` | accepted | no absolute path/secret/raw traceback leak in closure payloads |
| V252-004 | Closure audit | 129 | `closure_audit_report.md` | accepted | no fatal/major finding across four real repos |
| V252-005 | Accepted implementation evidence audit | 129 | `closure_audit_report.md` | accepted | every accepted row has artifact evidence and real repo result |

## Status Rules

- `accepted`: implementation exists and real evidence is attached.
- `structured_blocker`: implementation attempted, blocker is explicit and evidence-backed.
- `provider_unavailable`: provider/config/project unavailable, not accepted.
- `not_implemented`: no implementation evidence.
- `out_of_scope`: explicitly excluded by PRD.
- `planned`: planning baseline only; not implementation evidence.
- `needs_review`: evidence or confidence is insufficient for accepted status.

## Rejection Rules

- No row may be accepted with mock-only evidence.
- No row may be accepted without artifact path.
- No row may be accepted without test command and test result.
- No row may be accepted without real repo result or structured unavailable rationale.
- No row may be accepted without acceptance audit ref.
- No row may be accepted if public payload leaks local absolute path.
- No row may be accepted if it violates PRD boundaries.
- No direct UI route may be accepted without parity evidence or documented UI-only exception pointing to readback artifacts.
