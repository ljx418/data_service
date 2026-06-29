# V2.76-V2.80 Full Coverage Matrix

| PRD 能力 | 阶段 | 计划 artifact | 验收证据 | 当前状态 |
| --- | --- | --- | --- | --- |
| 文档/验收矩阵回填一致性 | V2.76 | `acceptance_reconciliation/reconciled_matrix.json` | coverage matrix、final audit、visual report、focused tests | planned |
| 状态差异报告 | V2.76 | `acceptance_reconciliation/status_diff.json` | planned/accepted conflict detection | planned |
| Reconciliation report | V2.76 | `acceptance_reconciliation/reconciliation_report.md` | PRD/spec review、false-green audit | planned |
| 外部项目 preflight | V2.77 | `external_project_binding/project_preflight.json` | real repo path、readability、dependency result | planned |
| 外部项目 E2E rerun | V2.77 | `external_project_binding/e2e_rerun_records.json` | accepted 或 structured unavailable/blocker | planned |
| Binding decision report | V2.77 | `external_project_binding/binding_decision_report.md` | unavailable 不计入 accepted | planned |
| Warning inventory | V2.78 | `warning_reduction/warning_inventory.json` | pytest warning summary、category、owner | planned |
| Warning reduction plan | V2.78 | `warning_reduction/reduction_plan.json` | budget、owner、next action | planned |
| Release warning gate | V2.78 | `warning_reduction/release_warning_gate.json` | over-budget blocks release accepted | planned |
| Console experience model | V2.79 | `console_productization/experience_model.json` | 维护者目标体验映射 | planned |
| Panel contract | V2.79 | `console_productization/panel_contract.json` | 每个 panel 有 evidence 或 unresolved | planned |
| Action registry | V2.79 | `console_productization/action_registry.json` | action 映射 MCP/CLI/HTTP 或人工流程 | planned |
| Readiness gate | V2.80 | `release_readiness/readiness_gate.json` | restore、smoke、warning、external、approval | planned |
| Restore verification | V2.80 | `release_readiness/restore_verification.json` | clean local restore result | planned |
| Smoke run records | V2.80 | `release_readiness/smoke_run_records.json` | MCP/CLI/HTTP/focused tests result | planned |
| Handoff package manifest | V2.80 | `release_readiness/handoff_package_manifest.json` | redaction、public surface、artifact manifest | planned |

## 状态规则

- `planned`：文档规划，不能作为实现证据。
- `accepted`：必须有真实 artifact、命令、结果、PRD/spec review 和 false-green audit。
- `structured_unavailable`：外部条件不可用，不是 accepted。
- `structured_blocker`：阻断，需要人工或环境变化。
- `needs_review`：证据弱、缺失或需要人工判断。
- `out_of_scope`：明确不属于本阶段。

## 回填规则

任何 row 从 `planned` 改为 `accepted` 前必须补齐：

- artifact path；
- focused test command/result；
- real project E2E result 或 structured unavailable/blocker rationale；
- PRD/spec review；
- false-green audit；
- acceptance audit report path。
