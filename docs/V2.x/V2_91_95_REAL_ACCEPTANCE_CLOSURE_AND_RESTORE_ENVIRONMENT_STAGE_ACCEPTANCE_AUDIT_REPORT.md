# V2.91-V2.95 Stage Acceptance Audit Report

Date: 2026-07-03

## Overall Result

Implementation completed for the document-supported V2.91-V2.95 scope. Final release is not accepted.

This report is a stage acceptance audit, not a final release approval. It does not claim complete design-intent recovery, full call graph, runtime topology, data/control flow, or type inference.

## Re-run Acceptance Commands

```text
PYTHONPATH=backend python3 -m pytest -q backend/tests/test_v2_86_full_corpus_e2e_hardening.py backend/tests/test_v2_87_route_a_representative_acceptance.py backend/tests/test_v2_88_quality_governance_human_review.py backend/tests/test_v2_89_external_project_e2e_closure.py backend/tests/test_v2_90_release_gate_restore_hygiene.py backend/tests/test_v2_91_restoreable_acceptance_runtime.py backend/tests/test_v2_92_route_a_material_closure.py backend/tests/test_v2_93_human_quality_decision_closure.py backend/tests/test_v2_94_external_project_path_e2e_closure.py backend/tests/test_v2_95_final_release_gate_closure.py backend/tests/test_public_surface_guard.py
```

Result: 27 passed, 16 warnings.

```text
PYTHONPATH=backend python3 -m compileall -q backend/data_service backend/app/api backend/tests
```

Result: passed.

```text
git diff --check
```

Result: passed.

```text
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

Result: empty diff. Protected legacy files were not modified.

## Real E2E Evidence

Fresh artifacts were generated under:

```text
workspace/v2_91_95_stage_audit_e2e/v29195_stage_audit/assets/codebase/data_service_v29195_stage_audit/real_acceptance_closure/
```

Current real data_service E2E status:

| Phase | Scope | Status | Evidence |
| --- | --- | --- | --- |
| V2.91 | Restoreable Acceptance Runtime | `structured_blocker` | `runtime_restore/runtime_diagnosis.json` |
| V2.92 | Route A Representative Material Closure | `needs_review` | `route_a_closure/manual_acceptance_record.md` |
| V2.93 | Human Quality Decision Closure | `needs_review` | `quality_decision/quality_closure_report.md` |
| V2.94 | External Project E2E Path Closure | `structured_unavailable` | `external_project_closure/e2e_result_matrix.json` |
| V2.95 | Final Release Gate Closure | `structured_blocker` | `release_finalizer/final_gate_summary.json` |

Runtime details:

- `python -m pytest --version`: accepted.
- `python -m venv <temporary_acceptance_runtime>`: `structured_blocker`.
- Focused regression with isolated acceptance environment variables: accepted.
- `backend/.venv`: broken and not used as acceptance proof.

## PRD / Spec Review

- V2.91 implements runtime diagnosis, restore checklist, focused regression result, and false-green guard. It keeps venv failure as `structured_blocker`.
- V2.92 implements Route A material intake and manual acceptance artifact structure. It remains `needs_review` without user representative real material, redaction decision, screenshot/headless evidence, and human acceptance.
- V2.93 implements human quality decision closure artifacts. It remains `needs_review` without real reviewer decisions.
- V2.94 implements external project path binding and E2E matrix. `data_service` is runnable; `codexPat`, `HarnessOS`, and `Navia` remain `structured_unavailable` because no readable paths were provided.
- V2.95 implements final release gate aggregation and false-green audit. Final release remains `structured_blocker` because high-risk inputs are not all accepted.

## Public Surface Review

Implemented and tested surfaces:

- MCP tools: `knowledge_code_real_acceptance_closure_*`.
- HTTP route family: `/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/...`.
- Code parser inventory: `_build_knowledge_parser()` includes `code real-acceptance-closure`.

Observed CLI shell entrypoint caveat:

- `PYTHONPATH=backend python3 -m data_service code real-acceptance-closure --help` currently uses the legacy `_build_parser()` command set and rejects `code`.
- This is recorded as a public CLI execution gap for human review. It must not be described as accepted shell CLI behavior until the default module entrypoint exposes the code parser or the documented CLI invocation is updated.

## False-green Audit

Passed for implementation scope. Final release remains non-accepted because:

- venv creation support is unavailable in the selected runtime.
- Route A real user material, redaction decision, screenshot/headless evidence, and manual acceptance are missing.
- Human quality reviewer decisions are missing.
- `codexPat`, `HarnessOS`, and `Navia` paths are missing.
- Dependency hygiene and human release approval are not accepted.

No `needs_review`, `structured_unavailable`, or `structured_blocker` item is counted as accepted.

## Remaining High-risk Human Inputs

- User representative Route A material package and manual acceptance.
- Human quality reviewer decisions.
- Readable `codexPat`, `HarnessOS`, and `Navia` paths or explicit unavailable decisions.
- Working isolated Python venv creation support, for example `python3.12-venv` / ensurepip availability.
- Dependency hygiene confirmation.
- Human release approval.
