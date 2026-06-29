# V2.76-V2.80 Implementation Blueprint and Acceptance Spec

## 1. 目标

本文把 PRD 目标体验连接到目标架构、计划代码落点、public surface、artifact contract、focused tests 和出门验收。本文是后续实现指导，不是实现完成证据。

## 2. 代码落点

计划新增 package：

```text
backend/data_service/code_assets/project_acceptance_hardening/
  __init__.py
  shared.py
  persistence.py
  matrix_reconciliation.py
  external_project_binding.py
  warning_reduction.py
  console_productization.py
  release_readiness.py
```

计划新增 public adapter：

```text
backend/data_service/mcp_code_project_acceptance_hardening_tools.py
backend/data_service/cli_code_project_acceptance_hardening.py
backend/app/api/v1/code_assets_project_acceptance_hardening.py
```

禁止默认修改：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 3. 共享实现规则

- `build_*` 读取上游 artifact、生成本阶段 artifact，并返回 artifact refs。
- `read_*` 只读取已持久化 artifact，不重新制造事实。
- public payload 使用 repo-relative refs，不输出本地绝对路径。
- accepted 必须绑定 evidence refs、command/result 或真实 adapter registry inspection。
- unavailable/blocker/needs_review 必须保留 reason 和 next_action。
- HTML/console 只能渲染 structured artifact，不能硬编码 accepted 结论。

## 4. Service Contract

### 4.1 `matrix_reconciliation.py`

计划 class：

```text
AcceptanceMatrixReconciliationService
  build_reconciliation(codebase_id) -> dict
  read_reconciliation(codebase_id) -> dict
```

输出：

```text
acceptance_reconciliation/reconciled_matrix.json
acceptance_reconciliation/status_diff.json
acceptance_reconciliation/reconciliation_report.md
```

验收：

- planned/accepted 不一致必须进入 diff。
- accepted row 必须绑定真实 evidence。
- status conflict 不能自动 accepted。

### 4.2 `external_project_binding.py`

计划 class：

```text
ExternalProjectRealBindingService
  build_external_binding(codebase_id, project_paths=None) -> dict
  read_external_binding(codebase_id) -> dict
```

输出：

```text
external_project_binding/project_preflight.json
external_project_binding/e2e_rerun_records.json
external_project_binding/binding_decision_report.md
```

验收：

- 路径不可读时是 `structured_unavailable`。
- 依赖阻断时是 `structured_blocker`。
- accepted 必须有真实路径、preflight 和 E2E。

### 4.3 `warning_reduction.py`

计划 class：

```text
CIWarningReductionService
  build_warning_reduction(codebase_id, command_results=None) -> dict
  read_warning_reduction(codebase_id) -> dict
```

输出：

```text
warning_reduction/warning_inventory.json
warning_reduction/reduction_plan.json
warning_reduction/release_warning_gate.json
warning_reduction/warning_reduction_report.md
```

验收：

- warning 超预算时 release gate 不能 accepted。
- 每类 warning 必须有 owner 或 `needs_review`。
- 不允许通过删除测试覆盖降低 warning。

### 4.4 `console_productization.py`

计划 class：

```text
MaintainerConsoleProductizationService
  build_console_productization(codebase_id) -> dict
  read_console_productization(codebase_id) -> dict
```

输出：

```text
console_productization/experience_model.json
console_productization/panel_contract.json
console_productization/action_registry.json
console_productization/maintainer_console_product_report.md
```

验收：

- panel contract 覆盖 matrix、external projects、warning、release、human approval。
- 每个 action 有 planned surface 或 human decision route。
- non-accepted 状态不可隐藏。

### 4.5 `release_readiness.py`

计划 class：

```text
ReleaseReadinessClosureService
  build_release_readiness(codebase_id, approval_state=None) -> dict
  read_release_readiness(codebase_id) -> dict
```

输出：

```text
release_readiness/readiness_gate.json
release_readiness/restore_verification.json
release_readiness/smoke_run_records.json
release_readiness/handoff_package_manifest.json
release_readiness/release_closure_report.md
```

验收：

- restore、smoke、warning gate、redaction、public surface guard 均通过才可机器 accepted。
- 人工审批缺失时必须是 `needs_review`。
- public artifact 不泄露敏感信息。

## 5. Public Surface

MCP tools：

```text
knowledge_code_project_acceptance_hardening_matrix_build
knowledge_code_project_acceptance_hardening_matrix_read
knowledge_code_project_acceptance_hardening_external_binding_build
knowledge_code_project_acceptance_hardening_external_binding_read
knowledge_code_project_acceptance_hardening_warning_reduction_build
knowledge_code_project_acceptance_hardening_warning_reduction_read
knowledge_code_project_acceptance_hardening_console_product_build
knowledge_code_project_acceptance_hardening_console_product_read
knowledge_code_project_acceptance_hardening_release_readiness_build
knowledge_code_project_acceptance_hardening_release_readiness_read
```

CLI group：

```text
python -m data_service code project-acceptance-hardening <command>
```

HTTP route family：

```text
/api/workspaces/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/<capability>
```

## 6. Focused Tests

计划测试：

```text
backend/tests/test_v2_76_acceptance_matrix_reconciliation.py
backend/tests/test_v2_77_external_project_real_binding.py
backend/tests/test_v2_78_ci_warning_reduction.py
backend/tests/test_v2_79_maintainer_console_productization.py
backend/tests/test_v2_80_release_readiness_closure.py
```

所有测试必须配合 `backend/tests/test_public_surface_guard.py` 和 protected file diff check。
