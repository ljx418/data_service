# V2.54-V2.58 Phase Readiness and Schema Contracts

## 1. Purpose

This document freezes the planning-level artifact contracts for V2.54-V2.58 before implementation starts. It supports development planning only; it does not mark any V2.54-V2.58 feature as implemented or accepted.

## 2. Shared Artifact Contract

Every JSON artifact produced in this stage must include:

```json
{
  "schema_version": "v2.54-58",
  "codebase_id": "string",
  "phase": "V2.54|V2.55|V2.56|V2.57|V2.58",
  "generated_at": "ISO-8601 string",
  "artifact_refs": ["repo-relative path"],
  "evidence_refs": ["repo-relative path or artifact id"],
  "warnings": ["string"],
  "unresolved": [
    {
      "id": "string",
      "status": "needs_review|structured_unavailable|structured_blocker",
      "reason": "string"
    }
  ]
}
```

Rules:

- No local absolute path, secret, token, raw traceback, or machine-specific virtualenv path may appear in public artifacts.
- `accepted` is not a valid unresolved status.
- A row may move to `accepted` only after implementation evidence, focused test result, real project result or structured unavailable rationale, and acceptance audit exist.
- Artifact fields may describe static relationships, file-level references, and evidence-backed observations. They must not claim full call graph, runtime topology, data/control flow, type inference, or complete design-intent recovery.

## 3. V2.54 Human Portal Deepening Contracts

### `human_portal_deepening/project_story.json`

Required fields:

- `project_summary`: evidence-backed short summary.
- `accepted_baseline`: V2.46-V2.53 accepted artifact references.
- `current_limits`: known limits and non-claims.
- `next_actions`: evidence-backed next action list.

### `human_portal_deepening/risk_priority.json`

Required fields:

- `risk_items`: list of `id`, `title`, `severity`, `evidence_refs`, `recommended_action`, `status`.
- `status` must be one of `accepted_evidence`, `needs_review`, `structured_unavailable`, `structured_blocker`.
- `accepted_evidence` means the risk item is evidence-backed; it does not mean the feature is accepted.

### `human_portal_deepening/reading_path.json`

Required fields:

- `audience`: `maintainer|agent|reviewer`.
- `ordered_items`: list of repo-relative artifact paths and rationale.
- `omitted_items`: list with reason when token or artifact limits apply.

### `human_portal_deepening/chart_audit.json`

Required fields:

- `charts`: list of chart id, source artifact, rendered artifact, quality status.
- `quality_status`: `rendered|needs_review|structured_unavailable`.
- `raw_mermaid_visible`: boolean; must be false for accepted portal output.

## 4. V2.55 Agent Task Workflow Contracts

### `agent_task_workflow/workflow_bundle.json`

Required fields:

- `task_summary`: user task restatement.
- `reading_order`: evidence-backed artifact and file reading order.
- `impact_candidates`: static file/artifact candidates only.
- `suggested_tests`: references into `suggested_tests.json`.
- `omitted_items`: items skipped due to budget or availability.

### `agent_task_workflow/stop_conditions.json`

Required fields:

- `conditions`: list of `id`, `trigger`, `required_action`.
- Required triggers include unsupported accepted claim, legacy file mutation without approval, mock-only evidence, and private path leak.

### `agent_task_workflow/suggested_tests.json`

Required fields:

- `tests`: list of `command`, `scope`, `confidence`, `evidence_refs`, `status`.
- `status` must be `recommended`, `needs_review`, or `structured_unavailable`.
- A test with no evidence must be `needs_review`.

## 5. V2.56 Doc-Code Governance Evidence Loop Contracts

### `doc_code_evidence_loop/evidence_loop.json`

Required fields:

- `findings`: supported, weak, unsupported, contradicted, or needs_review findings.
- `decisions`: references into `decision_history.jsonl`.
- `rule_effects`: references into `rule_effect.json`.
- `readback`: what public output should show after decisions.

### `doc_code_evidence_loop/decision_history.jsonl`

Each line must be a JSON object with:

- `decision_id`
- `finding_id`
- `action`: `approve|revoke|comment|needs_review`
- `actor`: non-secret local actor label.
- `reason`
- `timestamp`

### `doc_code_evidence_loop/rule_effect.json`

Required fields:

- `rules`: list of rule id, current state, source decision.
- `upstream_hashes`: hashes of original docs/code facts before and after readback.
- `hash_unchanged`: boolean; must be true unless a dedicated approved mutation phase exists.

## 6. V2.57 Multi-project Regression Expansion Contracts

### `regression_expansion/expanded_matrix.json`

Required fields:

- `projects`: `data_service`, `HarnessOS`, `Navia`, `codexPat`.
- `results`: per project status, artifact refs, test command, evidence refs.
- Allowed statuses: `accepted`, `needs_review`, `structured_unavailable`, `structured_blocker`.

### `regression_expansion/artifact_diff.json`

Required fields:

- `baseline_ref`
- `current_ref`
- `diff_items`
- `status`
- `false_green_risk`

### `regression_expansion/failure_diagnosis.json`

Required fields:

- `failures`: list of command, project, category, evidence refs.
- Allowed categories: `dependency_drift`, `sandbox_limit`, `artifact_missing`, `public_surface_drift`, `real_regression`, `needs_review`.

## 7. V2.58 Developer Onboarding / Restore UX Contracts

### `restore_ux/onboarding_report.json`

Required fields:

- `environment_summary`: redacted environment facts.
- `dependency_baseline`: test dependency references.
- `acceptance_commands`: canonical command list.
- `failure_diagnosis`: references to troubleshooting sections.
- `path_redaction_passed`: boolean.

Markdown outputs:

- `restore_ux/restore_checklist.md`
- `restore_ux/troubleshooting.md`

These documents must be executable by a maintainer without relying on local private paths.

## 8. Phase Implementation Readiness

Before implementing any phase:

1. Create or update that phase's development plan, acceptance plan, and pre-implementation audit.
2. Confirm changed files and legacy-file boundary.
3. Confirm real repository availability or record `structured_unavailable`.
4. Freeze focused test names and real project E2E target.
5. Confirm schema compatibility with this document.

## 9. Completion Boundary

This document completes planning support for artifact contracts. It does not replace post-implementation focused tests, real project E2E, PRD/spec review, false-green audit, or acceptance audit.
