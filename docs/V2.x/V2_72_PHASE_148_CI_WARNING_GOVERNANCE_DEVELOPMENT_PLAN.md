# V2.72 / Phase 148 Development Plan：CI and Warning Governance

## Scope

Implement CI matrix, warning budget, failure diagnosis, and CI readiness artifacts.

## Implementation Plan

- Add `CIWarningGovernanceService`.
- Generate static CI matrix from documented focused/regression commands.
- Accept real command summaries when provided; otherwise preserve historical counts as evidence and mark reviewable items.
- Expose build/read through MCP, CLI, and HTTP.

## Audit Opinion

No fatal or major planning findings. Warning over budget must not be accepted.

