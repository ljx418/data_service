# V2.70 Phase 146 Maintainer Home Status Dashboard Development Plan

## Goal

Build a maintainer home and status dashboard that summarizes external project path binding, real E2E, worktree delivery, public surface baseline, and Portal V3 inherited status.

## Implementation

- Add a dashboard service under `external_e2e_portal_delivery`.
- Read persisted artifacts from V2.63-V2.69.
- Generate a structured home model, status panels, and HTML view.
- Preserve `needs_review`, `structured_unavailable`, and `structured_blocker`.
- Expose MCP, CLI, and HTTP build/read parity plus HTTP HTML view.

## Stop Conditions

- Do not hardcode accepted conclusions in HTML.
- Do not hide unresolved statuses.
- Do not create facts that are absent from persisted artifacts.
