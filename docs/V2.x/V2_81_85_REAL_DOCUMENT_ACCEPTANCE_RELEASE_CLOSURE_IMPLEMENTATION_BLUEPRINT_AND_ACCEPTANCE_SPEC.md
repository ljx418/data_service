# V2.81-V2.85 Implementation Blueprint and Acceptance Spec

## 1. Purpose

This document connects the V2.81-V2.85 PRD, target architecture, schemas, and acceptance plan to concrete implementation surfaces. It is an implementation baseline, not implementation evidence.

The stage objective is to close the known acceptance gap: previous visual and mind-map acceptance was directionally acceptable, but did not use real document materials. Therefore real-document user experience remains `needs_review` until it is rerun with real documents and auditable evidence.

## 2. Non-negotiable Boundaries

- Do not claim complete recovery of complex project design intent.
- Do not claim full call graph, runtime topology, data/control flow, or type inference.
- Do not treat documentation claims as code facts.
- Do not convert `needs_review`, `structured_unavailable`, or `structured_blocker` to `accepted` without new real evidence.
- Do not use mock-only materials as real-document acceptance evidence.
- Do not modify `backend/app/api/v1/data_service.py` or `backend/data_service/service.py` unless explicitly approved by the user.

## 3. Recommended Code Placement

If this stage enters implementation, new code should live in an isolated package:

```text
backend/data_service/code_assets/real_document_acceptance/
  __init__.py
  shared.py
  persistence.py
  sample_contract.py
  real_document_e2e.py
  retrieval_trace.py
  quality_acceptance.py
  release_closure.py
```

Recommended adapters:

```text
backend/data_service/mcp_code_real_document_acceptance_tools.py
backend/data_service/cli_code_real_document_acceptance.py
backend/app/api/v1/code_assets_real_document_acceptance.py
```

Protected legacy files remain read-only for this stage:

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 4. Shared Artifact Location

All generated evidence should be written under a stage-specific path:

```text
workspace/assets/codebase/{codebase_id}/real_document_acceptance/
```

Public artifact references must be repo-relative paths or artifact URIs. Public artifacts must not contain local absolute paths, secrets, tokens, private keys, raw traceback, private virtualenv paths, or sensitive real document text.

## 5. Capability Blueprint

### 5.1 Real Document Sample Contract

Module:

```text
sample_contract.py
```

Inputs:

- workspace id and codebase id;
- real document source description;
- redaction and privacy declaration;
- target user scenarios;
- screenshot and evidence requirements.

Outputs:

```text
real_document_acceptance/sample_contract.json
real_document_acceptance/manual_scenario_plan.md
```

Acceptance rules:

- If no valid real document material is available, status must be `needs_review` or `structured_unavailable`.
- Mock-only documents can be used only as development fixtures, not accepted evidence.
- Sensitive material must be redacted or referenced through safe metadata.

### 5.2 Real Document Import and Wiki Acceptance

Module:

```text
real_document_e2e.py
```

Inputs:

- real document sample contract;
- workspace/source import commands or API inputs;
- existing Knowledge Console or backend workspace/source capabilities;
- generated wiki/distill artifacts.

Outputs:

```text
real_document_acceptance/import_run.json
real_document_acceptance/wiki_artifact_review.json
real_document_acceptance/real_document_e2e_report.md
```

Acceptance rules:

- Accepted import requires a real document source, execution record, artifact refs, and screenshot or equivalent UI/API evidence.
- Parser failures, empty extraction, unsupported formats, or low-signal output must remain visible.
- A screenshot of a UI shell is not sufficient evidence for real document import.

### 5.3 Retrieval, GraphRAG, and Source Trace Acceptance

Module:

```text
retrieval_trace.py
```

Inputs:

- real-document query scenarios;
- retrieval results;
- GraphRAG results;
- source trace output and evidence spans.

Outputs:

```text
real_document_acceptance/query_trace_review.json
real_document_acceptance/graphrag_review.json
real_document_acceptance/source_trace_review.md
```

Acceptance rules:

- Query acceptance requires source refs or explicit unresolved reason.
- GraphRAG output must not be described as full runtime topology or complete call graph.
- Missing source trace is a blocker for accepted user experience and must be reported as `needs_review` or `structured_blocker`.

### 5.4 Quality Governance and Correction Acceptance

Module:

```text
quality_acceptance.py
```

Inputs:

- low-signal findings;
- quality feedback records;
- correction plan or correction rule review;
- human review state.

Outputs:

```text
real_document_acceptance/quality_governance_review.json
real_document_acceptance/correction_acceptance_report.md
```

Acceptance rules:

- Quality findings must not be hidden by UI/report formatting.
- Correction recommendations require evidence refs or `needs_review`.
- Human review missing means quality correction cannot be fully accepted.

### 5.5 Release Closure Rerun

Module:

```text
release_closure.py
```

Inputs:

- V2.76-V2.80 persisted evidence index;
- V2.81-V2.84 real-document acceptance artifacts;
- external project availability status;
- warning gate and restore/smoke evidence;
- human release approval state.

Outputs:

```text
real_document_acceptance/release_closure_rerun.json
real_document_acceptance/final_manual_acceptance_report.md
```

Acceptance rules:

- Final release accepted requires real-document acceptance, external project status, warning gate, restore/smoke, and human approval.
- Missing external project paths remain `structured_unavailable`.
- Missing human approval remains `needs_review`.
- Release closure must preserve unresolved items instead of smoothing them into an accepted summary.

## 6. Public Surface Plan

MCP tools should follow build/read parity:

```text
knowledge_code_real_document_acceptance_sample_contract_build
knowledge_code_real_document_acceptance_sample_contract_read
knowledge_code_real_document_acceptance_real_e2e_build
knowledge_code_real_document_acceptance_real_e2e_read
knowledge_code_real_document_acceptance_retrieval_trace_build
knowledge_code_real_document_acceptance_retrieval_trace_read
knowledge_code_real_document_acceptance_quality_build
knowledge_code_real_document_acceptance_quality_read
knowledge_code_real_document_acceptance_release_closure_build
knowledge_code_real_document_acceptance_release_closure_read
```

CLI commands should follow:

```text
python -m data_service code real-document-acceptance sample-contract build/read
python -m data_service code real-document-acceptance real-e2e build/read
python -m data_service code real-document-acceptance retrieval-trace build/read
python -m data_service code real-document-acceptance quality build/read
python -m data_service code real-document-acceptance release-closure build/read
```

HTTP routes should follow:

```text
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/sample-contract
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/real-e2e
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/retrieval-trace
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/quality
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/release-closure
```

Build surfaces create or refresh persisted artifacts. Read surfaces only read persisted artifacts and must not manufacture new conclusions.

## 7. Focused Test Plan

Planned focused tests:

```text
backend/tests/test_v2_81_real_document_sample_contract.py
backend/tests/test_v2_82_real_document_import_wiki.py
backend/tests/test_v2_83_retrieval_graphrag_source_trace.py
backend/tests/test_v2_84_quality_governance_real_document.py
backend/tests/test_v2_85_release_closure_rerun.py
```

Shared guard commands:

```text
pytest -q backend/tests/test_public_surface_guard.py
python -m compileall backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 8. Exit Rule

This blueprint supports implementation planning. It does not prove V2.81-V2.85 implementation or real-document acceptance. Accepted status requires implementation, real execution, evidence artifacts, PRD/spec review, false-green audit, and final acceptance audit.
