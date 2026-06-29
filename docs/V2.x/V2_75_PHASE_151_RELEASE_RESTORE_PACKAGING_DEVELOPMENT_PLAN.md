# V2.75 / Phase 151 Development Plan：Release and Restore Packaging

## Scope

Implement release manifest, MCP config template, smoke commands, restore runbook, and release readiness report.

## Implementation Plan

- Add `ReleaseRestoreService`.
- Read delivery, restore UX, public surface baseline, and Agent memory artifacts.
- Generate redaction-safe public artifacts.
- Expose build/read through MCP, CLI, and HTTP.

## Audit Opinion

No fatal or major planning findings. Release readiness must preserve unavailable external project states.

