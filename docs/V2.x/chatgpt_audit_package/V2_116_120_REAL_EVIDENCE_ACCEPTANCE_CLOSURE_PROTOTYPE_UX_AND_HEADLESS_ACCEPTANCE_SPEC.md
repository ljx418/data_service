# V2.116-V2.120 Prototype UX and Headless Acceptance Spec

## 1. 目的

Drawio 表达信息架构和流程，但不足以作为 UI 原型。本文件冻结 `/knowledge` 或 HTML report 的页面结构、组件边界、交互和 headless 验收条件。

## 2. 页面结构

本阶段选择保守路线：`/knowledge` 是 read-only evidence console，HTML report 是 read-only audit output。UI 不直接写入 anchor、approval、revoke 或 approved out-of-scope；所有决策通过独立 `decisions/{decision_set_id}.json` 或后续专用接口阶段处理。

目标页面应包含：

```text
PortfolioRealEvidencePanel
  FinalGateSummary
  EvidenceStatusTabs
    OcrEvidenceTable
    SourceTraceEvidenceTable
    UiCaptureEvidencePanel
    SafeBuildApprovalTable
    DecisionRegistryPanel
  FalseGreenAuditPanel
  ArtifactLinksPanel
```

`KnowledgePage.vue` 只挂载 `PortfolioRealEvidencePanel`，避免继续膨胀。

## 3. Required Fields

FinalGateSummary：

- `run_id`
- `generated_at`
- `implementation_delivery_status`
- `portfolio_final_status`
- `high_risk_unresolved_count`
- `stale_or_mixed_run`
- `next_actions`

OcrEvidenceTable：

- `media_id`
- `source_ref`
- `sha256`
- `ocr_anchor`
- `provider_name`
- `provider_version`
- `anchor_hit`
- `acceptance_status`
- `row_acceptance_status`
- `next_action`

SourceTraceEvidenceTable：

- `document_id`
- `source_id`
- `source_content_hash`
- `query_text_hash`
- `query_result_source_ids`
- `trace_source_id`
- `same_source_assertion`
- `row_acceptance_status`

UiCaptureEvidencePanel：

- `scenario_id`
- `route`
- `viewport`
- `stable_selectors`
- `selector_assertions`
- `console_errors`
- `network_errors`
- `screenshot_ref`
- `row_acceptance_status`

SafeBuildApprovalTable：

- `project_id`
- `command_id`
- `risk_level`
- `approval_status`
- `decision_id`
- `normalized_binding_digest`
- `execution_status`
- `redaction_passed`
- `process_tree_cleanup_passed`
- `sandbox_ref`

DecisionRegistryPanel：

- `decision_set_id`
- `decision_id`
- `decision_type`
- `decision_status`
- `revokes_decision_id`
- `supersedes_decision_id`
- `scope_digest`
- `expires_at`

FalseGreenAuditPanel：

- `check_id`
- `check_name`
- `result`
- `non_waivable`
- `evidence_refs`
- `next_action`

ArtifactLinksPanel：

- `artifact_id`
- `artifact_type`
- `artifact_ref`
- `sha256`
- `run_id`
- `input_manifest_ref`

## 4. Interaction Contract

本阶段 UI 交互仅限只读导航、筛选、复制 refs 和查看决策状态：

- 查看 anchor proposal。
- 复制 anchor decision bundle 模板路径。
- 查看 anchor confirmation 是否有效、过期或撤销。
- 不在 UI 内 Add/Edit/Revoke anchor。

Build approval：

- 查看 proposed command、risk、digest 和 sandbox policy。
- 复制 decision bundle 模板路径或 CLI 提示。
- 查看 approved/rejected/revoked/expired 状态。
- 不在 UI 内 Approve/Reject/Revoke build command。

Approved out-of-scope：

- 查看已有 exception 的 risk level、scope、reason、approver 和 expiry。
- 不在 UI 内创建或撤销 approved out-of-scope。
- Expired/revoked decisions cannot satisfy final accepted。

如未来需要交互式 UI，必须新增专门 PRD 与 public write surface，不能在本阶段由前端直接修改 persisted artifact。

## 5. Large-data Behavior

必须支持：

- 200 media rows。
- 80 source trace gaps。
- 140 high-risk unresolved。
- Filtering by status、phase、project、risk。
- Pagination or virtualized visible rows。
- Empty、loading、error、blocked、stale states。

## 6. Headless Acceptance

截图 accepted 不只看文件存在。必须同时断言：

- stable selector exists: `[data-testid="portfolio-real-evidence-panel"]`
- final gate selector exists: `[data-testid="final-gate-summary"]`
- OCR table selector exists when OCR data exists。
- Source trace selector exists when source trace data exists: `[data-testid="source-trace-evidence-table"]`
- Safe build selector exists when command proposals exist: `[data-testid="safe-build-approval-table"]`
- Decision panel selector exists when decision set exists: `[data-testid="decision-registry-panel"]`
- False-green panel selector exists: `[data-testid="false-green-audit-panel"]`
- No blank page。
- No uncaught console error。
- HTTP/API failure is displayed as structured blocker。
- Screenshot file exists and has sha256。
- DOM status matches artifact `portfolio_final_status`。

空白页、500 页面、错误 workspace 数据、selector 缺失或 console fatal error 均不得 accepted。

## 7. Scenario IDs

Headless E2E 必须至少覆盖：

| scenario_id | 目的 | 不可 accepted 条件 |
| --- | --- | --- |
| `REAC_UI_001_final_gate_summary` | 验证 final gate 总览 | 缺 `portfolio_final_status` |
| `REAC_UI_002_ocr_table` | 验证 OCR evidence 列表 | 缺 anchor/status/source ref |
| `REAC_UI_003_source_trace_table` | 验证同源闭环字段 | `same_source_assertion=mismatch` 却 accepted |
| `REAC_UI_004_safe_build_table` | 验证 command proposal 和 sandbox 状态 | 未批准命令显示为 executable accepted |
| `REAC_UI_005_decision_registry` | 验证决策有效期和撤销 | revoked/expired 决策仍满足 final accepted |
| `REAC_UI_006_stale_or_wrong_workspace` | 验证 stale/wrong workspace 展示 | UI 隐藏 structured blocker |
