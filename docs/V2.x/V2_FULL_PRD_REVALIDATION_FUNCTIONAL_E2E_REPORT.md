# V2 Full PRD Revalidation Functional E2E Report

## Verdict

Pass for current local full functional E2E revalidation.

## Grouped Test Results

| Group | Command scope | Result |
| --- | --- | --- |
| 1 | codebase, overview, context pack, DevWiki | 29 passed, 146 warnings |
| 2 | V2.6-V2.16 architecture and coding-agent foundations | 86 passed, 55 warnings |
| 3 | V2.18-V2.30 platform and architecture intent | 23 passed, 15 warnings |
| 4 | V2.31-V2.45 task navigation, doc-grounded architecture, scale semantic | 20 passed, 20 warnings |
| 5 | V2.46-V2.70 productization, E2E, Portal, dashboard, public surface guard | 57 passed, 41 warnings |

Total grouped result: 215 passed, 277 warnings.

## Infrastructure Checks

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

Result: passed with no output.

## Real data_service E2E

The current local `data_service` repository was imported into a temporary managed workspace and the following artifact chain was built:

- codebase import
- snapshot
- public surface inventory
- symbol index
- evidence trace
- project overview
- Agent context pack
- external E2E
- external repository path binding
- worktree delivery consolidation
- versioned public surface baseline
- Portal V3+
- maintainer dashboard

Observed result:

```text
codebase_id: codebase_data_service
snapshot_file_count: 3143
inventory_surface_count: 669
trace_surface_count: 669
symbol_count: 29644
overview_has_summary: true
context_guidance_count: 1
external_e2e accepted_count: 1
external_e2e unavailable_accepted_count: 0
data_service path binding: accepted
codexPat path binding: structured_unavailable
HarnessOS path binding: structured_unavailable
Navia path binding: structured_unavailable
delivery file_count: 189
delivery safe_to_delete_true_count: 0
delivery exit_gate: needs_review
surface_baseline surface_count: 4
surface_baseline breaking_count: 0
surface_baseline needs_review_count: 0
portal panel_count: 6
portal raw_mermaid_visible: false
dashboard panel_count: 5
dashboard non_accepted_panel_count: 4
dashboard_stage_status: structured_unavailable
```

## Functional Coverage Opinion

- Original V2 PRD core flow is covered by real import, snapshot, inventory, symbols, trace, overview, and context pack E2E.
- Agent productization and later Portal/dashboard stages are covered by focused tests and real persisted artifact build/read paths.
- External projects without real paths are correctly represented as non-accepted.
- Delivery review is not a release or cleanup action; it is advisory evidence.
