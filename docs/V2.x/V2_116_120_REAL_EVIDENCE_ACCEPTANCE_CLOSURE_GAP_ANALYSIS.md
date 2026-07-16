# V2.116-V2.120 Gap Analysis

## 1. 当前缺口

| 缺口 | 风险 | 处理方式 |
| --- | --- | --- |
| 缺真实 OCR 文本锚点 | OCR 被误 accepted | V2.116 建立 anchor registry；无 anchor 保持 needs_review |
| OCR provider 依赖未冻结 | 实现时临时选择依赖导致不可复跑 | 首发默认 Tesseract + Poppler + LibreOffice；缺依赖结构化阻断，不自动安装 |
| Source trace 链不完整 | 文件存在被误当 source evidence | V2.117 要求 import/query/source trace 三段 refs |
| UI screenshot 未完成 | HTML report 被误当视觉验收 | V2.118 生成 headless screenshot 或 blocker |
| Build 命令未审批 | 执行不可信外部命令 | V2.119 引入 allowlist 和 approval state |
| Final gate 仍 non-accepted | 错误声明 release accepted | V2.120 聚合 high-risk 状态并执行 false-green audit |

## 2. 架构风险

- 模块边界退化：新逻辑必须进入独立包，不回写 legacy 大文件。
- 证据混跑：每个 artifact 必须包含 `run_id`、`schema_version`、`generated_at` 和 refs。
- 状态混淆：execution failure 和 acceptance failure 不得混写为 accepted。
- UI 过度承诺：截图只能证明页面展示，不证明 OCR/source/build evidence accepted。
- 有界 E2E 误用：`--max-code-projects` 只验证 runtime governance，不证明全量 workspace accepted。

## 3. 降险策略

- Coverage matrix 每行必须绑定 artifact、test、E2E、PRD review 和 false-green audit。
- Drawio 中用颜色标识已实现、待新增、需修改、阻断，避免架构状态不清。
- Final gate 使用最差高风险状态，不隐藏 blocker。
- Public surface read/report 只读取 artifacts，不重新制造事实。

## 4. 外部复审后的 P0 契约闭合状态

| ID | 当前结论 | 必须关闭的内容 |
| --- | --- | --- |
| P0-01 Artifact schema completeness | closed_for_scaffolding | 已新增 `SCHEMA_BUNDLE.json`；实现阶段必须先跑 schema validation tests |
| P0-02 Status algebra conflict | closed_for_scaffolding | 已增加 `run_acceptance_status`、确定状态优先级和安全机制失效/正确阻断区分 |
| P0-03 Run/decision lifecycle | closed_for_scaffolding | 已改为 lineage-bound cross-run validation，并拆分 Decision Set 与 immutable decision snapshot |
| P0-04 Safe build isolation | partial_pass_true_execution_blocked | managed sandbox 合同已定义；真实外部 build 仍禁止，直到 sandbox 实现和测试通过 |
| P0-05 UI write path ambiguity | closed | 本阶段明确 read-only UI；不提供 anchor/decision 写接口 |
| P0-06 Source trace same-source proof | closed_for_scaffolding | 已定义 source_id、source_content_hash、query_result_source_ids、trace_source_id 和 same_source_assertion |
| P0-07 OCR provider chain | closed_for_scaffolding | 已定义 `provider_steps[]`、page_outputs、语言包和 anchor_hit；真实 provider 结果仍待实现验收 |
| P0-08 Normative package authority | closed_for_scaffolding | 已新增 `CONTRACT_BUNDLE_MANIFEST.json`，固定权威文档、hash、classification 和优先级 |

## 5. 开发失败风险与备选路线

| 风险点 | 默认路线 | 备选路线 | 优点 | 代价 |
| --- | --- | --- | --- | --- |
| 缺真实 OCR anchor | 维护者提供或确认 anchor 后执行 OCR provider | 将该 OCR row 标为 `needs_review` 或 approved out_of_scope | 不制造虚假 OCR accepted | Final accepted 可能继续受阻 |
| 本地 OCR 依赖缺失 | 记录 provider health 和 `structured_unavailable` | 用户安装 Tesseract/Poppler/LibreOffice 后复跑 | 保持本地隐私和可复跑 | 当前机器无法 OCR accepted |
| OCR/转换 provider 不可用 | 记录 provider health 和 structured_unavailable | 仅保留样本资格，不执行 provider | 环境问题可复核 | 不能把 media row accepted |
| Headless 浏览器不可用 | 输出 structured browser blocker | 人工批准后再使用可见浏览器截图 | 避免焦点抢占 | 需要人类介入或保持 non-accepted |
| 外部 build 命令高风险 | 只生成 allowlist proposal，不执行 | 人工批准有限命令后执行 | 安全边界清晰 | 覆盖率取决于批准范围 |
| Source trace 缺底层能力或资料 | 保留 structured_unavailable 并给 next action | 缩小 in-scope 范围并记录 approved out_of_scope | 不把文件存在误写 accepted | Final gate 可能不能全绿 |
| Final gate 高风险未闭合 | `portfolio_final_status` 保持 non-accepted | 只在高风险项 approved out_of_scope 后放行 | 避免 false-green | 需要明确风险 owner |

当前不需要用户选择路线，因为每个风险均已有默认安全路线和结构化失败路线；后续实现若需要执行可见浏览器、安装依赖或运行未批准外部命令，必须再找用户确认。

## 6. 当前文档目标

文档完成后应达到：

```text
documentation_status=pass_for_implementation_guidance
low_risk_scaffolding_readiness=pass
guided_phase_implementation_readiness=pass
autonomous_continuous_implementation_readiness=not_pass
implementation_acceptance=not_pass
portfolio_final_acceptance=not_pass
```

## 7. 风险闭环结论

```text
fatal_document_gap=none
major_document_gap=closed_for_implementation_guidance
known_execution_risk=real_evidence_human_decision_and_safe_build_sandbox_dependent
safe_build_true_execution_readiness=not_pass_until_sandbox_verified
phase_specific_acceptance_logic_readiness=partial_pass_requires_schema_validation_and_focused_tests
next_allowed_action=controlled_phase_implementation_after_human_approval_and_stage_gate
```
