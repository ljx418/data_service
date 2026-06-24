# V2.54-V2.58 Phase 130-134 Detailed Implementation Package

## 1. Implementation Boundary

This package is a phase-level implementation baseline. It does not authorize claims beyond the PRD boundary:

- no full call graph;
- no runtime topology;
- no data/control flow;
- no type inference;
- no complete design-intent recovery.

All new artifacts should live under:

```text
workspace/assets/codebase/{codebase_id}/human_agent_deepening/
```

## 2. Shared Preconditions

Before each phase implementation:

1. V2.53 acceptance audit exists and is accepted.
2. Current worktree is clean or changed files are explicitly listed.
3. data_service, HarnessOS, Navia, and codexPat paths are checked.
4. Missing real repo path returns structured_unavailable, not accepted.
5. V2.46-V2.53 artifacts are read-only inputs unless rebuilt by their owning phase.
6. Artifact shape follows `V2_54_58_HUMAN_AGENT_DEEPENING_PHASE_READINESS_AND_SCHEMA_CONTRACTS.md`.
7. Focused tests and real-project E2E follow `V2_54_58_HUMAN_AGENT_DEEPENING_TEST_AND_E2E_MAPPING.md`.

## 3. Phase 130 / V2.54 Human Portal Deepening

Inputs:

- V2.48 portal model and HTML.
- profile onboarding artifacts.
- doc-code alignment / findings.
- closure and acceptance state artifacts.

Outputs:

```text
human_portal_deepening/project_story.json
human_portal_deepening/risk_priority.json
human_portal_deepening/reading_path.json
human_portal_deepening/chart_audit.json
human_portal_deepening/project_portal_v2.html
```

Acceptance:

- New portal sections are evidence-backed.
- No raw Mermaid source is shown as final chart.
- No artifact-external facts are introduced.

## 4. Phase 131 / V2.55 Agent Task Workflow Hardening

Inputs:

- task navigation artifacts.
- playbooks.
- suggested tests.
- token budget / omitted items.

Outputs:

```text
agent_task_workflow/workflow_bundle.json
agent_task_workflow/stop_conditions.json
agent_task_workflow/suggested_tests.json
agent_task_workflow/task_workflow.md
```

Acceptance:

- Every recommendation has evidence_refs or needs_review.
- Stop conditions are explicit.
- Impact candidates are not runtime-call claims.

## 5. Phase 132 / V2.56 Doc-Code Governance Evidence Loop

Inputs:

- doc-code findings.
- governance feedback/rules/reviews/overlay.
- human review artifacts.

Outputs:

```text
doc_code_evidence_loop/evidence_loop.json
doc_code_evidence_loop/decision_history.jsonl
doc_code_evidence_loop/rule_effect.json
doc_code_evidence_loop/evidence_loop_report.md
```

Acceptance:

- approve/revoke behavior is tested.
- original docs and upstream code facts remain unchanged.
- weak/unsupported/contradicted findings remain visible.

## 6. Phase 133 / V2.57 Multi-project Regression Expansion

Inputs:

- V2.52 closure matrix.
- V2.53 acceptance runner output.
- four real repository results.

Outputs:

```text
regression_expansion/expanded_matrix.json
regression_expansion/artifact_diff.json
regression_expansion/failure_diagnosis.json
regression_expansion/regression_report.md
```

Acceptance:

- data_service, HarnessOS, Navia, codexPat have accepted result or structured_unavailable.
- artifact diff and failure diagnosis are visible.
- unavailable is not accepted.

## 7. Phase 134 / V2.58 Developer Onboarding / Restore UX

Inputs:

- V2.53 acceptance commands and runner.
- restore guide.
- dependency baseline.

Outputs:

```text
restore_ux/restore_checklist.md
restore_ux/troubleshooting.md
restore_ux/onboarding_report.json
```

Acceptance:

- Restore guide is executable in a clean local environment.
- TestClient sandbox limitation is documented.
- No private path leaks.
