# V2.66 / Phase 142 Development Plan：Public Surface Contract Regression

## Goal

Build contract regression artifacts from real MCP, CLI, HTTP, and artifact schema registration surfaces.

## Implementation

- Use `PublicSurfaceContractRegressionService`.
- Inspect real adapter registries, not documentation.
- Generate contract baseline, diff, compatibility report, and diagnosis.
- Mark missing or breaking surface as `needs_review` or `structured_blocker`.
