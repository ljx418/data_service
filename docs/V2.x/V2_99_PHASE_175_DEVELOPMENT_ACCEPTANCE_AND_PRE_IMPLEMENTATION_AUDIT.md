# V2.99 / Phase 175 External Project E2E Governance Plan, Acceptance, and Audit

## Development Plan

- Implement `ExternalProjectPathRegistry` under `backend/data_service/code_assets/automated_evidence_closure/`.
- Persist `external_path_registry/project_paths.json`, `project_smoke_matrix.json`, and `unavailable_resolution.md`.
- Track `data_service`, `codexPat`, `HarnessOS`, and `Navia` as explicit project rows.

## Acceptance Plan

- Readable project path plus real smoke command can become `accepted`.
- Missing or unreadable path must be `structured_unavailable`, not `accepted`.
- Failed smoke command must be `failed`; timed out or unstartable command is `structured_blocker`.
- Public artifacts may include redacted path refs only, not local absolute paths.

## Pre-implementation Audit

- Fatal findings: none.
- Major findings: none.
- Guardrails: unavailable external projects cannot be counted as accepted; local path values are redacted from public artifacts.

## Implementation Acceptance Result

- Focused test: `PYTHONPATH=backend pytest -q backend/tests/test_v2_99_external_project_e2e_governance.py`
- Result: passed.
- PRD/spec review: pass for implementation behavior.
- False-green audit: pass; missing external paths remain `structured_unavailable`.

