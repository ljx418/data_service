# V2.78 / Phase 154 CI Warning Reduction Phase Gate

## Development Plan

- Implement `backend/data_service/code_assets/project_acceptance_hardening/warning_reduction.py`.
- Consume real command summary input when supplied; otherwise use structured fallback records.
- Generate `warning_reduction/warning_inventory.json`, `reduction_plan.json`, `release_warning_gate.json`, and `warning_reduction_report.md`.
- Expose build/read parity through MCP, CLI, and HTTP.

## Acceptance Plan

- Focused test: `backend/tests/test_v2_78_ci_warning_reduction.py`.
- E2E signal: over-budget warning counts must block release acceptance; in-budget counts may pass only with evidence.
- PRD/spec review: warning cleanup is an explicit release gate, not cosmetic output.
- False-green audit: warning overflow cannot be hidden by a summary-level accepted status.

## Pre-implementation Audit

- Fatal findings: none.
- Major findings: none.
- Implementation may start because gate behavior and warning budget rules are defined.
- Boundary: warnings without owner or category remain `needs_review`.
