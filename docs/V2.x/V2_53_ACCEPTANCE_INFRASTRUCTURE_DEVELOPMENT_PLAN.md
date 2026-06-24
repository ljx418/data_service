# V2.53 Acceptance Infrastructure Development Plan

## Status

Status: implementation plan.

V2.53 hardens the V2.46-V2.52 Agent Productization acceptance baseline. It does not add product capability and does not expand architecture-analysis claims.

## Development Scope

- Add a reproducible test dependency baseline for acceptance runs.
- Add a canonical acceptance runner for V2.46-V2.52 focused tests, `git diff --check`, and `compileall`.
- Add a focused V2.53 test that verifies dependency, documentation, and closure-matrix consistency.
- Reconcile the V2.46-V2.52 coverage matrix row for direct UI route parity with the Phase 129 closure evidence.
- Document the local environment boundary discovered during restore: sandboxed FastAPI `TestClient` can hang, so final acceptance must run in a normal local process or approved non-sandbox execution.

## Out of Scope

- No new HTTP, MCP, or CLI product endpoint.
- No changes to `backend/app/api/v1/data_service.py`.
- No changes to `backend/data_service/service.py`.
- No claim of full call graph, runtime topology, data flow, control flow, type inference, or full design-intent recovery.

## Implementation Notes

- Test-only dependencies live in `backend/requirements-test.txt` and the `test` optional dependency group in `backend/pyproject.toml`; this baseline pins pytest, httpx, FastAPI, and Starlette to avoid public-surface and TestClient drift.
- The canonical runner is `backend/scripts/v2_53_acceptance.py`.
- V2.53 acceptance must keep all accepted claims evidence-backed and must not mark `needs_review`, `structured_unavailable`, or `structured_blocker` as accepted.
