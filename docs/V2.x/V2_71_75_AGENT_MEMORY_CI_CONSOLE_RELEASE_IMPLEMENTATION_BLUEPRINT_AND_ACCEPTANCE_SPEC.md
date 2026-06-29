# V2.71-V2.75 Implementation Blueprint and Acceptance Spec

## 1. 目标

本文把 PRD 体验目标连接到目标架构、代码落点、public surface、artifact contract、focused tests 和出门验收。本文仍是实现指导，不是实现完成证据。

## 2. 代码落点

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

计划新增 public adapter：

```text
backend/data_service/mcp_code_agent_memory_release_tools.py
backend/data_service/cli_code_agent_memory_release.py
backend/app/api/v1/code_assets_agent_memory_release.py
```

禁止默认修改：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 3. 共享实现规则

- `build_*` 负责读取上游 artifact、生成本阶段 artifact，并返回 artifact refs。
- `read_*` 只读取已持久化 artifact，不重新制造事实。
- 所有 public payload 使用 repo-relative refs，不输出本地绝对路径。
- 每个 accepted row 必须绑定 evidence refs、command/result 或真实 adapter registry inspection。
- 每个 unavailable/blocker/needs_review row 必须保留 reason 和 next_action。
- HTML/console 只能渲染 structured artifact，不能硬编码 accepted 结论。

## 4. Service Contract

### 4.1 `external_project_closure.py`

计划 class：

```text
ExternalProjectClosureService
  build_external_project_closure(codebase_id, projects=None) -> dict
  read_external_project_closure(codebase_id) -> dict
```

输入来源：

- V2.63 external E2E artifacts；
- V2.67 path binding artifacts；
- 当前 `data_service` repo path；
- 可选外部项目真实 path。

输出：

```text
external_project_closure/project_binding_closure.json
external_project_closure/e2e_closure_report.md
```

验收：

- `data_service` 可以 accepted，但必须引用真实本地 repo 和真实 artifact。
- `codexPat`、`HarnessOS`、`Navia` 没有真实路径时必须是 `structured_unavailable`。
- `unavailable_accepted_count` 必须为 0。

### 4.2 `ci_warning_governance.py`

计划 class：

```text
CIWarningGovernanceService
  build_ci_warning_governance(codebase_id, command_results=None) -> dict
  read_ci_warning_governance(codebase_id) -> dict
```

输入来源：

- focused pytest command plan；
- full PRD revalidation warning counts；
- compileall、`git diff --check`、public surface guard；
- 后续实现阶段真实 pytest 输出。

输出：

```text
ci_warning_governance/ci_matrix.json
ci_warning_governance/warning_budget.json
ci_warning_governance/failure_diagnosis.json
ci_warning_governance/ci_readiness_report.md
```

验收：

- warning 超预算时阶段状态不能 accepted。
- failure category 只能使用：`dependency_drift`、`sandbox_limit`、`artifact_missing`、`public_surface_drift`、`real_regression`、`needs_review`。
- 不允许通过删除测试覆盖降低 warning 或运行时间。

### 4.3 `agent_memory.py`

计划 class：

```text
AgentMemoryService
  build_agent_memory(codebase_id) -> dict
  read_agent_memory(codebase_id) -> dict
```

输入来源：

- snapshot、inventory、symbol、trace、overview、DevWiki；
- Agent context pack；
- human portal、task workflow、evidence loop；
- external closure、CI governance、delivery、surface baseline、dashboard。

输出：

```text
agent_memory/memory_index.json
agent_memory/evidence_index.json
agent_memory/acceptance_state.json
agent_memory/task_briefing.json
agent_memory/retention_policy.md
```

验收：

- 每个 memory item 必须有 `source_artifact_ref`。
- 每个 recommendation 必须有 evidence refs 或 `needs_review`。
- 不声明通用聊天长期记忆；只声明项目情报长期记忆。

### 4.4 `interactive_console.py`

计划 class：

```text
InteractiveMaintainerConsoleService
  build_interactive_console(codebase_id) -> dict
  read_interactive_console(codebase_id) -> dict
```

输入来源：

- maintainer dashboard；
- Portal V3+；
- external closure；
- CI governance；
- agent memory；
- release restore。

输出：

```text
interactive_console/console_model.json
interactive_console/navigation_model.json
interactive_console/status_panels.json
interactive_console/maintainer_console.html
```

验收：

- 每个 panel 必须有 `status`、`artifact_ref`、`evidence_ref` 或 `unresolved`。
- HTML 不能隐藏 non-accepted。
- HTML 不显示 raw Mermaid source，也不创造 artifact 外事实。

### 4.5 `release_restore.py`

计划 class：

```text
ReleaseRestoreService
  build_release_restore(codebase_id) -> dict
  read_release_restore(codebase_id) -> dict
```

输入来源：

- delivery manifest；
- restore UX；
- public surface baseline；
- MCP/CLI/HTTP adapter registry；
- smoke command plan。

输出：

```text
release_restore/release_manifest.json
release_restore/mcp_config_template.json
release_restore/smoke_commands.md
release_restore/restore_runbook.md
release_restore/release_readiness_report.md
```

验收：

- redaction check 必须通过。
- smoke commands 覆盖 MCP、CLI、HTTP、focused tests。
- release readiness 不能把外部 unavailable 写成 accepted。

## 5. Public Surface

MCP tools：

```text
knowledge_code_agent_memory_release_external_closure_build
knowledge_code_agent_memory_release_external_closure_read
knowledge_code_agent_memory_release_ci_governance_build
knowledge_code_agent_memory_release_ci_governance_read
knowledge_code_agent_memory_release_memory_build
knowledge_code_agent_memory_release_memory_read
knowledge_code_agent_memory_release_console_build
knowledge_code_agent_memory_release_console_read
knowledge_code_agent_memory_release_release_restore_build
knowledge_code_agent_memory_release_release_restore_read
```

CLI commands：

```text
python -m data_service code agent-memory-release external-closure build/read
python -m data_service code agent-memory-release ci-governance build/read
python -m data_service code agent-memory-release memory build/read
python -m data_service code agent-memory-release console build/read
python -m data_service code agent-memory-release release-restore build/read
```

HTTP routes：

```text
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/external-closure/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/external-closure
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/ci-governance/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/ci-governance
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/memory/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/memory
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/console/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/console
POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/release-restore/build
GET  /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-memory-release/release-restore
```

## 6. Final Acceptance Signals

- V2.71-V2.75 focused tests pass。
- V2.63-V2.70 focused regression pass。
- `test_public_surface_guard.py` pass。
- `compileall` pass。
- `git diff --check` pass。
- protected legacy diff empty。
- real `data_service` E2E pass。
- external unavailable projects remain non-accepted unless real paths exist。
- PRD/spec review and false-green audit complete。

