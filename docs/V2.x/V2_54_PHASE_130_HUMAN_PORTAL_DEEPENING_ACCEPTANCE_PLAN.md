# V2.54 / Phase 130 Human Portal Deepening Acceptance Plan

## 1. Acceptance Verdict Target

V2.54 can be accepted only after implementation evidence exists. This plan defines required evidence; it is not acceptance evidence by itself.

## 2. Required Artifacts

Required artifact paths:

```text
workspace/assets/codebase/{codebase_id}/human_agent_deepening/human_portal_deepening/project_story.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/human_portal_deepening/risk_priority.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/human_portal_deepening/reading_path.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/human_portal_deepening/chart_audit.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/human_portal_deepening/project_portal_v2.html
```

Each JSON artifact must follow `V2_54_58_HUMAN_AGENT_DEEPENING_PHASE_READINESS_AND_SCHEMA_CONTRACTS.md`.

## 3. Focused Tests

Planned focused test:

```text
backend/tests/test_v2_54_human_portal_deepening.py
```

Required assertions:

- project story includes accepted baseline, current limits, next actions, and evidence refs;
- risk items include severity, evidence refs or unresolved reason, and allowed status;
- reading path uses repo-relative artifact refs;
- chart audit records `raw_mermaid_visible: false` for accepted portal output;
- Portal V2 HTML does not introduce artifact-external facts;
- public payload contains no local absolute path, secret, token, or raw traceback;
- missing input artifacts become `warnings` or `unresolved`, not accepted evidence.

## 4. Real-project E2E

Required:

- data_service portal build/read result.
- at least one available external project portal build/read result.

Workspace path observations before implementation:

| Display name | Observed local directory | Required handling |
| --- | --- | --- |
| data_service | `/mnt/c/workSpace/data_service` | expected available |
| HarnessOS | `/mnt/c/workSpace/harnessOS` | use actual path casing or record mapping |
| Navia | `/mnt/c/workSpace/navia` | use actual path casing or record mapping |
| codexPat | `/mnt/c/workSpace/codexPat` | expected available |

If an external project cannot be used during E2E, record `structured_unavailable` with the concrete reason. Do not mark it accepted.

## 5. Public Surface Acceptance

The phase must provide or explicitly defer with evidence:

- MCP build/read surface;
- CLI build/read surface;
- HTTP build/read surface;
- parity evidence or a UI-only read exception pointing to equivalent MCP/CLI artifacts.

Public outputs must use repo-relative or artifact-relative paths.

## 6. PRD / Spec Review

Review questions:

- Does the portal let a maintainer see project state, risk, evidence, and next actions?
- Does every new section come from persisted artifacts or explicit evidence refs?
- Does the portal preserve `needs_review`, `structured_unavailable`, and `structured_blocker`?
- Does the portal avoid claiming full design-intent recovery, full call graph, runtime topology, data/control flow, or type inference?

## 7. False-green Audit

Reject acceptance if:

- any section is evidence-free and not marked unresolved;
- a missing artifact is hidden;
- raw Mermaid is treated as final rendered chart;
- mock-only result is used as real project E2E;
- local absolute path, secret, token, or raw traceback leaks;
- unavailable project is counted as accepted.

## 8. Closure Evidence

Before V2.54 coverage rows can move from `planned` to `accepted`, attach:

- artifact path;
- focused test command and result;
- data_service E2E result;
- external project E2E result or `structured_unavailable` rationale;
- PRD/spec review result;
- false-green audit result;
- acceptance audit report path.

## 9. Required Post-implementation Document

After implementation, create:

```text
docs/V2.x/V2_54_PHASE_130_HUMAN_PORTAL_DEEPENING_ACCEPTANCE_AUDIT_REPORT.md
```
