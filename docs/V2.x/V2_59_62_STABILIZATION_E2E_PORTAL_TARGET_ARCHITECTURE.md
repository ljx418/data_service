# V2.59-V2.62 Target Architecture：Stabilization, E2E Expansion, Packaging, Portal UX

## 1. 架构目标

V2.59-V2.62 在 V2.54-V2.58 已验收实现之上增加一个“稳定交付层”。该层不替换现有 Human-Agent Deepening 服务，而是在其外侧补齐 contract、E2E、packaging、Portal integration 四类实体。

```text
V2.54-V2.58 accepted Human-Agent Deepening
  -> V2.59 Public Surface Stabilization
  -> V2.60 Real Project E2E Expansion
  -> V2.61 Acceptance Artifact Cleanup and Packaging
  -> V2.62 Human Portal UX Integration
```

## 2. 当前架构事实

当前已存在：

- `backend/data_service/code_assets/human_agent_deepening/` 服务层。
- MCP adapter：`backend/data_service/mcp_code_human_agent_deepening_tools.py`。
- CLI adapter：`backend/data_service/cli_code_human_agent_deepening.py`。
- HTTP adapter：`backend/app/api/v1/code_assets_human_agent_deepening.py`。
- public surface guard：`backend/tests/test_public_surface_guard.py`。
- focused tests：V2.54-V2.58。
- real E2E scripts：V2.55-V2.58。
- 阶段文档、coverage matrix、final acceptance audit。

当前架构差距：

- public surface 由测试守护，但缺少阶段专属 contract snapshot 和 drift artifact。
- real E2E 已覆盖 data_service/codexPat，但 HarnessOS/Navia 仍可能因为路径、依赖或时间预算不可用。
- `.tmp/`、依赖、验收脚本、文档包缺少清晰交付策略。
- Human Portal 尚未统一展示 contract stability、E2E coverage、restore readiness、delivery status。

## 3. 目标组件

### 3.1 Public Surface Contract Registry

职责：

- 读取 MCP、CLI、HTTP 当前注册信息。
- 生成 Human-Agent Deepening 专属 contract snapshot。
- 记录 build/read parity、route/tool/command naming、schema version、artifact refs。
- 生成 drift report，区分新增、删除、重命名、schema drift、route mismatch。

目标 artifact：

```text
stabilization/public_surface_snapshot.json
stabilization/public_surface_parity_matrix.json
stabilization/public_surface_drift_report.json
stabilization/migration_notes.md
```

### 3.2 Real Project E2E Runner Expansion

职责：

- 统一运行 data_service、codexPat、HarnessOS、Navia 的真实项目 E2E。
- 为不可用项目记录结构化原因和复查动作。
- 生成项目级 result、failure classification、artifact availability。

目标 artifact：

```text
e2e_expansion/project_e2e_matrix.json
e2e_expansion/project_failure_diagnosis.json
e2e_expansion/project_artifact_availability.json
e2e_expansion/e2e_expansion_report.md
```

### 3.3 Acceptance Package Manager

职责：

- 区分源代码、测试、文档、验收产物、本地临时目录。
- 生成 package manifest 和 cleanup plan。
- 检查 public artifact 不含 absolute path、secret、token、raw traceback。
- 提供 handoff checklist。

目标 artifact：

```text
packaging/package_manifest.json
packaging/cleanup_plan.md
packaging/handoff_checklist.md
packaging/package_audit_report.md
```

### 3.4 Human Portal Integration Layer

职责：

- 读取 V2.54-V2.61 persisted artifacts。
- 在 Portal 中展示项目状态、contract stability、real E2E coverage、restore readiness、delivery checklist。
- 保留 warning、unresolved、needs_review、structured_unavailable。

目标 artifact：

```text
portal_integration/portal_state_summary.json
portal_integration/portal_sections.json
portal_integration/portal_acceptance_panel.json
portal_integration/project_portal_v3.html
```

## 4. 目标架构关系

```text
Human-Agent Deepening Services
  -> Public Surface Contract Registry
  -> Real Project E2E Runner Expansion
  -> Acceptance Package Manager
  -> Human Portal Integration Layer
  -> Focused Tests / Public Surface Guard / Real E2E / Acceptance Audit
```

关系规则：

- Contract Registry 只读取注册表和公开 adapter，不修改业务服务。
- E2E Runner 只记录真实结果或结构化不可用，不伪造 accepted。
- Package Manager 可以建议清理，但不得自动删除未确认归属的用户文件。
- Portal Integration 只读取 persisted artifacts，不创造 artifact 外事实。

## 5. Public Contract

所有新 read output 使用阶段 schema：

```json
{
  "ok": true,
  "schema_version": "v2.59-62",
  "workspace_id": "string",
  "codebase_id": "string",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

Public payload 禁止包含：

- 本地 absolute path；
- secret、token；
- raw traceback；
- 未经证据支持的 accepted claim。

## 6. 架构门禁

- 每个 accepted capability 必须有 artifact path、focused test、real E2E 或 structured rationale。
- `structured_unavailable` 不能计入 accepted。
- Public surface 变更必须同步 contract snapshot 和 migration note。
- Portal 中每个状态项必须有 artifact_ref、evidence_ref 或 unresolved reason。
- 受保护 legacy 文件不得修改，除非用户明确批准。
