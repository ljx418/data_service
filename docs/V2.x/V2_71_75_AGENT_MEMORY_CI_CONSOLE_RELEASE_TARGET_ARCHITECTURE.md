# V2.71-V2.75 Target Architecture：Agent 记忆、CI 治理、控制台与发布恢复

## 1. 架构原则

- 以 V2.0-V2.70 已验收 artifact 为只读输入，不静默改写上游 artifact。
- 新能力写入独立 package，避免继续扩大 legacy 大文件。
- 所有 public output 必须包含 repo-relative artifact refs、evidence refs、warnings、unresolved 和 next actions。
- 任何 accepted 状态必须来自真实命令、真实 artifact 或真实 adapter registry inspection。
- `structured_unavailable`、`structured_blocker`、`needs_review` 必须完整保留给 Portal、控制台和 Agent memory。

## 2. 当前架构基线

已实现复用实体：

| 实体 | 状态 | 职责 |
| --- | --- | --- |
| `backend/data_service/code_assets/external_e2e_portal_delivery/path_binding.py` | 已实现 | 外部项目路径绑定和不可用状态 |
| `.../worktree_delivery.py` | 已实现 | 工作树交付分类和 reviewable cleanup plan |
| `.../surface_baseline.py` | 已实现 | public surface baseline |
| `.../maintainer_dashboard.py` | 已实现 | 维护者状态面板 artifact |
| `backend/data_service/code_assets/human_agent_deepening/restore_ux.py` | 已实现 | restore checklist 和 troubleshooting |
| `backend/data_service/code_assets/stabilization_e2e_portal/public_surface.py` | 已实现 | public surface parity 和 drift 检查 |
| `backend/data_service/mcp_code_external_e2e_portal_delivery_tools.py` | 已实现 | V2.63-V2.70 MCP build/read surface |
| `backend/data_service/cli_code_external_e2e_portal_delivery.py` | 已实现 | V2.63-V2.70 CLI surface |
| `backend/app/api/v1/code_assets_external_e2e_portal_delivery.py` | 已实现 | V2.63-V2.70 HTTP route family |

## 3. 目标新增分层

计划新增 package：

```text
backend/data_service/code_assets/agent_memory_release/
  __init__.py
  shared.py
  persistence.py
  external_project_closure.py
  ci_warning_governance.py
  agent_memory.py
  interactive_console.py
  release_restore.py
```

计划新增 adapter：

```text
backend/data_service/mcp_code_agent_memory_release_tools.py
backend/data_service/cli_code_agent_memory_release.py
backend/app/api/v1/code_assets_agent_memory_release.py
```

## 4. 目标架构实体

### 4.1 External Project Closure

输入：

- V2.67 path binding artifact；
- V2.63 external E2E artifact；
- 用户提供的真实 repo path；
- 当前 workspace asset registry。

输出：

- `external_project_closure/project_binding_closure.json`
- `external_project_closure/e2e_closure_report.md`

规则：

- `data_service` 可使用当前仓库真实路径。
- `codexPat`、`HarnessOS`、`Navia` 只有真实可读路径和真实 E2E 证据齐全才能 accepted。
- 不可用必须写为 `structured_unavailable` 或 `structured_blocker`。

### 4.2 CI Warning Governance

输入：

- focused pytest command plan；
- V2 full PRD revalidation warning counts；
- compileall、`git diff --check`、public surface guard 结果；
- 未来 CI job 配置。

输出：

- `ci_warning_governance/ci_matrix.json`
- `ci_warning_governance/warning_budget.json`
- `ci_warning_governance/failure_diagnosis.json`
- `ci_warning_governance/ci_readiness_report.md`

规则：

- warning 不能被忽略为 accepted；必须有 budget、owner、next_action。
- 慢测试只能通过分组、缓存、fixture 稳定化治理，不能删除覆盖。

### 4.3 Agent Long-term Memory

输入：

- snapshot、inventory、symbol、trace、overview、DevWiki；
- Agent context pack；
- human portal、task workflow、governance evidence loop；
- external E2E、delivery、surface baseline、dashboard；
- CI warning governance。

输出：

- `agent_memory/memory_index.json`
- `agent_memory/evidence_index.json`
- `agent_memory/acceptance_state.json`
- `agent_memory/task_briefing.json`
- `agent_memory/retention_policy.md`

规则：

- memory 只能引用 persisted artifacts，不生成无证据事实。
- 低置信或缺证据项必须进入 `needs_review`。
- 不提供通用聊天记忆承诺；本阶段只规划项目情报长期记忆。

### 4.4 Interactive Maintainer Console

输入：

- maintainer dashboard artifact；
- Portal V3+ artifact；
- agent memory artifact；
- CI governance artifact；
- release restore artifact。

输出：

- `interactive_console/console_model.json`
- `interactive_console/navigation_model.json`
- `interactive_console/status_panels.json`
- `interactive_console/maintainer_console.html`

规则：

- 控制台只能展示 artifact 支撑的状态。
- 必须显示 non-accepted 状态、next actions 和 stop conditions。
- 不隐藏 `structured_unavailable`、`structured_blocker`、`needs_review`。

### 4.5 Release Restore Packaging

输入：

- delivery manifest；
- restore UX；
- MCP/CLI/HTTP surface baseline；
- smoke command plan；
- public artifact redaction check。

输出：

- `release_restore/release_manifest.json`
- `release_restore/mcp_config_template.json`
- `release_restore/smoke_commands.md`
- `release_restore/restore_runbook.md`
- `release_restore/release_readiness_report.md`

规则：

- public artifact 不得包含本地绝对路径、secret、token、raw traceback、private venv path。
- 发布包只能说明可审计恢复路径；不能声称外部项目全部 accepted，除非真实证据存在。

## 5. Public Surface 规划

MCP tools 计划：

```text
knowledge_code_agent_memory_release_external_closure_build/read
knowledge_code_agent_memory_release_ci_governance_build/read
knowledge_code_agent_memory_release_memory_build/read
knowledge_code_agent_memory_release_console_build/read
knowledge_code_agent_memory_release_release_restore_build/read
```

CLI 计划：

```text
python -m data_service code agent-memory-release external-closure build/read
python -m data_service code agent-memory-release ci-governance build/read
python -m data_service code agent-memory-release memory build/read
python -m data_service code agent-memory-release console build/read
python -m data_service code agent-memory-release release-restore build/read
```

HTTP route family 计划：

```text
/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/external-closure
/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/ci-governance
/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/memory
/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/console
/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/release-restore
```

## 6. 禁止的架构设计

- “自动理解完整项目架构”这类没有 artifact、evidence、adapter 和验收面的模块。
- 只在 Portal/HTML 中硬编码 accepted 结论。
- 从文档标题推导代码事实。
- 修改 legacy 大文件来注册阶段能力。
- 自动删除 `.tmp/`、egg-info 或任何未确认归属文件。

