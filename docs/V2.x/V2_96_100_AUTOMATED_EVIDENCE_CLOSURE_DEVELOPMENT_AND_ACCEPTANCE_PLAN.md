# V2.96-V2.100 Development and Acceptance Plan

## 1. 阶段计划

| 阶段 | 开发目标 | 计划产物 | 用户可见体验 |
| --- | --- | --- | --- |
| V2.96 | 默认 shell CLI gap closure | `cli_gap_closure/cli_surface_result.json`、`cli_surface_report.md` | 用户能用默认命令验证 CLI surface，或看到明确 gap |
| V2.97 | Route A 自动证据包 | `route_a_evidence/material_scan.json`、`redaction_audit.json`、`evidence_capture_manifest.json`、`manual_confirmation_queue.md` | 用户提供真实资料后，系统自动生成证据包和最小人工确认清单 |
| V2.98 | 质量决策少人工工作流 | `quality_workbench/risk_queue.json`、`decision_recommendations.json`、`human_decision_backlog.md` | 用户只处理高风险和证据不足项 |
| V2.99 | 外部项目路径治理与 E2E | `external_path_registry/project_paths.json`、`project_smoke_matrix.json`、`unavailable_resolution.md` | 用户看到每个项目路径、E2E 状态和不可用原因 |
| V2.100 | 出门证据自动聚合 | `release_evidence_gate/evidence_summary.json`、`final_release_gate.md`、`false_green_recheck.md` | 用户看到 final release 是否可出门，以及阻断项补证路径 |

## 2. 子阶段流程

每个子阶段开始前必须落盘：

- phase-specific development plan。
- phase-specific acceptance plan。
- pre-implementation audit。

每个子阶段结束后必须落盘：

- focused test result。
- real workspace E2E result。
- PRD/spec review。
- false-green audit。
- acceptance audit report。

## 3. 验收规则

- 缺真实资料时 Route A 只能是 `needs_review`。
- 缺 reviewer decision 时 Quality 只能是 `needs_review`。
- 缺外部路径时 External Project 只能是 `structured_unavailable`。
- dependency hygiene 或 restore smoke 缺证据时 final release 不能 accepted。
- default shell CLI 未通过前，不能声明 CLI accepted。
- `docs/present/` 只允许作为理解材料，不作为 accepted evidence。

## 4. 真实数据要求

验收必须优先使用：

- `docs/V2.x` 中的真实 PRD、架构、验收文档。
- `workspace/data_service_docs_demo`、`workspace/v2_86_90_manual_experience`、`workspace/v2_91_95_real_acceptance_e2e` 等真实 workspace 产物。
- 用户提供的 Route A 真实资料目录。
- 可读的 `codexPat`、`HarnessOS`、`Navia` 路径；缺失时保留 structured unavailable。

## 5. 停止条件

出现以下情况时必须停止实现并返回计划阶段：

- 需要修改受保护 legacy 大文件但没有明确批准。
- 需要把 `needs_review`、`structured_unavailable` 或 `structured_blocker` 写成 accepted 才能通过测试。
- Route A、Quality、External 或 Release Gate 只能依赖 mock evidence。
- 文档和代码 public surface 发生重大偏差。
