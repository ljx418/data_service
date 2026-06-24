# V2.59 / Phase 135 Public Surface Stabilization Acceptance Plan

Date: 2026-06-23

## 1. Required Artifacts

```text
stabilization/public_surface_snapshot.json
stabilization/public_surface_parity_matrix.json
stabilization/public_surface_drift_report.json
stabilization/migration_notes.md
```

## 2. Focused Tests

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_59_public_surface_stabilization.py
```

Required assertions:

- snapshot is discovered from current MCP/CLI/HTTP registrations;
- `hardcoded_expected_only` is false;
- parity matrix covers surface, e2e, package, and portal capabilities;
- drift report does not hide drift;
- migration notes are readable;
- public payload is redacted.

## 3. Real E2E

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_59_real_e2e.py
```

Required result:

- data_service accepted;
- all V2.59 artifacts generated and read back;
- no absolute path, secret, token, or raw traceback leak.

## 4. Regression Gates

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_public_surface_guard.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend
git diff --check
git diff --name-only -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 5. False-green Rejection

Reject V2.59 if snapshot is hardcoded only, public surface drift is hidden, or protected legacy files change.
