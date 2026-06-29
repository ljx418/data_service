# V2.76-V2.80 Development and Acceptance Plan

## 1. 开发计划

### V2.76 Acceptance Matrix Reconciliation

目标效果：

- 维护者能看到 V2.71-V2.75 PRD 能力、coverage matrix、final audit、visual report 和真实 artifacts 是否一致。

计划开发：

- 新增 matrix reconciler，读取 coverage matrix、final audit、visual report 和测试结果。
- 输出 reconciled matrix、status diff、reconciliation report。
- 对证据不足、状态冲突、planned/accepted 不一致项标记 `needs_review`。

验收：

- 每个 accepted row 必须有 artifact ref、test command/result、PRD/spec review、false-green audit。
- `planned` 不得和已验收 artifact 冲突。
- 状态冲突不能自动 accepted。

### V2.77 External Project Real Binding

目标效果：

- 维护者能为 `codexPat`、`HarnessOS`、`Navia` 提供真实路径，看到 preflight、依赖检查和 E2E rerun 结果。

计划开发：

- 新增 external project binding runner。
- 支持读取用户提供的 repo path map。
- 输出 project preflight、E2E rerun records、binding decision report。

验收：

- 不可读路径为 `structured_unavailable`。
- 依赖或沙箱阻断为 `structured_blocker`。
- accepted 必须有真实路径、真实 preflight 和真实 E2E。

### V2.78 CI Warning Reduction

目标效果：

- 维护者能看到 warning 类型、来源、owner、削减计划、预算变化和 release gate。

计划开发：

- 新增 warning inventory、reduction plan、release warning gate。
- 区分 deprecation、third-party、test fixture、legacy API、needs_review。
- 记录 warning 下降、持平、上升原因。

验收：

- warning 不能被隐藏。
- 删除测试覆盖不能作为 reduction evidence。
- 超预算时 release gate 不能 accepted。

### V2.79 Maintainer Console Productization

目标效果：

- 维护者能通过统一控制台理解状态、风险、下一步、证据跳转和出门条件。

计划开发：

- 新增 experience model、panel contract、action registry。
- 规划状态面板：验收矩阵、外部项目、warning、release、人工审批。
- 保留 V2.74 artifact-backed console，不创造 artifact 外事实。

验收：

- 每个 panel 必须有 status、artifact_ref、evidence_ref 或 unresolved reason。
- 每个 action 必须映射到 planned MCP/CLI/HTTP surface 或人工流程。
- 控制台不能隐藏 `needs_review`、`structured_unavailable`、`structured_blocker`。

### V2.80 Release Readiness Closure

目标效果：

- 维护者可以基于 restore verification、smoke records、warning gate、external binding 和人工审批判断是否发布。

计划开发：

- 新增 readiness gate、restore verification、smoke run records、handoff package manifest。
- 将 release accepted 条件拆成机器验收和人工审批。
- 继续执行 redaction check。

验收：

- release accepted 必须满足 restore、smoke、warning gate、redaction、public surface guard。
- 人工审批缺失时必须是 `needs_review`。
- 外部项目 unavailable 不得静默通过。

## 2. 总体验收命令计划

后续实现阶段计划新增：

```text
pytest -q \
  backend/tests/test_v2_76_acceptance_matrix_reconciliation.py \
  backend/tests/test_v2_77_external_project_real_binding.py \
  backend/tests/test_v2_78_ci_warning_reduction.py \
  backend/tests/test_v2_79_maintainer_console_productization.py \
  backend/tests/test_v2_80_release_readiness_closure.py \
  backend/tests/test_public_surface_guard.py
```

回归命令计划：

```text
pytest -q backend/tests/test_v2_71_external_project_binding_closure.py \
  backend/tests/test_v2_72_ci_warning_governance.py \
  backend/tests/test_v2_73_agent_long_term_memory_productization.py \
  backend/tests/test_v2_74_interactive_maintainer_console.py \
  backend/tests/test_v2_75_release_restore_packaging.py
python -m compileall backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 3. 审计意见

当前文档阶段目标是 pass for implementation guidance，不能写成 pass for implementation acceptance。开始写代码前仍必须为每个子阶段生成 phase-specific development plan、acceptance plan、pre-implementation audit，并关闭 fatal/major 审计意见。
