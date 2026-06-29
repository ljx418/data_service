# V2.76-V2.80 Phase 152-156 Detailed Implementation Package

## 1. 使用方式

本文是后续自动化开发的阶段级执行包。它不证明任何功能已经实现，只把 V2.76-V2.80 的目标拆成可执行、可验收、可审计的子阶段。

每个子阶段必须按以下顺序执行：

1. 读取本阶段 PRD、目标架构、schema contract、coverage matrix。
2. 生成 phase-specific development plan。
3. 生成 phase-specific acceptance plan。
4. 生成 phase-specific pre-implementation audit。
5. 关闭 fatal/major finding。
6. 实现代码。
7. 运行 focused tests、真实 E2E、PRD/spec review、false-green audit。
8. 生成 acceptance audit report。

## 2. Phase 152 / V2.76 Acceptance Matrix Reconciliation

### 开发目标

把 V2.71-V2.75 的 coverage matrix、final acceptance audit、visual report、focused test result 和真实 E2E artifact 对齐，输出可机器读取的 observed status。

### 计划代码实体

```text
backend/data_service/code_assets/project_acceptance_hardening/matrix_reconciliation.py
AcceptanceMatrixReconciliationService
  build_reconciliation(codebase_id) -> dict
  read_reconciliation(codebase_id) -> dict
```

### 输入

- `V2_71_75_AGENT_MEMORY_CI_CONSOLE_RELEASE_FULL_COVERAGE_MATRIX.md`
- `V2_71_75_AGENT_MEMORY_CI_CONSOLE_RELEASE_FINAL_ACCEPTANCE_AUDIT_REPORT.md`
- `V2_71_75_STAGE_VISUAL_ACCEPTANCE_REPORT.html`
- V2.71-V2.75 persisted artifacts

### 输出

```text
acceptance_reconciliation/reconciled_matrix.json
acceptance_reconciliation/status_diff.json
acceptance_reconciliation/reconciliation_report.md
```

### 验收门槛

- 每个 accepted row 有 artifact_ref、test command/result、PRD/spec review、false-green audit。
- planned 与 accepted 冲突必须进入 `status_diff`。
- 缺证据项必须是 `needs_review`，不能 accepted。

### Focused Test

```text
pytest -q backend/tests/test_v2_76_acceptance_matrix_reconciliation.py
```

### False-green Audit

拒绝只根据 Markdown 文本把 row 标为 accepted。

## 3. Phase 153 / V2.77 External Project Real Binding

### 开发目标

为 `codexPat`、`HarnessOS`、`Navia` 提供真实路径接入、preflight 和 E2E rerun 机制。不可用状态必须保持结构化，不得计入 accepted。

### 计划代码实体

```text
backend/data_service/code_assets/project_acceptance_hardening/external_project_binding.py
ExternalProjectRealBindingService
  build_external_binding(codebase_id, project_paths=None) -> dict
  read_external_binding(codebase_id) -> dict
```

### 输入

- 用户提供的 project path map；
- V2.67 path binding artifact；
- V2.71 external closure artifact；
- dependency/preflight command plan。

### 输出

```text
external_project_binding/project_preflight.json
external_project_binding/e2e_rerun_records.json
external_project_binding/binding_decision_report.md
```

### 验收门槛

- 路径不可读：`structured_unavailable`。
- 路径可读但依赖或沙箱阻断：`structured_blocker`。
- accepted 必须有真实路径、真实 preflight、真实 E2E。
- unavailable_accepted_count 必须为 0。

### Focused Test

```text
pytest -q backend/tests/test_v2_77_external_project_real_binding.py
```

### False-green Audit

拒绝 mock-only evidence、硬编码路径和外部项目无路径 accepted。

## 4. Phase 154 / V2.78 CI Warning Reduction

### 开发目标

从 warning 可见治理推进到 warning inventory、owner、削减计划和 release warning gate。

### 计划代码实体

```text
backend/data_service/code_assets/project_acceptance_hardening/warning_reduction.py
CIWarningReductionService
  build_warning_reduction(codebase_id, command_results=None) -> dict
  read_warning_reduction(codebase_id) -> dict
```

### 输入

- V2.72 warning budget；
- pytest warning summary；
- warning category mapping；
- release gate policy。

### 输出

```text
warning_reduction/warning_inventory.json
warning_reduction/reduction_plan.json
warning_reduction/release_warning_gate.json
warning_reduction/warning_reduction_report.md
```

### 验收门槛

- 每类 warning 有 category、owner 或 `needs_review`。
- 超预算时 release warning gate 不能 accepted。
- warning 不能通过删除测试覆盖消失。

### Focused Test

```text
pytest -q backend/tests/test_v2_78_ci_warning_reduction.py
```

### False-green Audit

拒绝隐藏 warning、忽略 warning、删除测试覆盖、超预算 accepted。

## 5. Phase 155 / V2.79 Maintainer Console Productization

### 开发目标

把 V2.74 artifact-backed console 原型升级为产品化控制台模型：明确面板、动作、证据跳转、人工审批入口和 stop conditions。

### 计划代码实体

```text
backend/data_service/code_assets/project_acceptance_hardening/console_productization.py
MaintainerConsoleProductizationService
  build_console_productization(codebase_id) -> dict
  read_console_productization(codebase_id) -> dict
```

### 输入

- V2.70 maintainer dashboard；
- V2.74 interactive console；
- V2.76 reconciliation；
- V2.77 external binding；
- V2.78 warning reduction；
- V2.80 release readiness。

### 输出

```text
console_productization/experience_model.json
console_productization/panel_contract.json
console_productization/action_registry.json
console_productization/maintainer_console_product_report.md
```

### 验收门槛

- 每个 panel 有 status、source_artifact_ref、evidence_refs 或 unresolved。
- 每个 action 映射 planned MCP/CLI/HTTP surface 或人工流程。
- 控制台不能隐藏 `needs_review`、`structured_unavailable`、`structured_blocker`。

### Focused Test

```text
pytest -q backend/tests/test_v2_79_maintainer_console_productization.py
```

### False-green Audit

拒绝在 HTML 或控制台文案里硬编码成功状态。

## 6. Phase 156 / V2.80 Release Readiness Closure

### 开发目标

把 release readiness 从 `needs_review` 推进为可解释、可阻断、可审计的出门 gate。机器条件和人工审批必须拆开。

### 计划代码实体

```text
backend/data_service/code_assets/project_acceptance_hardening/release_readiness.py
ReleaseReadinessClosureService
  build_release_readiness(codebase_id, approval_state=None) -> dict
  read_release_readiness(codebase_id) -> dict
```

### 输入

- release manifest；
- restore runbook；
- MCP config template；
- smoke commands；
- warning gate；
- external binding decisions；
- human approval state。

### 输出

```text
release_readiness/readiness_gate.json
release_readiness/restore_verification.json
release_readiness/smoke_run_records.json
release_readiness/handoff_package_manifest.json
release_readiness/release_closure_report.md
```

### 验收门槛

- restore verification、smoke records、warning gate、redaction、public surface guard 通过，机器条件才可 accepted。
- 人工审批缺失时 release readiness 必须是 `needs_review`。
- 外部项目不可用时不能静默发布。

### Focused Test

```text
pytest -q backend/tests/test_v2_80_release_readiness_closure.py
```

### False-green Audit

拒绝跳过人工审批、跳过 restore、跳过 smoke、跳过 redaction、跳过 protected diff check。

## 7. 阶段最终验收命令

```text
pytest -q \
  backend/tests/test_v2_76_acceptance_matrix_reconciliation.py \
  backend/tests/test_v2_77_external_project_real_binding.py \
  backend/tests/test_v2_78_ci_warning_reduction.py \
  backend/tests/test_v2_79_maintainer_console_productization.py \
  backend/tests/test_v2_80_release_readiness_closure.py \
  backend/tests/test_public_surface_guard.py
python -m compileall backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 8. 必须停止的情况

- 需要修改 protected legacy 文件但没有用户明确批准。
- 外部项目无真实路径却被 accepted。
- warning 超预算却 release gate accepted。
- release readiness 缺人工审批却 accepted。
- public artifact 泄露本地绝对路径、secret、token、raw traceback。
