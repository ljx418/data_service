# V2.54-V2.58 Implementation Blueprint and Acceptance Spec

## 1. Verdict

Status: ready for phase-by-phase implementation. The drawio direction has been accepted by the user.

This document connects the PRD experience goals to the target architecture, concrete implementation surfaces, artifact contracts, focused tests, and acceptance gates. It is a development and acceptance guide only; it does not mark V2.54-V2.58 features as implemented.

Per external review, no more total-control documentation is required before V2.54. The next required work is Phase 130 implementation under the V2.54 phase development plan, acceptance plan, and pre-implementation audit.

## 2. PRD Experience Coverage

| PRD experience | Architecture capability | Implementation surface | Acceptance signal |
| --- | --- | --- | --- |
| Maintainer sees project state, risk, evidence, and next actions | Human Portal Deepening | `human_agent_deepening/human_portal.py` plus HTTP/MCP/CLI read surface | Portal V2 artifact, HTML smoke, evidence refs, no artifact-external facts |
| Agent receives task-aware reading order, bounded impact candidates, suggested tests, and stop conditions | Agent Task Workflow Hardening | `human_agent_deepening/task_workflow.py` plus task build/read tool | Workflow bundle test, recommendations have evidence or `needs_review` |
| Reviewer can trace doc claim, code fact, decision, rule effect, and revocation | Doc-Code Governance Evidence Loop | `human_agent_deepening/evidence_loop.py` | approve/revoke focused test, upstream hashes unchanged |
| Maintainer can compare multi-project availability, diff, trend, and failure diagnosis | Multi-project Regression Expansion | `human_agent_deepening/regression.py` | four project result or `structured_unavailable`, unavailable not accepted |
| New maintainer can restore test environment and diagnose common failures | Developer Onboarding / Restore UX | `human_agent_deepening/restore_ux.py` | restore checklist, troubleshooting coverage, path redaction |

The mapping fully covers the PRD target experiences at planning level. Runtime acceptance still depends on implementation evidence and phase acceptance audits.

## 3. Planned Code Surfaces

New implementation should stay outside legacy large files.

```text
backend/data_service/code_assets/human_agent_deepening/
  __init__.py
  shared.py
  persistence.py
  human_portal.py
  task_workflow.py
  evidence_loop.py
  regression.py
  restore_ux.py
```

Public entry surfaces:

```text
backend/data_service/mcp_code_human_agent_deepening_tools.py
backend/data_service/cli_code_human_agent_deepening.py
backend/app/api/v1/code_assets_human_agent_deepening.py
```

Registry/router wiring may be required in existing small entrypoint files, but the following legacy files remain protected unless the user explicitly approves edits:

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 4. Shared Implementation Rules

- Consume V2.46-V2.53 artifacts through read-only references.
- Write new artifacts only under `workspace/assets/codebase/{codebase_id}/human_agent_deepening/`.
- Keep all public paths repo-relative or artifact-relative.
- Return structured unavailable/blocker states instead of raising raw tracebacks into public payloads.
- Keep `schema_version` as `v2.54-58`.
- Do not infer full call graph, runtime topology, data/control flow, type inference, or full design-intent recovery.
- Do not treat documentation claims as code facts.

## 5. Public Tool and Route Plan

### MCP tools

Planned tool names:

- `knowledge_code_human_agent_deepening_portal_build`
- `knowledge_code_human_agent_deepening_portal_read`
- `knowledge_code_human_agent_deepening_task_workflow_build`
- `knowledge_code_human_agent_deepening_task_workflow_read`
- `knowledge_code_human_agent_deepening_evidence_loop_build`
- `knowledge_code_human_agent_deepening_evidence_loop_read`
- `knowledge_code_human_agent_deepening_regression_build`
- `knowledge_code_human_agent_deepening_regression_read`
- `knowledge_code_human_agent_deepening_restore_build`
- `knowledge_code_human_agent_deepening_restore_read`

### CLI commands

Planned command group:

```text
python -m data_service code human-agent-deepening <command>
```

Planned commands:

- `portal-build`, `portal`
- `task-workflow-build`, `task-workflow`
- `evidence-loop-build`, `evidence-loop`
- `regression-build`, `regression`
- `restore-build`, `restore`

### HTTP routes

Planned route family:

```text
/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/portal
/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/task-workflow
/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/evidence-loop
/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/regression
/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/restore
```

Each route should provide build/read parity unless the phase records a UI-only read exception with equivalent MCP/CLI artifact access.

## 6. Phase Implementation Plan

### V2.54 / Human Portal Deepening

Implementation:

- Read existing portal, profile, architecture evidence, governance state, and acceptance closure artifacts.
- Build project story, risk priority, reading path, chart audit, and Portal V2 HTML.
- Add public read payload that exposes evidence refs, warnings, unresolved items, and next actions.

Focused tests:

- `backend/tests/test_v2_54_human_portal_deepening.py`
- Assert every new section has evidence refs or unresolved reason.
- Assert raw Mermaid source is not shown as the final chart.
- Assert HTML does not introduce artifact-external facts.

Exit evidence:

- data_service portal artifact.
- at least one available external project portal artifact or `structured_unavailable`.
- PRD/spec review, false-green audit, acceptance audit.

### V2.55 / Agent Task Workflow Hardening

Implementation:

- Read task navigation, playbooks, suggested tests, constraints, and acceptance state.
- Build workflow bundle, stop conditions, suggested tests, and task workflow markdown.
- Record omitted items when budget or artifact availability prevents inclusion.

Focused tests:

- `backend/tests/test_v2_55_agent_task_workflow.py`
- Assert recommendations have `evidence_refs` or `needs_review`.
- Assert impact candidates are static candidates, not deterministic runtime calls.
- Assert small token budget records omitted items.

Exit evidence:

- real data_service task workflow.
- one available external project workflow or `structured_unavailable`.
- no full call graph/runtime topology claims.

### V2.56 / Doc-Code Governance Evidence Loop

Implementation:

- Read doc-code findings, governance feedback/rules/reviews/overlay, and human review artifacts.
- Build evidence loop, decision history, rule effect report, and markdown readback.
- Preserve original docs and upstream code facts.

Focused tests:

- `backend/tests/test_v2_56_doc_code_evidence_loop.py`
- Assert approve applies read-time effect.
- Assert revoke removes read-time effect.
- Assert upstream hashes are unchanged.
- Assert weak/unsupported/contradicted statuses remain visible.

Exit evidence:

- governance readback artifact.
- approve/revoke focused test result.
- hash unchanged evidence.

### V2.57 / Multi-project Regression Expansion

Implementation:

- Read V2.52 closure, V2.53 runner output, and per-project artifact availability.
- Build expanded matrix, artifact diff, failure diagnosis, and regression report.
- Classify failure categories without converting unavailable projects into accepted results.

Focused tests:

- `backend/tests/test_v2_57_multi_project_regression.py`
- Assert each project is `accepted`, `needs_review`, `structured_unavailable`, or `structured_blocker`.
- Assert unavailable is never accepted.
- Assert mock-only evidence is rejected as real E2E.

Exit evidence:

- data_service result.
- HarnessOS, Navia, codexPat result or structured unavailable reason.
- false-green audit.

### V2.58 / Developer Onboarding / Restore UX

Implementation:

- Read V2.53 runner, dependency baseline, restore guide, and failure history.
- Build restore checklist, troubleshooting guide, and onboarding report.
- Include sandbox/TestClient limitation and dependency drift diagnosis.

Focused tests:

- `backend/tests/test_v2_58_restore_ux.py`
- Assert canonical runner is referenced.
- Assert failure categories are covered.
- Assert no private path, secret, token, or raw traceback leaks.

Exit evidence:

- restore checklist and troubleshooting artifacts.
- onboarding report with redaction pass.
- acceptance command documentation updated.

## 7. Acceptance Command Plan

The stage acceptance runner should eventually cover V2.46-V2.58:

```bash
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
pytest -q \
  backend/tests/test_v2_54_human_portal_deepening.py \
  backend/tests/test_v2_55_agent_task_workflow.py \
  backend/tests/test_v2_56_doc_code_evidence_loop.py \
  backend/tests/test_v2_57_multi_project_regression.py \
  backend/tests/test_v2_58_restore_ux.py \
  backend/tests/test_public_surface_guard.py
git diff --check
python3 -m compileall backend
```

The exact runner file may be extended or replaced by a V2.58 runner after implementation. Until then, the V2.53 runner remains canonical for the already accepted baseline.

## 8. Coverage Matrix Update Rules

Rows in `V2_54_58_HUMAN_AGENT_DEEPENING_FULL_COVERAGE_MATRIX.md` stay `planned` until all required evidence exists.

To mark a row `accepted`, attach:

- artifact path;
- focused test command/result;
- real project E2E result or structured unavailable rationale;
- PRD/spec review result;
- false-green audit result;
- acceptance audit report path.

Rows with insufficient evidence must remain `needs_review`, `structured_unavailable`, or `structured_blocker`.

## 9. Documentation Sufficiency Assessment

After this blueprint, the documentation set is sufficient to guide V2.54-V2.58 implementation at development-planning level because it now defines:

- PRD target experiences;
- target architecture components and boundaries;
- concrete code surfaces;
- public MCP/CLI/HTTP surfaces;
- artifact layout and schema contracts;
- phase-by-phase implementation steps;
- focused test targets;
- real-project E2E expectations;
- false-green rejection rules;
- acceptance evidence required to close coverage rows.

Remaining limitation:

- It cannot serve as acceptance evidence for implemented behavior. Each phase must still produce real artifacts, tests, E2E results, PRD/spec review, false-green audit, and acceptance audit.
