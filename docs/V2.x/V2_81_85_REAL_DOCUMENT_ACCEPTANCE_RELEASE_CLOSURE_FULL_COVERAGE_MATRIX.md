# V2.81-V2.85 Full Coverage Matrix

| PRD 能力 | 阶段 | 计划 artifact | 验收证据 | 当前状态 |
| --- | --- | --- | --- | --- |
| 真实资料样本 contract | V2.81 | `real_document_acceptance/sample_contract.json` | 真实资料来源类型、脱敏说明、验收路径 | accepted for Route B |
| 人工场景计划 | V2.81 | `real_document_acceptance/manual_scenario_plan.md` | 用户步骤、截图标准、false-green checklist | accepted for Route B; Route A needs_review |
| 真实资料导入 | V2.82 | `real_document_acceptance/import_run.json` | source import result、artifact refs、截图 | accepted for Route B |
| Wiki artifact 验收 | V2.82 | `real_document_acceptance/wiki_artifact_review.json` | Wiki page / distill artifact / evidence refs | accepted for Route B |
| 检索体验验收 | V2.83 | `real_document_acceptance/query_trace_review.json` | query result、source refs、截图 | accepted for Route B |
| GraphRAG 体验验收 | V2.83 | `real_document_acceptance/graphrag_review.json` | graph result、边界声明、截图 | accepted for Route B |
| Source trace 验收 | V2.83 | `real_document_acceptance/source_trace_review.md` | source / unit / evidence path | accepted for Route B |
| 质量治理验收 | V2.84 | `real_document_acceptance/quality_governance_review.json` | low signal / feedback / correction plan | needs_review |
| 纠错链路验收 | V2.84 | `real_document_acceptance/correction_acceptance_report.md` | rule review、needs_review 保留 | needs_review |
| 发布闭环重跑 | V2.85 | `real_document_acceptance/release_closure_rerun.json` | V2.76-V2.80 evidence + real document evidence | structured_unavailable |
| 最终人工验收报告 | V2.85 | `real_document_acceptance/final_manual_acceptance_report.md` | 人工审批、截图、false-green audit | needs_review |

## 状态规则

- `planned`：文档阶段计划项，不是实现证据。
- `accepted`：必须有真实资料、artifact refs、截图、命令或 API/CLI/MCP 结果、PRD/spec review、false-green audit。
- `needs_review`：证据弱、缺失或需要人工判断。
- `structured_unavailable`：外部条件不可用，不是 accepted。
- `structured_blocker`：阻断，需要人工或环境变化。
- `out_of_scope`：明确不在本阶段。

## 回填规则

任何 row 从 `planned` 改为 `accepted` 前必须补齐：

- artifact path；
- evidence refs；
- focused test 或真实 E2E command/result；
- 截图证据；
- PRD/spec review；
- false-green audit；
- acceptance audit report。
