# V2.71 / Phase 147 Development Plan：External Project Binding Closure

## Scope

Implement external project binding closure using real `data_service` evidence and structured non-accepted states for unavailable external projects.

## Implementation Plan

- Add `ExternalProjectClosureService` under `agent_memory_release`.
- Read V2.63 external E2E and V2.67 path binding artifacts when present.
- Build `project_binding_closure.json` and `e2e_closure_report.md`.
- Expose build/read through MCP, CLI, and HTTP.

## Audit Opinion

No fatal or major planning findings. External projects without real readable paths must remain `structured_unavailable` or `structured_blocker`.

