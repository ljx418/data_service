# V2.68 Phase 144 Worktree Delivery Consolidation Development Plan

## Goal

Create a reviewable worktree delivery manifest for the current dirty tree so maintainers can distinguish source changes, generated evidence, local temp files, and manual review items.

## Implementation

- Add a worktree delivery consolidation service under `external_e2e_portal_delivery`.
- Read `git status --short` when available and fall back to bounded file listing for non-git fixtures.
- Classify rows as `commit_candidate`, `generated_evidence`, `local_temp`, or `manual_review`.
- Always set `safe_to_delete=false`.
- Expose MCP, CLI, and HTTP build/read parity.

## Stop Conditions

- The service must not delete or rewrite files.
- `.tmp/` and local cache files must not be accepted delivery evidence.
- Manual review rows must remain visible.
