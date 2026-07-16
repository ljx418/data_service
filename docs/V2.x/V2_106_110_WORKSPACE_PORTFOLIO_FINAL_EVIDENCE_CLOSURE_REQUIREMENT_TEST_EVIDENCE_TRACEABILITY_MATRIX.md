# V2.106-V2.110 Requirement-Test-Evidence Traceability Matrix

## 1. Purpose

This matrix closes the P0 acceptance gap by mapping each requirement to tests, real inputs, assertions and evidence artifacts.

## 2. Matrix

| Requirement ID | Requirement | Phase | Focused test | Real input | Required assertions | Evidence artifacts |
| --- | --- | --- | --- | --- | --- | --- |
| REQ-V2106-COVERAGE-STATE | V2.101-V2.105 status rows are correctly closed | V2.106 | `test_v2_106_portfolio_coverage_state_closure.py` | V2.101-V2.105 coverage/audit/report/drawio | accepted rows have evidence; non-accepted rows remain non-accepted | `coverage_state_closure.json`, report |
| REQ-V2106-ARCH-STATE | Architecture/drawio state reflects implemented/planned/needs-change entities | V2.106 | same | target architecture and drawio | no implemented entity remains planned without reason; conflicts recorded | `architecture_state_closure.json` |
| REQ-V2107-OCR-HEALTH | OCR/provider availability is tested or structurally unavailable | V2.107 | `test_v2_107_ocr_media_evidence_closure.py` | real media dirs | missing provider maps to `structured_unavailable`; no fake OCR evidence | `ocr_provider_health.json` |
| REQ-V2107-MEDIA-MATRIX | Media rows are classified with evidence and failure category | V2.107 | same | images, scans, PDF, PPT/PPTX | OCR-required rows not accepted without provider evidence | `media_evidence_matrix.json` |
| REQ-V2108-BUILD-QUEUE | Full workspace queue includes all discovered buildable projects | V2.108 | `test_v2_108_full_workspace_build_governance.py` | `/mnt/c/workspace` | queue covers all projects; limit-deferred rows have `deferred_by_limit` | `full_build_queue.json` |
| REQ-V2108-RUNTIME-SAFETY | Build execution follows safety runtime spec | V2.108 | same | data_service + external project candidates | unsafe commands rejected; outputs redacted; timeout/skipped not accepted | `project_build_diagnosis.json` |
| REQ-V2109-SOURCE-TRACE | Accepted documents have import/query/source trace evidence | V2.109 | `test_v2_109_document_source_trace_closure.py` | docs/media source candidates | accepted rows contain source import, query and source trace refs | `document_source_trace_closure.json` |
| REQ-V2110-UI-EVIDENCE | UI evidence is screenshot-backed or structurally unavailable | V2.110 | `test_v2_110_portfolio_final_release_gate.py` | `/knowledge?view=portfolio` | missing browser maps to `structured_unavailable`; no fake screenshots | `ui_evidence_capture.json` |
| REQ-V2110-FINAL-GATE | Final gate follows worst high-risk acceptance status | V2.110 | same | all closure artifacts | blocker/unavailable/needs_review prevents final accepted | `final_release_gate.json` |
| REQ-V2110-FALSE-GREEN | False-green recheck rejects scan-only/readiness-only/UI-only/OCR-missing evidence | V2.110 | same + public guard | all closure artifacts | report lists rejected patterns and no hidden blockers | `false_green_recheck.md`, HTML report |

## 3. Negative Scenarios

Required negative tests:

- accepted row with no evidence refs must fail.
- OCR-required row with missing provider must not be accepted.
- build queue with missing deferred projects must fail.
- timeout/skipped project must not be accepted.
- document row with no source trace must not be accepted.
- final gate with mixed run inputs must be structured blocker.
- protected legacy file diff must fail automated gate.

## 4. Automated Gate Commands

Protected file checks must use failing commands:

```text
git diff --exit-code -- backend/app/api/v1/data_service.py backend/data_service/service.py
git diff --cached --exit-code -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

`git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py` is informative only and must not be treated as a gate.

