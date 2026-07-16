# V2.116-V2.120 PRD：Real Evidence Acceptance Closure

## 1. 阶段定位

V2.111-V2.115 已完成最终验收闭环实现，真实 E2E 结果保持：

```text
implementation_status=accepted
portfolio_final_status=structured_unavailable
high_risk_unresolved_count=140
```

V2.116-V2.120 的目标是把阻断 final accepted 的真实证据缺口转成可复跑、可审计、可拒绝虚假通过的自动化验收流程。本阶段不扩大项目理解承诺，不声称完整恢复复杂项目设计意图，不声称 full call graph、runtime topology、data/control flow 或 type inference。

## 2. 当前事实基线

| 能力 | 当前状态 | 下一阶段目标 |
| --- | --- | --- |
| OCR/media | 200 个真实候选文件已 hash；缺合格 OCR 文本锚点；`status=needs_review` | 建立 OCR anchor registry，只有具备真实 source ref、hash、anchor 和 provider output 的行可 accepted |
| Source trace | 80 个 source trace 缺口保留为 `structured_unavailable` | 对 in-scope 文档补齐 import/query/source trace chain |
| UI evidence | HTML report 已生成；headless screenshot 未执行；`status=structured_unavailable` | 生成无焦点抢占 screenshot manifest，或记录浏览器依赖 blocker |
| Safe build | build queue 已保留；19 个 build 相关 unresolved；未批准命令不执行 | 引入 allowlist、审批、managed sandbox、timeout、独立 cache/output、日志脱敏、retry/resume；sandbox 未通过前只生成 proposal 和 structured blocker |
| Final gate | `portfolio_final_status=structured_unavailable` | 重新聚合证据，只有高风险项 accepted 或 approved out_of_scope 后才 final accepted |

## 3. 目标体验

| 用户 | 目标体验 |
| --- | --- |
| 维护者 | 在 `/knowledge` 或 HTML report 中看到 OCR 候选文件、文本锚点、source trace 缺口、UI 截图证据、安全 build 审批和 final gate 原因 |
| Agent | 通过 CLI/MCP/HTTP 读取下一步动作，只执行已批准的 build 命令，不把 unavailable 写成 accepted |
| 审计者 | 按 artifact refs、source refs、hash、focused test、E2E、PRD/spec review 和 false-green audit 复核每个 accepted 判断 |

## 4. 阶段拆分

| 阶段 | 名称 | 用户可体验结果 |
| --- | --- | --- |
| V2.116 | OCR Anchor and Provider Closure | 维护者能确认哪些媒体文件具备 OCR 样本资格，哪些缺 anchor，哪些 provider 执行失败 |
| V2.117 | Source Trace Batch Closure | 审计者能按文档行查看 import artifact、query result、source trace refs 和缺失原因 |
| V2.118 | Headless UI Visual Acceptance | 维护者能看到 `/knowledge` 或 HTML report 的真实截图证据；失败时看到浏览器依赖诊断 |
| V2.119 | Safe Build Allowlist Governance | Agent 只能在可信 approval 与 managed sandbox 同时存在时执行 allowlist 命令；否则只能看到 proposal、阻断原因和 next action |
| V2.120 | Final Portfolio Acceptance Rerun | 系统重新聚合全部证据，输出 final accepted 或可信 non-accepted |

## 5. In Scope

- OCR anchor registry、OCR 样本资格、provider execution、失败分类。
- Source import、query、source trace 三段证据链。
- Headless UI screenshot capture，优先无焦点抢占。
- Safe build allowlist、审批、managed sandbox、timeout、cache、独立 output/cache、日志脱敏、retry/resume。
- Decision Set 与 Evidence Decision Snapshot，用于记录 approved out_of_scope、人工确认、撤销/过期状态和绑定校验。
- Final gate rerun、PRD/spec review、false-green audit、acceptance package。

## 6. Out of Scope

- 自动安装 OCR、LibreOffice、Chrome/Chromium 或系统依赖。
- 自动修改、删除、移动或重写 `/mnt/c/workspace` 下被扫描项目。
- 自动执行未批准的外部项目任意 shell script。
- 把 PPT/PDF 直接文本抽取当成 OCR accepted。
- 把 HTML report、drawio、docs claim 当作 source/UI/build evidence。
- 默认修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。

## 7. 完成定义

文档阶段完成：

1. PRD、目标架构、开发验收计划、blueprint、schema、coverage matrix、测试映射、里程碑、gap analysis、pre-implementation audit、document audit 和 drawio 全部落盘。
2. drawio 不超过 8 页，中文书写，包含目标体验、当前到目标架构差异、代码实体分层、数据/证据流、开发验收计划、里程碑、出门条件和 No-Go。
3. P0 契约文档已落盘：run lineage、状态/审批、安全 build、public surface 注册、prototype/headless、详细测试 fixtures。
4. 机器 schema bundle 已落盘：`V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_SCHEMA_BUNDLE.json`。
5. 权威文档包 manifest 已落盘：`V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_CONTRACT_BUNDLE_MANIFEST.json`。
6. 已关闭支撑阶段级脚手架所需的 P0 契约冲突：schema bundle、状态算法、run/decision lifecycle、read-only UI、Source Trace 同源证明、OCR provider steps。
7. Safe Build managed sandbox 合同已定义，但真实外部 build 执行仍禁止，直到 sandbox 实现和 focused tests 通过。
8. 每个阶段都有 artifact contract、public surface、focused test、真实 E2E 输入、PRD/spec review 和 false-green audit。
9. 明确 final accepted 不得由 `needs_review`、`structured_unavailable`、`structured_blocker`、`failed` 推导。

实现阶段完成：

1. V2.116-V2.120 focused tests 全部通过。
2. 真实 `/mnt/c/workspace` E2E 完成，或每个不可用项有 structured blocker/unavailable reason。
3. `/knowledge` 或 HTML report 能展示真实证据、截图或结构化阻断。
4. public surface guard、compileall、frontend build、git diff checks 全部通过。
5. protected legacy files 未修改，除非用户明确批准。

## 8. 文档阶段状态

```text
documentation_status=pass_for_implementation_guidance
low_risk_scaffolding_readiness=pass
guided_phase_implementation_readiness=pass
autonomous_implementation_readiness=not_pass
continuous_v2_116_120_auto_implementation=not_approved
implementation_acceptance=not_pass
portfolio_final_acceptance=not_pass
major_document_gap=closed_for_implementation_guidance
safe_build_true_execution_readiness=not_pass_until_sandbox_verified
phase_specific_acceptance_logic_readiness=partial_pass_requires_schema_validation_and_focused_tests
```
