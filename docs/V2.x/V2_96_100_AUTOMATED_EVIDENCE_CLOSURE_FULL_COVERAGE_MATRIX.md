# V2.96-V2.100 Full Coverage Matrix

| PRD 能力 | 阶段 | 计划实体 | 计划 artifact | 当前状态 | Required Evidence |
| --- | --- | --- | --- | --- | --- |
| 默认 shell CLI closure | V2.96 | Default CLI Entrypoint Adapter | `cli_gap_closure/cli_surface_result.json` | accepted | shell command result、parser inventory、MCP/HTTP parity、focused test、real CLI E2E |
| CLI gap 报告 | V2.96 | CLI Gap Reporter | `cli_gap_closure/cli_surface_result.json` | accepted | gap diagnosis、accepted command、acceptance audit report |
| Route A 资料扫描 | V2.97 | Route A Evidence Automator | `route_a_evidence/material_scan.json` | needs_review | 代码和 artifact 已实现；最终 accepted 仍需用户代表性真实资料 refs |
| Route A 脱敏审查 | V2.97 | Route A Evidence Automator | `route_a_evidence/redaction_audit.json` | needs_review | 代码和 artifact 已实现；最终 accepted 仍需 redaction policy、risk、review state |
| Route A 截图证据 | V2.97 | Evidence Capture Runner | `route_a_evidence/evidence_capture_manifest.json` | needs_review | 代码和 artifact 已实现；最终 accepted 仍需 screenshot/headless refs 或 structured unavailable |
| Route A 人工确认 | V2.97 | Manual Confirmation Queue | `route_a_evidence/manual_confirmation_queue.md` | needs_review | 代码和 artifact 已实现；最终 accepted 仍需 reviewer decision |
| 质量风险队列 | V2.98 | Quality Decision Workbench | `quality_workbench/risk_queue.json` | needs_review | 代码和 artifact 已实现；高风险项最终 accepted 仍需 recommendation ids、risk levels、evidence refs |
| 质量决策建议 | V2.98 | Quality Decision Workbench | `quality_workbench/decision_recommendations.json` | needs_review | 代码和 artifact 已实现；自动建议不能替代 reviewer decision |
| 人工决策 backlog | V2.98 | Quality Decision Workbench | `quality_workbench/human_decision_backlog.md` | needs_review | 代码和 artifact 已实现；最终 accepted 仍需 high-risk human decisions |
| 外部项目路径 registry | V2.99 | External Project Path Registry | `external_path_registry/project_paths.json` | structured_unavailable | 代码和 artifact 已实现；缺 codexPat/HarnessOS/Navia readable path 时不可 accepted |
| 外部项目 smoke/E2E | V2.99 | External Project E2E Runner | `external_path_registry/project_smoke_matrix.json` | structured_unavailable | 代码和 artifact 已实现；缺外部项目 command refs、artifact refs、status 时不可 accepted |
| unavailable 决议 | V2.99 | External Project Path Registry | `external_path_registry/unavailable_resolution.md` | structured_unavailable | 代码和 artifact 已实现；unavailable reason、next action 保留 |
| 出门证据汇总 | V2.100 | Release Evidence Aggregator | `release_evidence_gate/evidence_summary.json` | structured_unavailable | 代码和 artifact 已实现；真实 E2E 中仍保留上游 non-accepted 状态 |
| final release gate | V2.100 | Release Evidence Aggregator | `release_evidence_gate/final_release_gate.md` | structured_unavailable | 代码和 artifact 已实现；缺 high-risk accepted / human approval 时不可 final accepted |
| false-green recheck | V2.100 | Release Evidence Aggregator | `release_evidence_gate/false_green_recheck.md` | accepted | non-accepted preservation 已由 focused tests、real CLI E2E 和 acceptance audit 验证 |

## 状态规则

- `planned`：文档规划完成，代码和证据未实现。
- `accepted`：真实资料、真实命令、artifact refs、PRD/spec review、false-green audit 全部具备。
- `needs_review`：缺人工判断、真实资料或高风险确认。
- `structured_unavailable`：路径、资料或环境不可用，不是 accepted。
- `structured_blocker`：实现、依赖或环境阻断，不是 accepted。

## 当前实现审计结论

- V2.96-V2.100 代码实体、CLI/MCP/HTTP surface、focused tests 和 artifact persistence 已落地。
- 本 matrix 中保留 `needs_review` / `structured_unavailable` 的行不是未实现代码，而是缺真实人工确认、外部项目路径或最终出门证据。
- 本阶段不能声明 final release 全绿；只能声明 pass for implemented and tested scope。

## 回填规则

任何 row 改为 `accepted` 前必须补齐：

- artifact path。
- focused test command and result。
- real project E2E result 或 structured unavailable rationale。
- PRD/spec review。
- false-green audit。
- acceptance audit report path。
