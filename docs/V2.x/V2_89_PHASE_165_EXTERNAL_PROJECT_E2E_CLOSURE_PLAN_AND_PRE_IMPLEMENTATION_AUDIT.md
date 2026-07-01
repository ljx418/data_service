# V2.89 / Phase 165 External Project E2E Closure Plan and Pre-implementation Audit

Date: 2026-07-01

## Development Plan

1. Add `external_project_closure.py` under `backend/data_service/code_assets/real_document_full_corpus_release/`.
2. Track required projects: `data_service`, `codexPat`, `HarnessOS`, and `Navia`.
3. Persist `path_manifest.json`, `project_e2e_records.json`, and `unavailable_diagnosis.md`.
4. Treat the local `data_service` repository as accepted when registered.
5. Keep missing external project paths as `structured_unavailable`.

## Acceptance Plan

- Focused test: `backend/tests/test_v2_89_external_project_e2e_closure.py`.
- Real E2E: verify the current `data_service` repository and classify missing external projects.
- PRD/spec review: unavailable external projects cannot be counted as accepted.
- False-green audit: local absolute paths must not leak into public artifacts.

## Pre-implementation Audit

- Fatal findings: none.
- Major findings: none.
- Minor risk: external project paths must be supplied or confirmed by human operators.
- Decision: pass for phase implementation guidance; not pass for full external-project acceptance while required paths are unavailable.

## Closure Status

Implemented and focused-tested. Real repository external project status remains `structured_unavailable` for `codexPat`, `HarnessOS`, and `Navia`.
