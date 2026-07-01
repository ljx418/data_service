# V2.81-V2.85 Phase 157-161 Detailed Implementation Package

## 1. Package Purpose

This package decomposes V2.81-V2.85 into implementable subphases. Each subphase must start with a phase-specific development plan, acceptance plan, and pre-implementation audit. Each subphase must end with focused tests, real-data E2E evidence where available, PRD/spec review, false-green audit, and an acceptance audit record.

This package is not implementation evidence.

## 2. Shared Pre-phase Checklist

Before any subphase implementation:

- Confirm the target PRD section and target architecture entity.
- Confirm whether real document materials are available.
- Confirm whether sensitive document text must be redacted.
- Confirm no protected legacy file modification is required.
- Confirm focused test names and artifact schema.
- Close fatal and major audit findings before coding.

If real documents are unavailable, the phase can produce `needs_review` or `structured_unavailable` artifacts but cannot produce accepted real-document UX evidence.

## 3. Phase 157 / V2.81 Real Document Sample and Scenario Contract

### Development Scope

Create a structured contract that lets maintainers and agents distinguish real documents, redacted real documents, development fixtures, and mock-only materials.

Recommended module:

```text
backend/data_service/code_assets/real_document_acceptance/sample_contract.py
```

### Planned Artifacts

```text
real_document_acceptance/sample_contract.json
real_document_acceptance/manual_scenario_plan.md
```

### Implementation Steps

1. Read PRD, target architecture, schema contracts, and V2.76-V2.80 evidence index.
2. Define sample fields: source type, redaction status, acceptance scope, expected paths, privacy warnings, unresolved state.
3. Validate that sample status cannot be `accepted` without real material declaration.
4. Persist artifact refs and unresolved reasons.

### Acceptance Plan

- Focused test: `pytest -q backend/tests/test_v2_81_real_document_sample_contract.py`
- PRD/spec review: verify sample contract maps to maintainer and auditor experiences.
- False-green audit: verify mock-only samples are rejected for accepted status.

### Exit Criteria

- Sample contract can explain what material is used and why it is or is not accepted.
- Missing real material remains `needs_review` or `structured_unavailable`.

## 4. Phase 158 / V2.82 Real Document Import and Wiki Acceptance

### Development Scope

Run or record real document import, parsing, and Wiki artifact review through existing workspace/source capabilities.

Recommended module:

```text
backend/data_service/code_assets/real_document_acceptance/real_document_e2e.py
```

### Planned Artifacts

```text
real_document_acceptance/import_run.json
real_document_acceptance/wiki_artifact_review.json
real_document_acceptance/real_document_e2e_report.md
```

### Implementation Steps

1. Read the V2.81 sample contract.
2. Execute or inspect real source import through existing workspace/source paths.
3. Record import/build status, artifact refs, screenshots, and failure category.
4. Review Wiki/distill artifact quality against the real document scope.
5. Preserve unsupported formats, empty extraction, or weak parsing as unresolved.

### Acceptance Plan

- Focused test: `pytest -q backend/tests/test_v2_82_real_document_import_wiki.py`
- Real E2E: use actual document material or mark unavailable.
- PRD/spec review: verify the maintainer can inspect imported real material and resulting artifacts.
- False-green audit: verify a screenshot alone cannot prove import success.

### Exit Criteria

- Accepted rows include real material, execution evidence, artifact refs, and screenshot or equivalent UI/API evidence.
- Failed or weak import is visible in the report.

## 5. Phase 159 / V2.83 Retrieval, GraphRAG, and Source Trace Acceptance

### Development Scope

Validate that real-document queries can be reviewed with retrieval evidence, GraphRAG boundaries, and source trace.

Recommended module:

```text
backend/data_service/code_assets/real_document_acceptance/retrieval_trace.py
```

### Planned Artifacts

```text
real_document_acceptance/query_trace_review.json
real_document_acceptance/graphrag_review.json
real_document_acceptance/source_trace_review.md
```

### Implementation Steps

1. Read V2.82 import artifacts.
2. Select real-document query scenarios from the manual scenario plan.
3. Capture retrieval result status and evidence refs.
4. Capture GraphRAG output with explicit boundary notes.
5. Verify source trace links the answer to source/unit/evidence or records unresolved reason.

### Acceptance Plan

- Focused test: `pytest -q backend/tests/test_v2_83_retrieval_graphrag_source_trace.py`
- Real E2E: execute representative queries against real imported documents where available.
- PRD/spec review: verify user can understand answer provenance.
- False-green audit: verify GraphRAG is not described as full call graph or runtime topology.

### Exit Criteria

- Accepted query rows have source refs or evidence refs.
- Missing trace blocks accepted source-trace experience.

## 6. Phase 160 / V2.84 Quality Governance and Correction Acceptance

### Development Scope

Validate low-signal findings, feedback, correction plan, and human review state on real-document artifacts.

Recommended module:

```text
backend/data_service/code_assets/real_document_acceptance/quality_acceptance.py
```

### Planned Artifacts

```text
real_document_acceptance/quality_governance_review.json
real_document_acceptance/correction_acceptance_report.md
```

### Implementation Steps

1. Read real-document import and trace review artifacts.
2. Collect quality findings and feedback records.
3. Review correction plan evidence and human review status.
4. Preserve low-signal, weak evidence, and missing review states.

### Acceptance Plan

- Focused test: `pytest -q backend/tests/test_v2_84_quality_governance_real_document.py`
- Real E2E: execute a quality review path on real-document outputs where available.
- PRD/spec review: verify quality problems remain visible to maintainers.
- False-green audit: verify correction recommendations without evidence remain `needs_review`.

### Exit Criteria

- Quality review exposes unresolved quality issues.
- Correction acceptance cannot pass without evidence or human review.

## 7. Phase 161 / V2.85 Release Closure Rerun and Human Sign-off

### Development Scope

Recompute release readiness from V2.76-V2.80 evidence, V2.81-V2.84 real-document acceptance, external project status, warning gate, restore/smoke checks, and human approval.

Recommended module:

```text
backend/data_service/code_assets/real_document_acceptance/release_closure.py
```

### Planned Artifacts

```text
real_document_acceptance/release_closure_rerun.json
real_document_acceptance/final_manual_acceptance_report.md
```

### Implementation Steps

1. Read all V2.81-V2.84 artifacts.
2. Read V2.76-V2.80 evidence and final acceptance report as prior evidence, not new proof.
3. Recheck external project path availability.
4. Recheck warning gate, restore/smoke, and protected file status.
5. Require human approval before final release accepted.

### Acceptance Plan

- Focused test: `pytest -q backend/tests/test_v2_85_release_closure_rerun.py`
- PRD/spec review: verify final readiness reflects all unresolved high-risk items.
- False-green audit: verify unavailable external projects and missing human approval block accepted release.

### Exit Criteria

- Final release accepted only when every required gate is backed by evidence.
- Otherwise final release remains `needs_review`, `structured_unavailable`, or `structured_blocker` with next actions.

## 8. Final Stage Command Plan

```text
pytest -q \
  backend/tests/test_v2_81_real_document_sample_contract.py \
  backend/tests/test_v2_82_real_document_import_wiki.py \
  backend/tests/test_v2_83_retrieval_graphrag_source_trace.py \
  backend/tests/test_v2_84_quality_governance_real_document.py \
  backend/tests/test_v2_85_release_closure_rerun.py \
  backend/tests/test_public_surface_guard.py
python -m compileall backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 9. Final Stage Acceptance Evidence

Final acceptance requires:

- focused test results;
- real-document E2E results or structured unavailable reason;
- PRD/spec review;
- false-green audit;
- public surface guard;
- protected file diff check;
- visual/manual evidence report;
- final acceptance audit report.

No planned row may be converted to accepted without these evidence classes.
