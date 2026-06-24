# V2.69 Phase 145 Public Surface Baseline Versioning Development Plan

## Goal

Create a versioned public surface baseline for MCP, CLI, HTTP, and artifact schema surfaces using live adapter or registry inspection.

## Implementation

- Add a surface baseline service under `external_e2e_portal_delivery`.
- Reuse registry inspection from the V2.66 contract regression implementation.
- Output baseline version, diff summary, and markdown report.
- Treat missing surfaces as `needs_review`.
- Expose MCP, CLI, and HTTP build/read parity.

## Stop Conditions

- Do not build a baseline from documentation claims alone.
- Do not silently accept breaking or missing public surface changes.
