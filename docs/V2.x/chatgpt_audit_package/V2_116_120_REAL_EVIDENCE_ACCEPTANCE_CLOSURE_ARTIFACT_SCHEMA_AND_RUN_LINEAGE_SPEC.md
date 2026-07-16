# V2.116-V2.120 Artifact Schema and Run Lineage Spec

## 1. 目的

本文件补齐 V2.116-V2.120 的不可变运行谱系、artifact 完整 schema、staleness 和 mixed-run 拒绝规则。它优先级高于单个阶段文档中的简化 schema 示例。

机器可校验 schema 以以下文件为准：

```text
V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_SCHEMA_BUNDLE.json
```

本文档内 JSON 片段是说明性摘要；如与 schema bundle 冲突，以 schema bundle 为准。

## 2. Artifact Directory Contract

所有 build 输出必须写入不可变 run 目录：

```text
workspace/{workspace_id}/portfolio_real_evidence_acceptance/
  latest.json
  decisions/{decision_set_id}.json
  runs/{run_id}/
    input_manifest.json
    ocr_anchor_registry.json
    ocr_provider_execution.json
    ocr_closure_report.md
    source_trace_batch_results.json
    source_trace_evidence_index.json
    source_trace_closure_report.md
    ui_capture_results.json
    ui_screenshot_manifest.json
    safe_build_allowlist.json
    safe_build_execution_results.json
    safe_build_governance_report.md
    evidence_decision_snapshot.json
    final_portfolio_acceptance_gate.json
    final_portfolio_false_green_audit.md
    final_portfolio_acceptance_report.html
```

`latest.json` 只能指向一个完整写入并通过完整性检查的 `run_id`。`latest.json` 是指针文件，不使用 Shared Artifact Envelope；`decisions/{decision_set_id}.json` 是 append-only authority，不属于不可变 run artifact；`input_manifest.json` 和其他 run 内 JSON artifact 必须使用 Shared Artifact Envelope，业务字段统一放入 `data`。

## 3. Shared Artifact Envelope

每个 JSON artifact 必须包含：

```json
{
  "schema_version": "v2.116-120",
  "workspace_id": "string",
  "run_id": "string",
  "run_type": "proposal|execution|final_gate",
  "lineage_root_id": "string",
  "parent_run_ids": ["string"],
  "source_run_refs": [
    {
      "run_id": "string",
      "artifact_id": "string",
      "artifact_hash": "sha256",
      "input_manifest_hash": "sha256",
      "role": "proposal|execution_evidence|decision_snapshot|upstream_baseline"
    }
  ],
  "artifact_id": "string",
  "artifact_type": "string",
  "phase": "V2.116|V2.117|V2.118|V2.119|V2.120",
  "generated_at": "ISO-8601 string",
  "producer": {
    "name": "string",
    "version": "string"
  },
  "input_manifest_ref": "runs/{run_id}/input_manifest.json",
  "input_hashes": {
    "root_fingerprint": "string",
    "upstream_artifacts": {}
  },
  "artifact_refs": ["workspace-relative path"],
  "evidence_refs": ["workspace-relative path or evidence id"],
  "artifact_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "warnings": ["string"],
  "unresolved": [
    {
      "kind": "needs_review|structured_unavailable|structured_blocker|failed",
      "item_id": "string",
      "reason": "string",
      "next_action": "string",
      "evidence_refs": ["string"]
    }
  ],
  "data": {}
}
```

Schema bundle 约束：

- 所有 envelope 顶层字段均为 required，除非本文件明确列为 nullable。
- 业务字段必须位于 `data`，不得在顶层混放业务字段。
- 机器 schema 应使用 `additionalProperties=false`，兼容字段必须通过显式 `x_compat` 或 schema migration 记录。
- Public response envelope 中的 `status` 只用于 API/CLI/MCP 返回；persisted artifact 使用 `artifact_status`。

## 4. Input Manifest

`input_manifest.json` 固定本次 run 的事实输入，并同样使用 Shared Artifact Envelope：

```json
{
  "schema_version": "v2.116-120",
  "workspace_id": "string",
  "run_id": "string",
  "artifact_id": "input_manifest",
  "artifact_type": "input_manifest",
  "phase": "V2.116",
  "generated_at": "ISO-8601 string",
  "producer": {"name": "portfolio_real_evidence_acceptance", "version": "string"},
  "input_manifest_ref": "runs/{run_id}/input_manifest.json",
  "input_hashes": {"root_fingerprint": "sha256", "upstream_artifacts": {}},
  "artifact_refs": ["runs/{run_id}/input_manifest.json"],
  "evidence_refs": [],
  "artifact_status": "accepted|structured_blocker",
  "warnings": [],
  "unresolved": [],
  "data": {
    "root_ref": "workspace-relative or redacted path",
    "root_fingerprint": "sha256",
    "upstream_runs": [
      {
        "phase": "V2.111-V2.115",
        "artifact_root": "workspace-relative path",
        "run_id": "string|null",
        "artifact_hashes": {
          "final_acceptance_gate.json": "sha256",
          "ocr_sample_qualification.json": "sha256",
          "media_execution_results.json": "sha256",
          "source_trace_execution.json": "sha256",
          "ui_evidence_capture.json": "sha256",
          "safe_build_execution.json": "sha256"
        }
      }
    ],
    "document_hashes": {
      "prd": "sha256",
      "target_architecture": "sha256",
      "schema_contract": "sha256",
      "test_mapping": "sha256",
      "drawio": "sha256"
    }
  }
}
```

## 5. Lineage-bound Run and Stale Rejection

本阶段采用 lineage-bound，而不是 same-run-only。

合法流程允许：

```text
Proposal Run
  -> Decision Set
  -> Execution Run
  -> Final Gate Run
```

Final Gate Run 可以读取 Proposal/Execution/Decision Snapshot 的 artifact，但必须在 `source_run_refs[]` 中显式声明并绑定 hash。

Final gate 必须拒绝以下情况：

- 跨 run artifact 未在 `source_run_refs[]` 中声明。
- `lineage_root_id` 不一致。
- `input_manifest_hash` 不一致。
- `source_run_refs[].artifact_hash` 与实际 artifact hash 不一致。
- 任一 artifact 的 `input_manifest_ref` 不存在。
- 上游 V2.111-V2.115 artifact hash 与 `input_manifest.json` 不一致。
- `latest.json` 指向的 run 不完整。
- 文档 hash 或 root fingerprint 已变化，但没有新 run。

拒绝结果：

```text
portfolio_final_status=structured_blocker
failure_category=mixed_run_or_stale_input
```

## 6. Atomic Write

实现阶段必须遵守：

1. 写入 `runs/{run_id}.tmp/`。
2. 每个 JSON 先写临时文件，再原子 rename。
3. 全部 artifact 和 completeness check 通过后，rename 为 `runs/{run_id}/`。
4. 最后原子更新 `latest.json`。
5. 崩溃遗留 `.tmp` 目录不得被 read/report 当作有效 run。

## 7. Required JSON Artifacts

完整 schema bundle 必须覆盖以下 JSON，并作为实现前冻结项：

| Schema | Persisted artifact | 核心 `data` 字段 |
| --- | --- | --- |
| `latest.schema.json` | `latest.json` | `current_run_id`、`current_run_ref`、`current_run_hash`、`updated_at`、`completeness_check_ref` |
| `input_manifest.schema.json` | `runs/{run_id}/input_manifest.json` | `root_ref`、`root_fingerprint`、`upstream_runs[]`、`document_hashes` |
| `ocr_anchor_registry.schema.json` | `ocr_anchor_registry.json` | `rows[].media_id`、`source_ref`、`sha256`、`ocr_anchor`、`anchor_text_hash`、`row_acceptance_status` |
| `ocr_provider_execution.schema.json` | `ocr_provider_execution.json` | `provider_health[]`、`rows[].provider_steps[]`、`page_outputs[]`、`anchor_hit`、`row_acceptance_status` |
| `source_trace_batch_results.schema.json` | `source_trace_batch_results.json` | `rows[].document_id`、`import_ref`、`query_ref`、`source_trace_refs`、`row_acceptance_status` |
| `source_trace_evidence_index.schema.json` | `source_trace_evidence_index.json` | `document_id`、`source_id`、`source_content_hash`、`query_text_hash`、`query_result_source_ids`、`trace_source_id`、`same_source_assertion` |
| `ui_capture_results.schema.json` | `ui_capture_results.json` | `scenario_id`、`route`、`selector_assertions[]`、`console_errors[]`、`network_errors[]`、`row_acceptance_status` |
| `ui_screenshot_manifest.schema.json` | `ui_screenshot_manifest.json` | `screenshots[].scenario_id`、`path`、`sha256`、`viewport`、`dom_assertion_ref` |
| `safe_build_allowlist.schema.json` | `safe_build_allowlist.json` | `commands[].command_id`、`proposal_run_id`、`decision_set_id`、`normalized_binding_digest`、`sandbox_policy_digest`、`approval_status` |
| `safe_build_execution_results.schema.json` | `safe_build_execution_results.json` | `commands[].execution_run_id`、`sandbox_ref`、`execution_status`、`redaction_passed`、`process_tree_cleanup_passed` |
| `decision_set.schema.json` | `decisions/{decision_set_id}.json` | `decision_set_id`、`decisions[].decision_id`、`revokes_decision_id`、`supersedes_decision_id`、`scope_digest` |
| `evidence_decision_snapshot.schema.json` | `evidence_decision_snapshot.json` | `decision_set_ref`、`decision_set_hash`、`effective_decision_ids`、`scope_validation`、`approval_binding_validation` |
| `final_portfolio_acceptance_gate.schema.json` | `final_portfolio_acceptance_gate.json` | `implementation_delivery_status`、`portfolio_final_status`、`non_waivable_failures[]`、`gate_reasons[]`、`mixed_run_check` |

## 8. Critical Artifact Field Contracts

`latest.json` 指针文件：

```json
{
  "schema_version": "v2.116-120",
  "workspace_id": "string",
  "current_run_id": "string",
  "current_run_ref": "runs/{run_id}",
  "current_run_hash": "sha256",
  "updated_at": "ISO-8601 string",
  "completeness_check_ref": "runs/{run_id}/final_portfolio_acceptance_gate.json"
}
```

`source_trace_evidence_index.json` 的 `data.rows[]` 必须包含：

```json
{
  "document_id": "string",
  "source_id": "string",
  "source_content_hash": "sha256",
  "import_artifact_id": "string",
  "query_id": "string",
  "query_text_hash": "sha256",
  "query_result_ref": "workspace-relative path",
  "query_result_source_ids": ["string"],
  "trace_id": "string",
  "trace_source_id": "string",
  "trace_evidence_refs": ["string"],
  "same_source_assertion": "matched|mismatch|not_available",
  "row_acceptance_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed"
}
```

`ocr_provider_execution.json` 的 `data.rows[].provider_steps[]` 必须记录多步骤链：

```json
{
  "step_id": "string",
  "step_kind": "office_convert|pdf_rasterize|image_ocr|text_extract|anchor_match",
  "provider_name": "tesseract|pdftoppm|soffice|pypdf|internal",
  "provider_version": "string|null",
  "input_ref": "workspace-relative path",
  "input_hash": "sha256",
  "output_ref": "workspace-relative path|null",
  "output_hash": "sha256|null",
  "page_or_slide": "integer|null",
  "language": "chi_sim|eng|mixed|null",
  "execution_status": "succeeded|failed|unavailable|skipped"
}
```

`ui_capture_results.json` 的 `data.scenarios[]` 必须包含：

```json
{
  "scenario_id": "string",
  "route": "/knowledge",
  "viewport": "desktop|mobile",
  "stable_selectors": ["[data-testid='portfolio-real-evidence-panel']"],
  "selector_assertions": [{"selector": "string", "result": "present|missing"}],
  "console_errors": ["string"],
  "network_errors": ["string"],
  "screenshot_ref": "workspace-relative path|null",
  "row_acceptance_status": "accepted|structured_blocker|failed"
}
```

`safe_build_allowlist.json` 的 `data.commands[]` 必须绑定 proposal、decision 和 sandbox 摘要：

```json
{
  "command_id": "string",
  "project_id": "string",
  "proposal_run_id": "string",
  "decision_set_id": "string|null",
  "argv": ["string"],
  "cwd_policy": "managed_sandbox_working_copy",
  "normalized_binding_digest": "sha256",
  "sandbox_policy_digest": "sha256",
  "project_input_hash": "sha256",
  "approval_status": "needs_review|approved|rejected|revoked|expired"
}
```

`final_portfolio_acceptance_gate.json` 的 `data` 必须包含：

```json
{
  "implementation_delivery_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "portfolio_final_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "artifact_status_priority_applied": ["failed", "structured_blocker", "structured_unavailable", "needs_review", "accepted"],
  "non_waivable_failures": ["mixed_run|stale_or_tampered_input|forged_or_invalid_approval|path_escape|secret_redaction_failure|child_process_cleanup_failure|artifact_hash_mismatch"],
  "high_risk_unresolved_count": 0,
  "gate_reasons": ["string"],
  "false_green_rejected": ["string"],
  "input_manifest_hash": "sha256",
  "decision_set_ids": ["string"]
}
```
