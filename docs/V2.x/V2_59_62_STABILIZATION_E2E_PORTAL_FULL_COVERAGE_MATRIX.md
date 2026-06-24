# V2.59-V2.62 Full Coverage Matrix

This matrix is the planning baseline for V2.59-V2.62. A row can only move to `accepted` after implementation evidence exists.

| ID | Capability | Phase | Planned Artifact | Acceptance Status | Required Evidence |
| --- | --- | --- | --- | --- | --- |
| V259-001 | Public surface snapshot | V2.59 | `stabilization/public_surface_snapshot.json` | accepted | focused test `backend/tests/test_v2_59_public_surface_stabilization.py` = 2 passed; real data_service E2E accepted; acceptance audit `docs/V2.x/V2_59_PHASE_135_PUBLIC_SURFACE_STABILIZATION_ACCEPTANCE_AUDIT_REPORT.md` |
| V259-002 | Surface parity matrix | V2.59 | `stabilization/public_surface_parity_matrix.json` | accepted | MCP/CLI/HTTP build-read parity accepted for surface/e2e/package/portal; public surface guard = 5 passed |
| V259-003 | Drift report and migration notes | V2.59 | `stabilization/public_surface_drift_report.json`, `stabilization/migration_notes.md` | accepted | drift categories verified; migration notes generated; false-green audit `docs/V2.x/V2_59_PHASE_135_PUBLIC_SURFACE_STABILIZATION_FALSE_GREEN_AUDIT_REPORT.md` |
| V260-001 | Multi-project E2E matrix | V2.60 | `e2e_expansion/project_e2e_matrix.json` | accepted | focused test `backend/tests/test_v2_60_real_project_e2e_expansion.py` = 2 passed; real E2E accepted data_service and recorded codexPat/HarnessOS/Navia as structured_unavailable; acceptance audit `docs/V2.x/V2_60_PHASE_136_REAL_PROJECT_E2E_EXPANSION_ACCEPTANCE_AUDIT_REPORT.md` |
| V260-002 | Failure diagnosis | V2.60 | `e2e_expansion/project_failure_diagnosis.json` | accepted | allowed categories verified; unavailable accepted count 0; false-green audit `docs/V2.x/V2_60_PHASE_136_REAL_PROJECT_E2E_EXPANSION_FALSE_GREEN_AUDIT_REPORT.md` |
| V260-003 | Artifact availability report | V2.60 | `e2e_expansion/project_artifact_availability.json`, `e2e_expansion/e2e_expansion_report.md` | accepted | artifact refs or structured unavailable reasons recorded; PRD review `docs/V2.x/V2_60_PHASE_136_REAL_PROJECT_E2E_EXPANSION_PRD_SPEC_REVIEW_REPORT.md` |
| V261-001 | Package manifest | V2.61 | `packaging/package_manifest.json` | accepted | focused test `backend/tests/test_v2_61_acceptance_packaging.py` = 2 passed; real E2E data_service accepted; acceptance audit `docs/V2.x/V2_61_PHASE_137_ACCEPTANCE_PACKAGING_ACCEPTANCE_AUDIT_REPORT.md` |
| V261-002 | Cleanup plan | V2.61 | `packaging/cleanup_plan.md` | accepted | cleanup is advisory; `.tmp` classified and not deleted; false-green audit `docs/V2.x/V2_61_PHASE_137_ACCEPTANCE_PACKAGING_FALSE_GREEN_AUDIT_REPORT.md` |
| V261-003 | Handoff checklist and package audit | V2.61 | `packaging/handoff_checklist.md`, `packaging/package_audit_report.md` | accepted | canonical runner and focused command verified; redaction checks covered by PRD review `docs/V2.x/V2_61_PHASE_137_ACCEPTANCE_PACKAGING_PRD_SPEC_REVIEW_REPORT.md` |
| V262-001 | Portal state summary | V2.62 | `portal_integration/portal_state_summary.json` | accepted | focused test `backend/tests/test_v2_62_portal_ux_integration.py` = 2 passed; real E2E data_service accepted; acceptance audit `docs/V2.x/V2_62_PHASE_138_PORTAL_UX_INTEGRATION_ACCEPTANCE_AUDIT_REPORT.md` |
| V262-002 | Portal acceptance panel | V2.62 | `portal_integration/portal_acceptance_panel.json` | accepted | accepted/unavailable/review states rendered distinctly; false-green audit `docs/V2.x/V2_62_PHASE_138_PORTAL_UX_INTEGRATION_FALSE_GREEN_AUDIT_REPORT.md` |
| V262-003 | Portal V3 HTML | V2.62 | `portal_integration/project_portal_v3.html` | accepted | raw Mermaid visible false; real data_service HTML smoke covered by PRD review `docs/V2.x/V2_62_PHASE_138_PORTAL_UX_INTEGRATION_PRD_SPEC_REVIEW_REPORT.md` |

## Status Rules

- `planned`: planning baseline only; not implementation evidence.
- `accepted`: implementation exists and real evidence is attached.
- `structured_blocker`: implementation attempted, blocker is explicit and evidence-backed.
- `structured_unavailable`: project/provider/environment unavailable with explicit reason; not accepted.
- `needs_review`: evidence or confidence is insufficient for accepted status.
- `out_of_scope`: explicitly excluded by PRD.

## Rejection Rules

- No row may be accepted with mock-only evidence.
- No row may be accepted without artifact path.
- No row may be accepted without focused test result.
- No row may be accepted without real repo result or structured rationale.
- No row may be accepted if it leaks local absolute path, secret, token, or raw traceback.
- No row may be accepted if it violates the claim boundary.
