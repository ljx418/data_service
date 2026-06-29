# V2.77 / Phase 153 External Project Real Binding Phase Gate

## Development Plan

- Implement `backend/data_service/code_assets/project_acceptance_hardening/external_project_binding.py`.
- Reconfirm `data_service`, `codexPat`, `HarnessOS`, and `Navia` using real readable paths or structured unavailable records.
- Generate `external_project_binding/project_preflight.json`, `e2e_rerun_records.json`, and `binding_decision_report.md`.
- Expose build/read parity through MCP, CLI, and HTTP.

## Acceptance Plan

- Focused test: `backend/tests/test_v2_77_external_project_real_binding.py`.
- E2E signal: `data_service` must bind to the imported local repository; unavailable external projects remain structured.
- PRD/spec review: no unavailable external project can become accepted.
- False-green audit: mock-only evidence and documentation-only evidence are rejected.

## Pre-implementation Audit

- Fatal findings: none.
- Major findings: none.
- Implementation may start because project binding status rules and evidence boundaries are explicit.
- Boundary: external projects without readable paths must remain `structured_unavailable`.
