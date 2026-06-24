# V2.59-V2.62 Implementation Blueprint and Acceptance Spec

Date: 2026-06-23

## 1. Purpose

This document connects the V2.59-V2.62 PRD and target architecture to concrete code surfaces, artifacts, tests, real E2E checks, and acceptance evidence.

It is a development baseline, not implementation evidence.

## 2. Code Placement

New implementation should stay under a new namespace:

```text
backend/data_service/code_assets/stabilization_e2e_portal/
  __init__.py
  shared.py
  persistence.py
  public_surface.py
  e2e_expansion.py
  packaging.py
  portal_integration.py
```

Public adapters:

```text
backend/data_service/mcp_code_stabilization_e2e_portal_tools.py
backend/data_service/cli_code_stabilization_e2e_portal.py
backend/app/api/v1/code_assets_stabilization_e2e_portal.py
```

Focused tests:

```text
backend/tests/test_v2_59_public_surface_stabilization.py
backend/tests/test_v2_60_real_project_e2e_expansion.py
backend/tests/test_v2_61_acceptance_packaging.py
backend/tests/test_v2_62_portal_ux_integration.py
```

Real E2E scripts:

```text
backend/scripts/v2_59_real_e2e.py
backend/scripts/v2_60_real_e2e.py
backend/scripts/v2_61_real_e2e.py
backend/scripts/v2_62_real_e2e.py
```

Protected files remain out of scope unless explicitly approved:

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 3. Artifact Layout

Artifacts should be persisted under:

```text
workspace/assets/codebase/{codebase_id}/stabilization_e2e_portal/
  stabilization/
  e2e_expansion/
  packaging/
  portal_integration/
```

All public artifact refs must be artifact URI or repo-relative. Public payloads must not include local absolute path, secret, token, or raw traceback.

## 4. Public Surface Plan

### V2.59 MCP Tools

```text
knowledge_code_stabilization_surface_build
knowledge_code_stabilization_surface_read
```

### V2.60 MCP Tools

```text
knowledge_code_stabilization_e2e_build
knowledge_code_stabilization_e2e_read
```

### V2.61 MCP Tools

```text
knowledge_code_stabilization_package_build
knowledge_code_stabilization_package_read
```

### V2.62 MCP Tools

```text
knowledge_code_stabilization_portal_build
knowledge_code_stabilization_portal_read
```

### CLI Family

```text
python -m data_service code stabilization-e2e-portal surface-build
python -m data_service code stabilization-e2e-portal surface
python -m data_service code stabilization-e2e-portal e2e-build
python -m data_service code stabilization-e2e-portal e2e
python -m data_service code stabilization-e2e-portal package-build
python -m data_service code stabilization-e2e-portal package
python -m data_service code stabilization-e2e-portal portal-build
python -m data_service code stabilization-e2e-portal portal
```

### HTTP Family

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/surface/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/surface
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/e2e/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/e2e
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/package/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/package
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/portal/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/portal
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/stabilization-e2e-portal/portal/view
```

Every build/read pair requires public surface guard coverage.

## 5. Phase Acceptance Spec

| Phase | Required artifacts | Focused acceptance |
| --- | --- | --- |
| V2.59 | `public_surface_snapshot.json`, `public_surface_parity_matrix.json`, `public_surface_drift_report.json`, `migration_notes.md` | snapshot is discovered from current surface registrations; parity matrix covers MCP/CLI/HTTP; drift report does not hide drift |
| V2.60 | `project_e2e_matrix.json`, `project_failure_diagnosis.json`, `project_artifact_availability.json`, `e2e_expansion_report.md` | unavailable projects are not accepted; mock-only evidence is rejected; failure categories are valid |
| V2.61 | `package_manifest.json`, `cleanup_plan.md`, `handoff_checklist.md`, `package_audit_report.md` | cleanup is advisory; no unconfirmed deletion; redaction passes; handoff includes canonical runner |
| V2.62 | `portal_state_summary.json`, `portal_sections.json`, `portal_acceptance_panel.json`, `project_portal_v3.html` | portal uses persisted artifacts only; statuses are distinct; HTML smoke passes |

## 6. Stage Acceptance Command Plan

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_59_public_surface_stabilization.py backend/tests/test_v2_60_real_project_e2e_expansion.py backend/tests/test_v2_61_acceptance_packaging.py backend/tests/test_v2_62_portal_ux_integration.py backend/tests/test_public_surface_guard.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend
git diff --check
git diff --name-only -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

Each phase must also have a real E2E script result and phase acceptance audit before its coverage rows move from `planned`.

## 7. False-green Rejection Rules

Reject acceptance if:

- a snapshot is only a hardcoded expected list;
- unavailable projects are counted as accepted;
- mock-only evidence is used as real E2E;
- cleanup deletes unconfirmed files;
- Portal hides unresolved, needs_review, structured_unavailable, or structured_blocker;
- any public payload leaks local absolute path, secret, token, or raw traceback;
- any document claims full design intent recovery, full call graph, runtime topology, data/control flow, or type inference.
