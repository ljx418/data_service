# V2.116-V2.120 Phase Readiness and Schema Contracts

## 1. Contract Priority

本文件保留 public envelope 和关键 artifact 摘要 schema。完整机器可执行 schema、不可变 run 目录、`input_manifest.json`、atomic write、stale/mixed-run 规则以以下文件为准：

```text
V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_SCHEMA_BUNDLE.json
V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_ARTIFACT_SCHEMA_AND_RUN_LINEAGE_SPEC.md
V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_STATUS_ALGEBRA_AND_DECISION_APPROVAL_SPEC.md
V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_SAFE_BUILD_SECURITY_AND_RUNTIME_SPEC.md
```

本文件中的 JSON 片段为 non-normative summary，不得作为 persisted artifact 的唯一形状。

## 2. 统一 Response Envelope

```json
{
  "ok": true,
  "schema_version": "v2.116-120",
  "workspace_id": "string",
  "phase": "V2.116|V2.117|V2.118|V2.119|V2.120",
  "run_id": "string",
  "generated_at": "ISO-8601 string",
  "status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "artifact_refs": ["workspace-relative path"],
  "evidence_refs": ["workspace-relative path or artifact id"],
  "warnings": ["string"],
  "unresolved": [
    {
      "kind": "needs_review|structured_unavailable|structured_blocker|failed",
      "reason": "string",
      "next_action": "string",
      "evidence_ref": "string"
    }
  ],
  "next_actions": ["string"],
  "data": {}
}
```

## 3. 状态语义

| 状态 | 语义 | 是否 accepted |
| --- | --- | --- |
| `accepted` | 真实资料、真实命令、artifact refs、证据引用、PRD/spec review 和 false-green audit 全部具备 | 是 |
| `needs_review` | 缺人工判断、真实 anchor、审批或高风险确认 | 否 |
| `structured_unavailable` | 路径、资料、provider、browser 或外部项目不可用 | 否 |
| `structured_blocker` | 依赖、环境、安全策略或实现阻断 | 否 |
| `failed` | 执行失败且不能归类为 unavailable/blocker | 否 |

`approved_out_of_scope` 不是 accepted，但可在 final gate 中作为显式出门例外，必须具备 approver、reason、risk、scope 和 evidence refs。安全或完整性类 non-waivable failure 不得被 approved out-of-scope 豁免。

## 4. 核心 Artifact 字段

`ocr_anchor_registry.json`：

```json
{
  "schema_version": "v2.116-120",
  "run_id": "string",
  "rows": [
    {
      "media_id": "string",
      "path": "workspace-relative path",
      "sha256": "string",
      "source_ref": "string",
      "ocr_anchor": "string|null",
      "sample_qualification": "accepted|needs_review|structured_unavailable",
      "reason": "string"
    }
  ]
}
```

`ocr_provider_execution.json`：

```json
{
  "schema_version": "v2.116-120",
  "run_id": "string",
  "provider_health": [
    {
      "provider_name": "tesseract|pdftoppm|soffice",
      "capability": "image_ocr|pdf_rasterize|office_conversion",
      "available": true,
      "version": "string",
      "row_acceptance_status": "accepted|structured_unavailable"
    }
  ],
  "rows": [
    {
      "media_id": "string",
      "execution_kind": "image_ocr|pdf_rasterize_then_ocr|office_convert_then_ocr|direct_text_extraction",
      "provider_steps": [
        {
          "step_kind": "office_convert|pdf_rasterize|image_ocr|text_extract|anchor_match",
          "provider_name": "string",
          "provider_version": "string|null",
          "input_hash": "sha256",
          "output_hash": "sha256|null",
          "page_or_slide": "integer|null"
        }
      ],
      "command_ref": ["string"],
      "input_ref": "workspace-relative path",
      "input_hash": "string",
      "output_ref": "workspace-relative path|null",
      "output_hash": "string|null",
      "anchor_text": "string|null",
      "anchor_hit": true,
      "execution_status": "succeeded|skipped|failed|unavailable",
      "row_acceptance_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
      "failure_category": "provider_missing|anchor_missing|anchor_not_found|execution_failed|unsupported_format|needs_review|null"
    }
  ]
}
```

`source_trace_batch_results.json`：

```json
{
  "schema_version": "v2.116-120",
  "run_id": "string",
  "rows": [
    {
      "document_id": "string",
      "source_id": "string|null",
      "source_content_hash": "sha256|null",
      "import_ref": "string|null",
      "query_ref": "string|null",
      "query_result_source_ids": ["string"],
      "trace_source_id": "string|null",
      "source_trace_refs": ["string"],
      "same_source_assertion": "matched|mismatch|not_available",
      "row_acceptance_status": "accepted|structured_unavailable|structured_blocker|needs_review|failed"
    }
  ]
}
```

`ui_screenshot_manifest.json`：

```json
{
  "schema_version": "v2.116-120",
  "run_id": "string",
  "capture_mode": "headless|structured_blocker",
  "screenshots": [
    {
      "scenario_id": "string",
      "path": "workspace-relative path",
      "sha256": "string",
      "viewport": "string",
      "row_acceptance_status": "accepted|structured_blocker"
    }
  ]
}
```

`safe_build_allowlist.json`：

```json
{
  "schema_version": "v2.116-120",
  "run_id": "string",
  "commands": [
    {
      "project_id": "string",
      "command_id": "string",
      "argv": ["string"],
      "normalized_binding_digest": "sha256",
      "sandbox_policy_digest": "sha256",
      "project_input_hash": "sha256",
      "approval_status": "approved|needs_review|rejected",
      "reason": "string"
    }
  ]
}
```

`final_portfolio_acceptance_gate.json`：

```json
{
  "schema_version": "v2.116-120",
  "run_id": "string",
  "implementation_delivery_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "portfolio_final_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "non_waivable_failures": ["string"],
  "high_risk_unresolved_count": 0,
  "gate_reasons": ["string"],
  "artifact_refs": ["workspace-relative path"],
  "false_green_rejected": ["string"]
}
```

## 5. Readiness Gate

进入实现前必须满足：

- 文档、drawio、schema、coverage matrix 和 test mapping 已落盘。
- Fatal findings 为 none。
- Major findings 已关闭到 phase-specific scaffolding 级别；仍不允许 continuous automatic implementation、真实外部 build 或 portfolio final accepted。
- V2.111-V2.115 artifacts 路径存在或被结构化标记为 unavailable。
- protected legacy files 不需要修改。
- P0 契约文档已审计：run lineage、状态/审批、安全 build、public surface、prototype/headless、详细测试 fixtures。
- Schema validation tests、focused tests 和真实 E2E 通过前，不得声明 implementation acceptance。
- Managed safe-build sandbox 实现和测试通过前，不得执行真实外部项目 build。
