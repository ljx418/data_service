# V2.117 / Phase 193 Source Trace Batch Closure Plan and Audit

Status: `implemented`

## Development Plan

- Bounded scan real workspace document files.
- Generate import/query/source trace batch rows.
- Generate `source_trace_evidence_index.json` with source identity, source hash, query result source ids, trace source id, and same-source assertion.

## Acceptance Plan

- File existence alone cannot be accepted.
- Accepted source trace row requires `source_id` in query results, `trace_source_id == source_id`, non-empty trace refs, and `same_source_assertion=matched`.

## Audit Opinion

```text
fatal_findings=none
major_findings=none
false_green_risk=controlled
implementation_result=accepted_for_mechanism
```

Focused test:

```text
backend/tests/test_v2_117_source_trace_batch_closure.py
```
