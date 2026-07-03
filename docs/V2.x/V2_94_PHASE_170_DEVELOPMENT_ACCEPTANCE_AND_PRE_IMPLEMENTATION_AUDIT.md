# V2.94 / Phase 170 Development, Acceptance and Pre-implementation Audit

Date: 2026-07-03

## Development Plan

- Implement external project path and E2E validator in `real_acceptance_closure`.
- Check `data_service`, `codexPat`, `HarnessOS`, and `Navia` path bindings.
- Execute scoped smoke commands only for readable project paths with explicit command definitions.
- Persist `external_project_closure/path_binding_decision.json`, `external_project_closure/e2e_result_matrix.json`, and `external_project_closure/unavailable_decisions.md`.

## Acceptance Plan

- Each project must have `accepted`, `structured_unavailable`, `structured_blocker`, or `failed`.
- Missing path, permission denied, or missing smoke command cannot be accepted.
- `structured_unavailable` is valid evidence of blocked scope but is not accepted.

## Pre-implementation Audit

- Fatal findings: none.
- Major findings: none.
- Required boundary: do not expose local absolute external paths in public artifacts.
- False-green guard: external project unavailable cannot count toward accepted project count.

Decision: pass for implementation start, not pass for implementation acceptance.
