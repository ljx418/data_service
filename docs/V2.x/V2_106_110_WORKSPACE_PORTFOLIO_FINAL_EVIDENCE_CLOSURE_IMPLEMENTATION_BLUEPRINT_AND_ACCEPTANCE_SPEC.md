# V2.106-V2.110 Implementation Blueprint and Acceptance Spec

## 1. Implementation Boundary

本文件只定义后续实现蓝图，不表示功能已实现。

默认新增独立包，避免扩大 legacy 大文件：

```text
backend/data_service/workspace_portfolio_final_evidence/
  __init__.py
  shared.py
  persistence.py
  coverage_closure.py
  media_evidence.py
  build_scheduler.py
  source_trace_closure.py
  ui_evidence.py
  release_gate.py
  report.py
```

Adapter 计划：

```text
backend/data_service/cli_portfolio_final_evidence.py
backend/data_service/mcp_workspace_portfolio_final_evidence_tools.py
backend/app/api/v1/workspace_portfolio_final_evidence.py
frontend/src/pages/KnowledgePage.vue
```

默认不修改：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 2. Unified Response Contract

The field-level contract is frozen in:

```text
V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_ARTIFACT_SCHEMA_AND_ID_CONTRACTS.md
```

The following envelope is the minimum shared wrapper. Each artifact must also satisfy its artifact-specific `data` schema.

```json
{
  "ok": true,
  "schema_version": "v2.106-110",
  "workspace_id": "string",
  "phase": "V2.106|V2.107|V2.108|V2.109|V2.110",
  "status": "accepted|needs_review|structured_unavailable|structured_blocker|out_of_scope",
  "artifact_refs": ["repo-relative path"],
  "evidence_refs": ["repo-relative path or artifact id"],
  "warnings": ["string"],
  "unresolved": [
    {
      "kind": "needs_review|structured_unavailable|structured_blocker",
      "reason": "string",
      "next_action": "string"
    }
  ],
  "next_actions": ["string"],
  "data": {}
}
```

## 3. Phase Artifacts

| Phase | Artifacts | Acceptance Signal |
| --- | --- | --- |
| V2.106 | `coverage_state_closure.json`, `architecture_state_closure.json` | 已实现项状态正确，non-accepted 缺口保留 |
| V2.107 | `ocr_provider_health.json`, `media_evidence_matrix.json` | OCR 缺失时 media rows 不 accepted |
| V2.108 | `full_build_queue.json`, `project_build_diagnosis.json` | 多项目 build 有 queue、timeout、failure category、next action |
| V2.109 | `document_source_trace_closure.json` | accepted 文档行具备 ingest/query/source trace refs |
| V2.110 | `final_release_gate.json`, `false_green_recheck.md`, `final_evidence_report.html` | final status 与最差高风险状态一致 |

## 4. Status Rules

Status rules are governed by:

```text
V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_STATUS_ALGEBRA_AND_FINAL_GATE_DECISION_TABLE.md
```

Implementation must separate `execution_status` from `acceptance_status`.

Accepted values for `acceptance_status`:

```text
accepted
needs_review
structured_unavailable
structured_blocker
out_of_scope
```

Accepted values for `execution_status`:

```text
pending
queued
running
succeeded
failed
timeout
skipped
unavailable
cancelled
```

## 5. False-green Rejection Rules

- scan accepted 不等于项目理解 accepted。
- readiness accepted 不等于 ingest/query/source trace accepted。
- UI available 不等于 build evidence accepted。
- OCR unavailable 不等于 media evidence accepted。
- timeout/skipped 不等于 project accepted。
- final report available 不等于 final release accepted。

## 6. P0 Contract Dependencies

Implementation must follow these contracts:

- Artifact schema and stable IDs.
- Status algebra and final gate decision table.
- Build execution security and runtime spec.
- Run lineage, persistence and staleness spec.
- Public surface interface contract.
- Requirement-test-evidence traceability matrix.
- Baseline evidence package.
- Prototype UX spec for `/knowledge` presentation.
