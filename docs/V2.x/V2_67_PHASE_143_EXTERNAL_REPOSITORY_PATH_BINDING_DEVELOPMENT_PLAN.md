# V2.67 Phase 143 External Repository Path Binding Development Plan

## Goal

Bind real paths for `data_service`, `codexPat`, `HarnessOS`, and `Navia` so external project E2E can distinguish readable repositories from structured unavailable projects.

## Implementation

- Add a path binding service under `external_e2e_portal_delivery`.
- Accept explicit project path specs, environment-derived paths, and optional search roots.
- Store only artifact refs, source labels, status, and safe fingerprints in public artifacts.
- Do not store local absolute paths in public payloads.
- Expose MCP, CLI, and HTTP build/read parity.

## Stop Conditions

- A missing external repo path must remain `structured_unavailable`.
- Mock-only or undocumented evidence must not be accepted.
- Any absolute path leakage in public artifacts is a blocker.
