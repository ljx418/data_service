# V2.46-V2.52 Phase 123-129 Detailed Implementation Package

## 1. Implementation Boundary

This package turns the V2.46-V2.52 planning baseline into phase-level implementation instructions. It does not authorize claims beyond the PRD boundary:

- no full call graph;
- no data/control flow;
- no production runtime topology;
- no type inference;
- no complete human design-intent recovery.

Every phase must produce persisted artifacts under:

```text
workspace/assets/codebase/{codebase_id}/agent_productization/
```

## 2. Shared Preconditions

Before each phase implementation:

1. `V2_39_45_ARCHITECTURE_SCALE_SEMANTIC_CLOSURE_AUDIT_REPORT.md` exists and has no fatal/major open findings.
2. Current worktree is clean or changed files are explicitly listed.
3. data_service, HarnessOS, Navia, and codexPat paths are checked.
4. Missing real repo path returns structured unavailable, not accepted.
5. Upstream V2 artifacts are treated as read-only inputs unless the owning phase explicitly rebuilds them.

## 3. Phase 123 / V2.46 MCP Productization

Inputs:

- MCP tool registry.
- Existing codebase import/snapshot/overview/context/architecture tools.
- V2.39-V2.45 artifacts.

Outputs:

```text
mcp_usage_guide.json
mcp_tool_catalog_readable.json
mcp_agent_workflows.json
docs/generated/codex_mcp_usage_guide.md
```

Implementation tasks:

1. Build a readable MCP tool catalog from the registry.
2. Define Codex CLI configuration snippets.
3. Define recommended workflows for project onboarding, task context, architecture review, and doc-code governance review.
4. Add structured diagnostics for missing MCP configuration.

Acceptance:

- Tool catalog count equals actual registry count.
- Codex CLI guide has command/config examples.
- Every workflow step has purpose, input, output, and failure handling.
- No unsupported tool is listed as available.

## 4. Phase 124 / V2.47 Project Profile Onboarding

Inputs:

- Snapshot and language/provider facts.
- Document semantics.
- Relationship chain artifacts.
- Existing profile/taxonomy registry.

Outputs:

```text
profile_onboarding/profile_draft.json
profile_onboarding/taxonomy_suggestions.json
profile_onboarding/authority_rule_suggestions.json
profile_onboarding/no_hardcode_audit.json
```

Implementation tasks:

1. Generate profile draft from repository facts and docs.
2. Suggest project-specific terms.
3. Suggest entrypoint/workflow/document authority rules.
4. Run no-hardcode audit against generic extractor modules.

Acceptance:

- data_service, HarnessOS, Navia, and codexPat each produce profile draft or structured unavailable.
- Project-specific terms only appear in profile artifacts.
- Generic modules pass no-hardcode audit.

## 5. Phase 125 / V2.48 Human Architecture Portal

Inputs:

- Overview, graph, document semantics, relationship chains, profile, and context pack artifacts.

Outputs:

```text
human_portal/portal_model.json
human_portal/project_architecture_portal.html
human_portal/charts/*.mmd
human_portal/charts/*.svg
```

Implementation tasks:

1. Build portal model with project one-liner, architecture map, public surfaces, module clusters, target/current/diff, risks, and recommended reading path.
2. Render HTML from persisted portal model only.
3. Render diagrams in place rather than showing raw Mermaid source.
4. Escape all document labels and links.

Acceptance:

- HTML contains visible target/current/diff/risks/reading sections.
- Every chart node resolves to persisted artifact refs.
- No raw Mermaid source is displayed as final chart.
- No absolute local path, secret, token, or raw traceback leaks.

## 6. Phase 126 / V2.49 Task Navigation and Impact v2

Inputs:

- Relationship chain v3.
- Module reading pack.
- Test selection and doc-code findings.
- Token budget artifacts.

Outputs:

```text
task_navigation_v2/task_impact.json
task_navigation_v2/reading_order.json
task_navigation_v2/suggested_tests.json
```

Implementation tasks:

1. Accept a task description.
2. Select relevant capability, surfaces, files, relationship chains, and tests.
3. Produce reading order with token estimates.
4. Produce impact candidates and suggested tests.

Acceptance:

- Each suggested test has evidence or needs_review.
- Impact candidates are never described as deterministic runtime calls.
- Reading order stays within requested budget or records omitted_items.

## 7. Phase 127 / V2.50 Doc-Code Governance Workflow

Inputs:

- Doc-code verification rows.
- Human review findings.
- Existing quality governance primitives.

Outputs:

```text
doc_code_governance/feedback.jsonl
doc_code_governance/rules.jsonl
doc_code_governance/reviews.jsonl
doc_code_governance/plans.jsonl
doc_code_governance/applied_overlay.json
```

Implementation tasks:

1. Map verification findings to governance targets.
2. Support feedback creation.
3. Generate reviewable rules.
4. Support approve/revoke.
5. Apply approved rules at read time only.

Acceptance:

- Approve adds `applied_rules` to read output.
- Revoke removes rule from read output.
- Source docs and upstream artifacts hashes remain unchanged.

## 8. Phase 128 / V2.51 Agent Context Playbooks

Inputs:

- MCP workflows.
- Portal model.
- Task navigation outputs.
- Context pack outputs.

Outputs:

```text
context_playbooks/maintainer.json
context_playbooks/coding_agent.json
context_playbooks/documentation_agent.json
context_playbooks/architecture_reviewer.json
context_playbooks/*.md
```

Implementation tasks:

1. Define role-specific MCP call sequences.
2. Define expected output interpretation.
3. Define stop conditions and false-green warnings.
4. Generate Markdown playbooks.

Acceptance:

- All four roles have JSON and Markdown playbooks.
- Every recommendation has evidence_refs or needs_review.
- Small token budget preserves high-risk evidence or omits the whole recommendation.

## 9. Phase 129 / V2.52 Multi-project Continuous Acceptance

Inputs:

- All V2.46-V2.51 artifacts.
- Real repositories: data_service, HarnessOS, Navia, codexPat.

Outputs:

```text
continuous_acceptance/real_repo_matrix.json
continuous_acceptance/public_contract_parity.json
continuous_acceptance/redaction_audit.json
continuous_acceptance/no_hardcode_audit.json
continuous_acceptance/closure_audit_report.md
```

Implementation tasks:

1. Run the full V2.46-V2.52 flow for each available repository.
2. Record accepted, structured blocker, provider unavailable, needs_review.
3. Run public redaction audit.
4. Run HTTP/MCP/CLI parity audit.
5. Produce closure audit.

Acceptance:

- All accepted rows have artifact path and test command evidence.
- Missing project path is structured unavailable.
- Closure has no open fatal/major finding.

