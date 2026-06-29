# V2.76-V2.80 Target Architecture：项目验收硬化与发布闭环

## 1. 架构原则

- 读取 V2.63-V2.75 persisted artifacts 作为只读输入，不静默改写上游 artifact。
- 新能力写入独立 package，避免扩大 legacy 大文件。
- 所有 public output 必须包含 repo-relative artifact refs、evidence refs、warnings、unresolved 和 next actions。
- accepted 必须来自真实命令、真实 artifact、真实 repo path 或真实 adapter registry inspection。
- `structured_unavailable`、`structured_blocker`、`needs_review` 必须被控制台、报告、Agent memory 和 release gate 保留。

## 2. 当前架构基线

| 实体 | 状态 | 职责 |
| --- | --- | --- |
| `backend/data_service/code_assets/external_e2e_portal_delivery/external_e2e.py` | 已实现 | 真实项目 E2E matrix |
| `.../path_binding.py` | 已实现 | 外部项目路径绑定和不可用状态 |
| `.../worktree_delivery.py` | 已实现 | 工作树交付分类和 reviewable cleanup plan |
| `.../surface_baseline.py` | 已实现 | public surface baseline 与 drift summary |
| `.../maintainer_dashboard.py` | 已实现 | 维护者首页状态 artifact |
| `backend/data_service/code_assets/agent_memory_release/external_project_closure.py` | 已实现 | 外部项目 closure，不接受 unavailable |
| `.../ci_warning_governance.py` | 已实现 | warning budget 与 failure diagnosis |
| `.../agent_memory.py` | 已实现 | Agent 项目记忆、证据索引和 acceptance state |
| `.../interactive_console.py` | 已实现 | artifact-backed 维护者控制台 HTML |
| `.../release_restore.py` | 已实现 | release manifest、MCP template、smoke、runbook |

## 3. 目标新增分层

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

计划新增 adapter：

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

## 4. 目标架构实体

### 4.1 Acceptance Matrix Reconciler

输入：

- V2.71-V2.75 coverage matrix；
- final acceptance audit；
- visual acceptance report；
- focused test results；
- real E2E artifacts。

输出：

- `acceptance_reconciliation/reconciled_matrix.json`
- `acceptance_reconciliation/status_diff.json`
- `acceptance_reconciliation/reconciliation_report.md`

规则：

- `planned` 只能在没有实现证据时保留。
- `accepted` 必须绑定 artifact path、test command/result、PRD/spec review 和 false-green audit。
- 文档状态和代码事实冲突时必须进入 `needs_review`。

### 4.2 External Project Binding Runner

输入：

- 用户提供的 `codexPat`、`HarnessOS`、`Navia` repo path；
- V2.67 path binding；
- V2.71 external closure；
- dependency/preflight command plan。

输出：

- `external_project_binding/project_preflight.json`
- `external_project_binding/e2e_rerun_records.json`
- `external_project_binding/binding_decision_report.md`

规则：

- 真实路径不可读时为 `structured_unavailable`。
- 依赖缺失但路径可读时为 `structured_blocker`。
- 只有真实 preflight 和 E2E 通过才能 accepted。

### 4.3 CI Warning Reduction Manager

输入：

- V2.72 warning budget；
- pytest warning summary；
- deprecation/source owner mapping；
- release gate policy。

输出：

- `warning_reduction/warning_inventory.json`
- `warning_reduction/reduction_plan.json`
- `warning_reduction/release_warning_gate.json`
- `warning_reduction/warning_reduction_report.md`

规则：

- warning 可以被分类、预算和削减，不能被隐藏。
- 删除测试覆盖不能作为 warning reduction evidence。
- 超预算时 release gate 不能 accepted。

### 4.4 Maintainer Console Productizer

输入：

- V2.70 dashboard；
- V2.74 interactive console；
- V2.76 reconciliation；
- V2.77 external binding；
- V2.78 warning reduction；
- V2.80 release readiness。

输出：

- `console_productization/experience_model.json`
- `console_productization/panel_contract.json`
- `console_productization/action_registry.json`
- `console_productization/maintainer_console_product_report.md`

规则：

- 控制台只能展示 structured artifact。
- 每个动作必须有 artifact_ref、evidence_ref 或 unresolved reason。
- non-accepted 状态不能被隐藏或改写。

### 4.5 Release Readiness Closer

输入：

- release manifest；
- restore runbook；
- MCP config template；
- smoke commands；
- warning gate；
- external binding decisions。

输出：

- `release_readiness/readiness_gate.json`
- `release_readiness/restore_verification.json`
- `release_readiness/smoke_run_records.json`
- `release_readiness/handoff_package_manifest.json`
- `release_readiness/release_closure_report.md`

规则：

- release accepted 需要 restore verification、smoke records、redaction check 和人工审批状态。
- 外部项目 unavailable 或 warning over budget 必须阻断或进入 `needs_review`。
- public artifact 不得包含本地绝对路径、secret、token、raw traceback、private venv path。

## 5. Public Surface 规划

MCP tools 计划：

```text
knowledge_code_project_acceptance_hardening_matrix_build/read
knowledge_code_project_acceptance_hardening_external_binding_build/read
knowledge_code_project_acceptance_hardening_warning_reduction_build/read
knowledge_code_project_acceptance_hardening_console_product_build/read
knowledge_code_project_acceptance_hardening_release_readiness_build/read
```

CLI 计划：

```text
python -m data_service code project-acceptance-hardening matrix build/read
python -m data_service code project-acceptance-hardening external-binding build/read
python -m data_service code project-acceptance-hardening warning-reduction build/read
python -m data_service code project-acceptance-hardening console-product build/read
python -m data_service code project-acceptance-hardening release-readiness build/read
```

HTTP route family 计划：

```text
/api/workspaces/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/matrix
/api/workspaces/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/external-binding
/api/workspaces/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/warning-reduction
/api/workspaces/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/console-product
/api/workspaces/{workspace_id}/codebases/{codebase_id}/project-acceptance-hardening/release-readiness
```

## 6. 禁止的架构设计

- “自动完整理解任意项目架构”这类没有 artifact、evidence、adapter 和验收面的模块。
- 只在 HTML 或报告里硬编码 accepted 结论。
- 从文档标题推导代码事实。
- 修改 legacy 大文件注册阶段能力。
- 自动删除 `.tmp/`、egg-info 或任何未确认归属文件。
- 用 mock-only evidence 接受外部项目。
