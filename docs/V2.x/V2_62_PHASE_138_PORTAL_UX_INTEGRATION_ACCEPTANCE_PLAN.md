# V2.62 / Phase 138 Portal UX Integration Acceptance Plan

Date: 2026-06-23

## 1. Required Artifacts

```text
portal_integration/portal_state_summary.json
portal_integration/portal_sections.json
portal_integration/portal_acceptance_panel.json
portal_integration/project_portal_v3.html
```

## 2. Focused Tests

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_62_portal_ux_integration.py
```

Required assertions:

- Portal uses persisted V2.59-V2.61 artifacts.
- Statuses remain distinct.
- structured_unavailable is not rendered as accepted.
- HTML smoke passes.
- Raw Mermaid source is absent.

## 3. Real E2E

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_62_real_e2e.py
```

Required result:

- data_service accepted.
- portal_v3 generated.
- status panel contains contract stability, E2E coverage, restore readiness, delivery readiness.
- raw Mermaid visible false.

## 4. False-green Rejection

Reject V2.62 if Portal hides unavailable/review states, creates facts outside persisted artifacts, or exposes raw Mermaid source.
