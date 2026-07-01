# V2.86-V2.90 Full Coverage Matrix

| PRD 能力 | 阶段 | 目标架构实体 | 计划 artifact | 验收证据 | 初始状态 |
| --- | --- | --- | --- | --- | --- |
| 全量真实文档构建 | V2.86 | Full Corpus E2E Runner | `full_corpus_e2e/full_corpus_run.json` | 全量 build command、artifact refs、截图或 headless evidence | planned |
| HTML extractor 失败分类 | V2.86 | Full Corpus E2E Runner | `full_corpus_e2e/parser_failures.json` | `Section` 错误复现、修复结果或 structured blocker | planned |
| 全量检索与 Source trace | V2.86 | Full Corpus E2E Runner | `full_corpus_e2e/full_corpus_report.md` | query result、source refs、GraphRAG boundary note | planned |
| Route A 资料包合同 | V2.87 | Route A Acceptance Pack | `route_a_acceptance/sample_pack_contract.json` | 来源类型、脱敏说明、用途边界 | needs_review |
| Route A 人工验收记录 | V2.87 | Route A Acceptance Pack | `route_a_acceptance/manual_acceptance_record.md` | 人工步骤、截图、签核结论 | needs_review |
| 质量治理人工审查 | V2.88 | Quality Review Recorder | `quality_review/human_quality_review.json` | reviewer decision、evidence refs、unresolved reason | needs_review |
| 纠错链路决策历史 | V2.88 | Quality Review Recorder | `quality_review/correction_decision_history.jsonl` | accept/reject/needs_review 记录 | needs_review |
| 外部项目路径绑定 | V2.89 | External Project Closure | `external_project_closure/path_manifest.json` | data_service/codexPat/HarnessOS/Navia path status | structured_unavailable |
| 外部项目真实 E2E | V2.89 | External Project Closure | `external_project_closure/project_e2e_records.json` | accepted 或 structured unavailable/blocker | structured_unavailable |
| 发布出门聚合 | V2.90 | Release Gate Aggregator | `release_gate/release_gate_summary.json` | M1-M4 状态、restore、dependency、approval | planned |
| 最终发布报告 | V2.90 | Release Gate Aggregator | `release_gate/release_readiness_report.md` | PRD/spec review、false-green audit、human approval | needs_review |

## Implementation Evidence Update

Date: 2026-07-01

| PRD 能力 | 实现状态 | 真实仓库验收状态 | 证据 |
| --- | --- | --- | --- |
| 全量真实文档构建 | implemented | accepted | `backend/tests/test_v2_86_full_corpus_e2e_hardening.py`，真实 `docs/V2.x` 处理 867 行 |
| HTML extractor 失败分类 | implemented | accepted | focused test 覆盖 `extractor_bug` structured blocker；真实仓库本轮无 parser failure |
| 全量检索与 Source trace | implemented | accepted | full corpus rows 使用 `repo://docs/V2.x/...` source refs，并保留 GraphRAG claim boundary |
| Route A 资料包合同 | implemented | needs_review | 缺用户代表性真实资料；`needs_review` 保留 |
| Route A 人工验收记录 | implemented | needs_review | 缺人工签核 evidence refs；不能 accepted |
| 质量治理人工审查 | implemented | needs_review | 缺真实人工 quality decisions；不能 accepted |
| 纠错链路决策历史 | implemented | needs_review | 结构已实现；真实决策缺失时保持 `needs_review` |
| 外部项目路径绑定 | implemented | structured_unavailable | `data_service` accepted；`codexPat`、`HarnessOS`、`Navia` 路径缺失 |
| 外部项目真实 E2E | implemented | structured_unavailable | 缺路径项目不计入 accepted |
| 发布出门聚合 | implemented | structured_unavailable | release gate 汇总 2 accepted、5 needs_review、1 structured_unavailable |
| 最终发布报告 | implemented | needs_review | human approval 缺失，final release 未 accepted |

本节更新的是实现证据状态，不改变 `needs_review` / `structured_unavailable` 的验收含义。任何缺少真实资料、人工审查或外部路径的能力仍不得写成 accepted。

## 状态规则

- `planned`：文档已规划，尚未实现或尚未验收。
- `accepted`：必须有真实资料、artifact refs、截图或 headless evidence、命令/API/CLI/MCP 结果、PRD/spec review 和 false-green audit。
- `needs_review`：证据弱、缺人工判断、缺 Route A 或缺质量审查。
- `structured_unavailable`：外部条件不可用，不是 accepted。
- `structured_blocker`：阻断，需要人工或环境变化。
- `out_of_scope`：必须有明确批准的 scope exception。

## 回填规则

任何 row 改为 `accepted` 前必须补齐：

1. artifact path。
2. focused test command/result。
3. 真实资料 E2E result 或 structured unavailable/blocker reason。
4. PRD/spec review。
5. false-green audit。
6. acceptance audit report path。
7. protected legacy file diff check。

Route A、外部项目、human approval 缺失时，相关 row 不能 accepted。
