# V2.59-V2.62 Test and Real E2E Mapping

Date: 2026-06-23

## 1. Focused Test Mapping

| Phase | Test file | Required checks |
| --- | --- | --- |
| V2.59 | `backend/tests/test_v2_59_public_surface_stabilization.py` | registry-discovered snapshot, MCP/CLI/HTTP parity, drift classification, migration notes, redaction |
| V2.60 | `backend/tests/test_v2_60_real_project_e2e_expansion.py` | unavailable not accepted, mock-only rejected, failure categories valid, artifact refs or unresolved reason |
| V2.61 | `backend/tests/test_v2_61_acceptance_packaging.py` | manifest classification, cleanup advisory, no destructive default, redaction, handoff runner |
| V2.62 | `backend/tests/test_v2_62_portal_ux_integration.py` | persisted artifact inputs only, status separation, no raw Mermaid source, HTML smoke |

Public surface guard must cover all new MCP tools, CLI commands, and HTTP routes.

## 2. Real E2E Mapping

| Phase | Script | Required real result |
| --- | --- | --- |
| V2.59 | `backend/scripts/v2_59_real_e2e.py` | data_service builds and reads surface snapshot, parity matrix, drift report, migration notes |
| V2.60 | `backend/scripts/v2_60_real_e2e.py` | data_service accepted; codexPat/HarnessOS/Navia accepted or structured rationale |
| V2.61 | `backend/scripts/v2_61_real_e2e.py` | data_service package manifest and cleanup plan generated without destructive action |
| V2.62 | `backend/scripts/v2_62_real_e2e.py` | data_service portal_v3 generated and status panel preserves accepted/unavailable/review states |

## 3. Baseline Regression

Each phase acceptance must run:

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
```

Stage closure must additionally run the V2.59-V2.62 focused set with `backend/tests/test_public_surface_guard.py`.

## 4. False-green Scenarios

| Scenario | Expected handling |
| --- | --- |
| Snapshot generated from static expected names only | reject |
| External project path missing | structured_unavailable or structured_blocker, not accepted |
| Mock-only E2E used as real project evidence | reject |
| Cleanup requires deleting files | manual approval required |
| Portal renders unavailable as accepted | reject |
| Public payload contains absolute path or traceback | reject |

## 5. PRD/Spec Review Checklist

Each phase PRD/spec review must confirm:

- user-facing target experience is met by artifacts;
- architecture boundaries are preserved;
- no protected legacy file modification occurred;
- no full design intent, full call graph, runtime topology, data/control flow, or type inference claim was introduced;
- coverage matrix status is evidence-backed.
