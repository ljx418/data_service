# V2.91-V2.95 Full Coverage Matrix

| PRD 能力 | 阶段 | 目标架构实体 | 计划 artifact | 验收证据 | 初始状态 |
| --- | --- | --- | --- | --- | --- |
| 本机验收 runtime 诊断 | V2.91 | Acceptance Runtime Restorer | `runtime_restore/runtime_diagnosis.json` | Python/pytest/venv/dependency baseline | planned |
| Focused regression 复跑 | V2.91 | Acceptance Runtime Restorer | `runtime_restore/focused_regression_result.json` | V2.81-V2.90 focused command result | planned |
| Route A 真实资料 manifest | V2.92 | Route A Material Intake and Review | `route_a_closure/material_manifest.json` | 资料来源、类型、repo-relative refs | needs_review |
| Route A 脱敏审查 | V2.92 | Route A Material Intake and Review | `route_a_closure/redaction_decision.json` | 脱敏策略、风险、人工确认 | needs_review |
| Route A 人工验收 | V2.92 | Route A Material Intake and Review | `route_a_closure/manual_acceptance_record.md` | 截图/headless evidence、reviewer decision | needs_review |
| 质量人工决策 | V2.93 | Human Quality Decision Recorder | `quality_decision/human_decisions.jsonl` | reviewer decision history | needs_review |
| Rule effect closure | V2.93 | Human Quality Decision Recorder | `quality_decision/rule_effect_closure.json` | upstream hash unchanged、effect summary | needs_review |
| 外部项目路径绑定 | V2.94 | External Project Path and E2E Validator | `external_project_closure/path_binding_decision.json` | data_service/codexPat/HarnessOS/Navia path status | structured_unavailable |
| 外部项目 E2E | V2.94 | External Project Path and E2E Validator | `external_project_closure/e2e_result_matrix.json` | accepted 或 structured unavailable/blocker | structured_unavailable |
| Final release gate | V2.95 | Final Release Gate Finalizer | `release_finalizer/final_gate_summary.json` | M1-M4、dependency、human approval | planned |
| False-green audit | V2.95 | Final Release Gate Finalizer | `release_finalizer/false_green_audit.md` | PRD/spec review、non-accepted preservation | planned |

## 状态规则

- `planned`：文档已规划，尚未实现或尚未验收。
- `accepted`：必须有真实资料、artifact refs、测试/API/CLI/MCP 结果、截图或人工签核、PRD/spec review、false-green audit。
- `needs_review`：缺人工判断、缺 Route A 资料、缺质量审查或证据不足。
- `structured_unavailable`：外部路径、环境或资料不可用，不是 accepted。
- `structured_blocker`：依赖、实现或环境阻断，不是 accepted。

## 回填规则

任何 row 改为 `accepted` 前必须补齐：

1. Artifact path。
2. Focused test command/result。
3. 真实资料 E2E result 或 structured unavailable/blocker reason。
4. PRD/spec review。
5. False-green audit。
6. Acceptance audit report path。
7. Protected legacy file diff check。

