# V2.59 / Phase 135 Public Surface Stabilization Development Plan

Date: 2026-06-23

## 1. Scope

Implement V2.59 public surface stabilization for the V2.59-V2.62 stage.

## 2. Development Tasks

1. Add `backend/data_service/code_assets/stabilization_e2e_portal/`.
2. Implement public surface snapshot, parity matrix, drift report, and migration notes.
3. Add MCP, CLI, and HTTP build/read surfaces.
4. Add focused tests for service, HTTP, MCP, CLI, redaction, and hardcoded snapshot rejection.
5. Add real data_service E2E script.

## 3. Boundaries

- Do not modify `backend/app/api/v1/data_service.py`.
- Do not modify `backend/data_service/service.py`.
- Do not claim full design recovery, full call graph, runtime topology, data/control flow, or type inference.
- Do not mark `structured_unavailable`, `structured_blocker`, or `needs_review` as accepted.

## 4. Expected User Experience

Maintainers can inspect whether MCP, CLI, and HTTP public surfaces are stable, where drift exists, and which migration notes apply before accepting future changes.
