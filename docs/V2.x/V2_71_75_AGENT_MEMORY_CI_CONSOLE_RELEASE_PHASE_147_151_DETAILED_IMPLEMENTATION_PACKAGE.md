# V2.71-V2.75 / Phase 147-151 Detailed Implementation Package

## 1. Phase Map

| Phase | Version | Name | Primary module |
| --- | --- | --- | --- |
| Phase 147 | V2.71 | External Project Binding Closure | `external_project_closure.py` |
| Phase 148 | V2.72 | CI and Warning Governance | `ci_warning_governance.py` |
| Phase 149 | V2.73 | Agent Long-term Memory Productization | `agent_memory.py` |
| Phase 150 | V2.74 | Interactive Maintainer Console | `interactive_console.py` |
| Phase 151 | V2.75 | Release and Restore Packaging | `release_restore.py` |

## 2. Phase 147 / V2.71

### Development steps

1. Create package skeleton and persistence helpers.
2. Read V2.63 external E2E artifact and V2.67 path binding artifact.
3. Normalize project rows for `data_service`、`codexPat`、`HarnessOS`、`Navia`。
4. Mark `data_service` accepted only when current repo path and persisted artifact evidence exist.
5. Mark missing external paths as `structured_unavailable` with reason and next_action.
6. Write closure JSON and Markdown report.
7. Add MCP/CLI/HTTP build/read parity for external closure.

### Acceptance steps

- Focused test verifies unavailable projects are not accepted.
- Real `data_service` E2E builds closure artifact.
- PRD/spec review confirms user can see status and next action.
- False-green audit checks unavailable-to-accepted conversion does not occur.

## 3. Phase 148 / V2.72

### Development steps

1. Build static CI matrix from current grouped test strategy.
2. Read or accept command result summaries from real test execution.
3. Compute warning budget and observed warning count.
4. Categorize failures into the approved failure categories.
5. Generate CI readiness Markdown report.
6. Add MCP/CLI/HTTP build/read parity for CI governance.

### Acceptance steps

- Focused test verifies warning over-budget cannot become accepted.
- Failure diagnosis uses only approved categories.
- Public surface guard remains in final command plan.
- PRD/spec review confirms maintainer can identify slow tests, warnings, and next action.

## 4. Phase 149 / V2.73

### Development steps

1. Collect persisted artifact refs from codebase intelligence, Agent productization, human deepening, external delivery, and CI governance.
2. Build memory index with stable IDs and source artifact refs.
3. Build evidence index with repo-relative evidence refs.
4. Build acceptance state preserving accepted、needs_review、structured_unavailable、structured_blocker。
5. Build task briefing with recommended reading order, stop conditions, suggested tests.
6. Write retention policy Markdown.
7. Add MCP/CLI/HTTP build/read parity for memory.

### Acceptance steps

- Focused test verifies every memory item has source artifact.
- Recommendations without evidence become `needs_review`.
- No generic chat memory or complete project understanding claim appears.
- PRD/spec review confirms Agent can read memory and evidence boundaries.

## 5. Phase 150 / V2.74

### Development steps

1. Read maintainer dashboard, Portal V3+, external closure, CI governance, memory, release restore artifacts.
2. Build console model with panels and navigation.
3. Generate status panels with status, artifact_ref, evidence_ref or unresolved.
4. Render HTML from structured model only.
5. Add MCP/CLI/HTTP build/read parity for console.

### Acceptance steps

- Focused test verifies panels preserve non-accepted statuses.
- HTML does not hardcode unsupported accepted claims.
- HTML does not show raw Mermaid source.
- PRD/spec review confirms maintainer can see status, evidence, risk, next action, and exit gate.

## 6. Phase 151 / V2.75

### Development steps

1. Read delivery manifest, restore UX, public surface baseline, adapter registry, focused test plan.
2. Build release manifest with source/test/doc/artifact classification.
3. Generate MCP config template without secrets or private absolute paths.
4. Generate smoke commands for MCP、CLI、HTTP、focused tests。
5. Generate restore runbook and release readiness report.
6. Run redaction checks over public artifacts.
7. Add MCP/CLI/HTTP build/read parity for release restore.

### Acceptance steps

- Focused test verifies no secret/token/raw traceback/private venv path.
- Smoke commands include MCP、CLI、HTTP、focused tests。
- Release readiness preserves external unavailable states.
- PRD/spec review confirms maintainer can restore and smoke-test locally.

## 7. Stage-level Closure

Final closure requires:

- Phase 147-151 focused tests pass.
- V2.63-V2.70 regression pass.
- Public surface guard pass.
- Compileall pass.
- `git diff --check` pass.
- Protected legacy diff empty.
- Real `data_service` E2E pass.
- Final acceptance audit report created.

