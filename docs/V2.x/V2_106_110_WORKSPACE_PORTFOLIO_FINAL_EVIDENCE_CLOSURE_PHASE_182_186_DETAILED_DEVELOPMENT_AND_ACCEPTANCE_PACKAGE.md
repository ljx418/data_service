# V2.106-V2.110 Phase 182-186 Detailed Development and Acceptance Package

## 1. Package Status

This package is a phase-level implementation guide. It is not implementation evidence.

It decomposes the V2.106-V2.110 PRD, target architecture, schema contract, test mapping, milestones, gap analysis and drawio into executable phase plans.

## 2. Shared Entry Gate

Before each phase implementation:

1. Read the PRD, target architecture, implementation blueprint, test mapping, coverage matrix and this package.
2. Reconfirm real `/mnt/c/workspace` availability.
3. Confirm no protected legacy file modification is required.
4. Write or update phase-specific development plan, acceptance plan and pre-implementation audit.
5. Close fatal and major findings before code implementation.

Shared no-go:

- Do not mark `needs_review`, `structured_unavailable` or `structured_blocker` as accepted.
- Do not claim full call graph, runtime topology, data/control flow, type inference or complete design-intent recovery.
- Do not use UI-only evidence, report-only evidence or readiness-only evidence as build/source trace acceptance.

## 3. Phase 182 / V2.106：Coverage and Architecture State Closure

Development plan:

- Implement coverage state closure over V2.101-V2.105 accepted/non-accepted rows.
- Implement architecture state closure over target architecture and drawio entity statuses.
- Preserve non-accepted states for OCR, deferred projects, document source trace and headless screenshot evidence.

Artifacts:

```text
coverage_state_closure.json
architecture_state_closure.json
coverage_state_closure_report.md
```

Acceptance plan:

- Focused test: `backend/tests/test_v2_106_portfolio_coverage_state_closure.py`.
- Real input: V2.101-V2.105 coverage matrix, acceptance audit, visual acceptance report and drawio.
- Required result: implemented entities are not shown as planned; blockers remain visible; no non-accepted row is converted to accepted.

False-green checks:

- Reject matrix rows that become accepted without evidence refs.
- Reject architecture reports that hide OCR/source trace/UI evidence gaps.

## 4. Phase 183 / V2.107：OCR and Media Evidence Closure

Development plan:

- Implement OCR/provider health artifact.
- Implement media evidence matrix with row-level format, extractor capability, OCR requirement, failure category and next action.
- Keep media rows non-accepted unless real OCR/text extraction evidence exists.

Artifacts:

```text
ocr_provider_health.json
media_evidence_matrix.json
media_evidence_report.md
```

Acceptance plan:

- Focused test: `backend/tests/test_v2_107_ocr_media_evidence_closure.py`.
- Real input: `/mnt/c/workspace` media/document directories, including images, scans, PDFs and PPT/PPTX samples where present.
- Required result: OCR unavailable rows are `structured_unavailable`; extractable text rows may be accepted only with extraction evidence.

False-green checks:

- Reject OCR-required rows marked accepted without provider evidence.
- Reject sample-only or path-only evidence.

## 5. Phase 184 / V2.108：Full Workspace Project Build Governance

Development plan:

- Implement full build queue over discovered workspace projects.
- Implement cache policy, timeout policy, failure isolation and incremental rerun metadata.
- Implement project build diagnosis with accepted, failed, timeout, skipped, structured_unavailable and needs_review categories.

Artifacts:

```text
full_build_queue.json
project_build_diagnosis.json
full_build_governance_report.md
```

Acceptance plan:

- Focused test: `backend/tests/test_v2_108_full_workspace_build_governance.py`.
- Real input: `/mnt/c/workspace`, with `data_service` as required build sample and external projects as accepted or structured unavailable depending on path/readability.
- Required result: skipped/timeout/deferred projects are visible and not counted as accepted.

False-green checks:

- Reject silent skip.
- Reject timeout counted as accepted.
- Reject project build reports without command refs or structured reason.

## 6. Phase 185 / V2.109：Document Ingest / Query / Source Trace Closure

Development plan:

- Implement document source trace closure over source candidates.
- Bind accepted document rows to source import evidence, query evidence and source trace refs.
- Preserve readiness-only rows as non-accepted.

Artifacts:

```text
document_source_trace_closure.json
document_source_trace_report.md
```

Acceptance plan:

- Focused test: `backend/tests/test_v2_109_document_source_trace_closure.py`.
- Real input: project docs and pure document/media directories under `/mnt/c/workspace`.
- Required result: every accepted document row has import/query/source trace evidence; missing source trace becomes `needs_review` or `structured_unavailable`.

False-green checks:

- Reject readiness-only accepted rows.
- Reject query answers without source trace refs.

## 7. Phase 186 / V2.110：Portfolio Final Release Gate

Development plan:

- Implement final release gate over V2.106-V2.109 artifacts.
- Implement UI evidence capture result with headless screenshot refs or structured unavailable.
- Generate final HTML evidence report and false-green recheck.

Artifacts:

```text
ui_evidence_capture.json
final_release_gate.json
false_green_recheck.md
final_evidence_report.html
```

Acceptance plan:

- Focused test: `backend/tests/test_v2_110_portfolio_final_release_gate.py`.
- Real input: all closure artifacts, `/knowledge` UI endpoint and public surface guard.
- Required result: `portfolio_final_status` follows the worst high-risk status; final accepted appears only when all high-risk rows are accepted or explicitly out of scope with evidence.

False-green checks:

- Reject final accepted while OCR, project build, source trace or UI evidence blockers remain.
- Reject HTML report availability as final acceptance.

## 8. Final Stage Acceptance Command Plan

```text
PYTHONPATH=backend python3 -m pytest -q \
  backend/tests/test_v2_106_portfolio_coverage_state_closure.py \
  backend/tests/test_v2_107_ocr_media_evidence_closure.py \
  backend/tests/test_v2_108_full_workspace_build_governance.py \
  backend/tests/test_v2_109_document_source_trace_closure.py \
  backend/tests/test_v2_110_portfolio_final_release_gate.py \
  backend/tests/test_public_surface_guard.py

PYTHONPATH=backend python3 -m compileall -q backend/data_service backend/app/api backend/tests

npm --prefix frontend run build

git diff --check

git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 9. Final Judgment Rule

The stage can be marked implementation accepted only after all focused tests, real workspace E2E, PRD/spec review, false-green audit and acceptance audit reports pass.

The portfolio can be marked final accepted only when `final_release_gate.json` has no high-risk `needs_review`, `structured_unavailable` or `structured_blocker` rows.

