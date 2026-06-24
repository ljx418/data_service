# V2.59-V2.62 Phase 135-138 Detailed Implementation Package

Date: 2026-06-23

## 1. Stage Mapping

| Version | Phase | Name | Primary user-visible result |
| --- | --- | --- | --- |
| V2.59 | Phase 135 | Public Surface Stabilization | Maintainer can inspect stable MCP/CLI/HTTP contracts, drift, and migration notes. |
| V2.60 | Phase 136 | Real Project E2E Expansion | Maintainer can see real multi-project E2E status and failure diagnosis without false acceptance. |
| V2.61 | Phase 137 | Acceptance Artifact Cleanup and Packaging | Maintainer can distinguish deliverable files, local temporary files, and manual-review cleanup items. |
| V2.62 | Phase 138 | Human Portal UX Integration | Maintainer can read one Portal page for contract stability, E2E coverage, restore readiness, delivery readiness, and next actions. |

This package is a development baseline, not implementation evidence.

## 2. Shared Implementation Rules

- New code uses `backend/data_service/code_assets/stabilization_e2e_portal/`.
- New public adapters use the MCP / CLI / HTTP files named in the implementation blueprint.
- New artifacts use `workspace/assets/codebase/{codebase_id}/stabilization_e2e_portal/`.
- No stage may modify `backend/app/api/v1/data_service.py` or `backend/data_service/service.py` unless the user explicitly approves.
- No phase may mark `structured_unavailable`, `structured_blocker`, or `needs_review` as `accepted`.
- No public output may leak local absolute path, secret, token, or raw traceback.
- No phase may claim full design-intent recovery, full call graph, runtime topology, data/control flow, or type inference.

## 3. Phase 135 / V2.59 Public Surface Stabilization

### 3.1 Required planning documents

```text
docs/V2.x/V2_59_PHASE_135_PUBLIC_SURFACE_STABILIZATION_DEVELOPMENT_PLAN.md
docs/V2.x/V2_59_PHASE_135_PUBLIC_SURFACE_STABILIZATION_ACCEPTANCE_PLAN.md
docs/V2.x/V2_59_PHASE_135_PUBLIC_SURFACE_STABILIZATION_PRE_IMPLEMENTATION_AUDIT_REPORT.md
```

### 3.2 Implementation files

```text
backend/data_service/code_assets/stabilization_e2e_portal/shared.py
backend/data_service/code_assets/stabilization_e2e_portal/persistence.py
backend/data_service/code_assets/stabilization_e2e_portal/public_surface.py
backend/data_service/mcp_code_stabilization_e2e_portal_tools.py
backend/data_service/cli_code_stabilization_e2e_portal.py
backend/app/api/v1/code_assets_stabilization_e2e_portal.py
```

### 3.3 Required artifacts

```text
stabilization/public_surface_snapshot.json
stabilization/public_surface_parity_matrix.json
stabilization/public_surface_drift_report.json
stabilization/migration_notes.md
```

### 3.4 Focused tests

```text
backend/tests/test_v2_59_public_surface_stabilization.py
```

Required assertions:

- snapshot is generated from current MCP/CLI/HTTP registries;
- `hardcoded_expected_only` is false;
- parity matrix covers `surface`, `e2e`, `package`, and `portal`;
- drift categories are from the allowed set;
- migration notes include user-facing impact and required follow-up tests;
- public output is redacted.

### 3.5 Real E2E

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_59_real_e2e.py
```

Required result:

- data_service accepted;
- all four V2.59 artifacts generated and readable;
- public surface guard passes;
- no protected legacy file diff.

### 3.6 Required closure documents

```text
docs/V2.x/V2_59_PHASE_135_PUBLIC_SURFACE_STABILIZATION_PRD_SPEC_REVIEW_REPORT.md
docs/V2.x/V2_59_PHASE_135_PUBLIC_SURFACE_STABILIZATION_FALSE_GREEN_AUDIT_REPORT.md
docs/V2.x/V2_59_PHASE_135_PUBLIC_SURFACE_STABILIZATION_ACCEPTANCE_AUDIT_REPORT.md
```

## 4. Phase 136 / V2.60 Real Project E2E Expansion

### 4.1 Required planning documents

```text
docs/V2.x/V2_60_PHASE_136_REAL_PROJECT_E2E_EXPANSION_DEVELOPMENT_PLAN.md
docs/V2.x/V2_60_PHASE_136_REAL_PROJECT_E2E_EXPANSION_ACCEPTANCE_PLAN.md
docs/V2.x/V2_60_PHASE_136_REAL_PROJECT_E2E_EXPANSION_PRE_IMPLEMENTATION_AUDIT_REPORT.md
```

### 4.2 Implementation files

```text
backend/data_service/code_assets/stabilization_e2e_portal/e2e_expansion.py
backend/scripts/v2_60_real_e2e.py
backend/tests/test_v2_60_real_project_e2e_expansion.py
```

### 4.3 Required artifacts

```text
e2e_expansion/project_e2e_matrix.json
e2e_expansion/project_failure_diagnosis.json
e2e_expansion/project_artifact_availability.json
e2e_expansion/e2e_expansion_report.md
```

### 4.4 Required checks

- data_service must be accepted.
- codexPat should be attempted as a real project if path and dependencies are available.
- HarnessOS and Navia should be attempted if available within the bounded E2E budget.
- unavailable projects must be `structured_unavailable` or `structured_blocker`, not `accepted`.
- failure categories must be one of:

```text
dependency_drift
sandbox_limit
path_unavailable
artifact_missing
public_surface_drift
real_regression
needs_review
```

### 4.5 Real E2E

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_60_real_e2e.py
```

Required result:

- accepted projects have artifact refs and no unresolved evidence gap;
- unavailable projects include reason and next action;
- mock-only evidence is rejected.

### 4.6 Required closure documents

```text
docs/V2.x/V2_60_PHASE_136_REAL_PROJECT_E2E_EXPANSION_PRD_SPEC_REVIEW_REPORT.md
docs/V2.x/V2_60_PHASE_136_REAL_PROJECT_E2E_EXPANSION_FALSE_GREEN_AUDIT_REPORT.md
docs/V2.x/V2_60_PHASE_136_REAL_PROJECT_E2E_EXPANSION_ACCEPTANCE_AUDIT_REPORT.md
```

## 5. Phase 137 / V2.61 Acceptance Artifact Cleanup and Packaging

### 5.1 Required planning documents

```text
docs/V2.x/V2_61_PHASE_137_ACCEPTANCE_PACKAGING_DEVELOPMENT_PLAN.md
docs/V2.x/V2_61_PHASE_137_ACCEPTANCE_PACKAGING_ACCEPTANCE_PLAN.md
docs/V2.x/V2_61_PHASE_137_ACCEPTANCE_PACKAGING_PRE_IMPLEMENTATION_AUDIT_REPORT.md
```

### 5.2 Implementation files

```text
backend/data_service/code_assets/stabilization_e2e_portal/packaging.py
backend/scripts/v2_61_real_e2e.py
backend/tests/test_v2_61_acceptance_packaging.py
```

### 5.3 Required artifacts

```text
packaging/package_manifest.json
packaging/cleanup_plan.md
packaging/handoff_checklist.md
packaging/package_audit_report.md
```

### 5.4 Required checks

- manifest classifies source, test, doc, script, evidence, local_tmp, and needs_review entries;
- cleanup plan is advisory by default;
- destructive action is false unless the user explicitly approves;
- handoff checklist includes canonical V2.53 runner and V2.59-V2.62 focused command;
- redaction check passes.

### 5.5 Real E2E

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_61_real_e2e.py
```

Required result:

- data_service package artifacts generated;
- `.tmp/` is classified as local_tmp or needs_review;
- no file is deleted by the E2E script.

### 5.6 Required closure documents

```text
docs/V2.x/V2_61_PHASE_137_ACCEPTANCE_PACKAGING_PRD_SPEC_REVIEW_REPORT.md
docs/V2.x/V2_61_PHASE_137_ACCEPTANCE_PACKAGING_FALSE_GREEN_AUDIT_REPORT.md
docs/V2.x/V2_61_PHASE_137_ACCEPTANCE_PACKAGING_ACCEPTANCE_AUDIT_REPORT.md
```

## 6. Phase 138 / V2.62 Human Portal UX Integration

### 6.1 Required planning documents

```text
docs/V2.x/V2_62_PHASE_138_PORTAL_UX_INTEGRATION_DEVELOPMENT_PLAN.md
docs/V2.x/V2_62_PHASE_138_PORTAL_UX_INTEGRATION_ACCEPTANCE_PLAN.md
docs/V2.x/V2_62_PHASE_138_PORTAL_UX_INTEGRATION_PRE_IMPLEMENTATION_AUDIT_REPORT.md
```

### 6.2 Implementation files

```text
backend/data_service/code_assets/stabilization_e2e_portal/portal_integration.py
backend/scripts/v2_62_real_e2e.py
backend/tests/test_v2_62_portal_ux_integration.py
```

### 6.3 Required artifacts

```text
portal_integration/portal_state_summary.json
portal_integration/portal_sections.json
portal_integration/portal_acceptance_panel.json
portal_integration/project_portal_v3.html
```

### 6.4 Required checks

- Portal reads persisted V2.59-V2.61 artifacts only;
- accepted, needs_review, structured_unavailable, structured_blocker, and out_of_scope are distinct;
- Portal does not show raw Mermaid source;
- each section has artifact refs, evidence refs, or unresolved reason;
- project_portal_v3.html passes real data_service smoke.

### 6.5 Real E2E

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_62_real_e2e.py
```

Required result:

- data_service portal_v3 generated;
- contract stability, E2E coverage, restore readiness, delivery readiness, and next actions are visible;
- unavailable/review states are not rendered as accepted.

### 6.6 Required closure documents

```text
docs/V2.x/V2_62_PHASE_138_PORTAL_UX_INTEGRATION_PRD_SPEC_REVIEW_REPORT.md
docs/V2.x/V2_62_PHASE_138_PORTAL_UX_INTEGRATION_FALSE_GREEN_AUDIT_REPORT.md
docs/V2.x/V2_62_PHASE_138_PORTAL_UX_INTEGRATION_ACCEPTANCE_AUDIT_REPORT.md
```

## 7. Stage Closure

Required closure documents:

```text
docs/V2.x/V2_59_62_STABILIZATION_E2E_PORTAL_FINAL_ACCEPTANCE_AUDIT_REPORT.md
```

Required final commands:

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_59_public_surface_stabilization.py backend/tests/test_v2_60_real_project_e2e_expansion.py backend/tests/test_v2_61_acceptance_packaging.py backend/tests/test_v2_62_portal_ux_integration.py backend/tests/test_public_surface_guard.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend
git diff --check
git diff --name-only -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

Stage closure rejects:

- missing phase acceptance audit;
- missing real E2E or structured rationale;
- unsupported accepted coverage row;
- hidden needs_review / structured_unavailable / structured_blocker;
- protected legacy file diff;
- unresolved fatal or major finding.
