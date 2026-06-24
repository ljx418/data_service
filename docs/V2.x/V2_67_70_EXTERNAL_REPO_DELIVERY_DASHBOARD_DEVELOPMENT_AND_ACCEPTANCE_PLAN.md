# V2.67-V2.70 External Repository Delivery Dashboard Development and Acceptance Plan

## Scope

This stage extends the accepted V2.63-V2.66 external E2E portal delivery baseline with four focused capabilities:

- V2.67 external repository path binding.
- V2.68 worktree delivery consolidation.
- V2.69 versioned public surface baseline.
- V2.70 maintainer home and status dashboard.

This document is implementation guidance and acceptance evidence routing. It does not claim complete project design-intent recovery, full call graph, runtime topology, data/control flow, or type inference.

## Development Plan

- Reuse `backend/data_service/code_assets/external_e2e_portal_delivery/` and keep new artifacts under the existing managed workspace asset directory.
- Expose build/read parity through MCP, CLI, and HTTP.
- Keep external repositories non-accepted unless a real readable path is provided.
- Generate delivery manifests as advisory review artifacts only; do not delete files.
- Generate public surface baselines from adapter or registry inspection, not documentation claims.
- Build the maintainer dashboard only from persisted artifacts and preserve non-accepted statuses.

## Acceptance Plan

- Run focused tests for V2.67-V2.70 plus public surface guard.
- Run V2.63-V2.66 focused regression.
- Run V2.46-V2.62 baseline regression.
- Run compileall, `git diff --check`, and protected legacy diff check.
- Execute real-data E2E on current `data_service`; external projects remain `structured_unavailable` unless real paths are provided.

## Audit Opinion

Pass for implementation guidance. Not pass for broader product acceptance until focused tests, real-data E2E, PRD/spec review, and false-green audit are completed and recorded.
