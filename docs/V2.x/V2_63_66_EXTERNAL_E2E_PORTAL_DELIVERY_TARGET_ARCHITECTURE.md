# V2.63-V2.66 Target Architecture：External E2E, Portal V3+, Delivery Versioning, Contract Regression

## 1. 架构目标

V2.63-V2.66 在 V2.59-V2.62 已验收的稳定交付层上增加“外部证据与交付回归层”。该层不替换 Human-Agent Deepening 或 Stabilization E2E Portal 服务，而是在其外侧补齐四类能力：

```text
V2.59-V2.62 accepted stabilization layer
  -> V2.63 External Project Full E2E
  -> V2.64 Portal V3+ Experience Hardening
  -> V2.65 Delivery Cleanup and Versioning
  -> V2.66 Public Surface Contract Regression
```

## 2. 当前架构事实

当前已存在：

- `backend/data_service/code_assets/human_agent_deepening/`：V2.54-V2.58 Human-Agent Deepening 服务层。
- `backend/data_service/code_assets/stabilization_e2e_portal/`：V2.59-V2.62 稳定交付层。
- MCP adapter、CLI adapter、HTTP adapter 的新增 public surface。
- public surface guard：`backend/tests/test_public_surface_guard.py`。
- focused tests：V2.54-V2.62。
- final acceptance audit：V2.54-V2.58 与 V2.59-V2.62。
- Portal V3、E2E expansion、package manifest、contract snapshot 等 persisted artifacts。

当前架构差距：

- 外部项目 E2E 仍可能停留在 `structured_unavailable`，缺少完整真实执行闭环。
- Portal 能汇总状态，但目标体验、风险优先级、合同回归和交付版本状态仍需更直观地呈现。
- 工作树和交付包需要版本化解释，避免把临时文件、测试依赖、验收产物混在一起。
- Public surface guard 能防漂移，但还需要跨阶段 baseline、diff 和 compatibility diagnosis。

## 3. 目标组件

### 3.1 External Full E2E Orchestrator

职责：

- 读取 data_service、codexPat、HarnessOS、Navia 的项目配置和可用性。
- 执行完整 artifact build/read、Portal read、contract read、restore/readiness 检查。
- 为每个项目输出 accepted、needs_review、structured_unavailable 或 structured_blocker。
- 将失败分类为 dependency_drift、sandbox_limit、path_unavailable、artifact_missing、public_surface_drift、real_regression、needs_review。

目标 artifact：

```text
external_e2e/full_project_matrix.json
external_e2e/project_run_records.json
external_e2e/artifact_readiness.json
external_e2e/external_e2e_report.md
```

### 3.2 Portal V3+ Experience Composer

职责：

- 读取 V2.54-V2.66 persisted artifacts。
- 生成维护者首页、外部 E2E 面板、合同稳定性面板、交付状态面板、风险与下一步动作。
- 保留 unresolved、needs_review、structured_unavailable、structured_blocker，不做视觉隐藏。
- 不从 HTML 或 UI 文案创造 artifact 外事实。

目标 artifact：

```text
portal_v3/experience_model.json
portal_v3/navigation_model.json
portal_v3/status_panels.json
portal_v3/project_portal_v3_plus.html
```

### 3.3 Delivery Version Manager

职责：

- 读取 git status、阶段文档、测试、验收报告和 persisted artifacts。
- 输出版本化交付清单、review package manifest、cleanup execution plan。
- 将文件分类为 commit_candidate、local_temp、manual_review、generated_evidence、out_of_scope。
- 不自动删除未确认归属的文件。

目标 artifact：

```text
delivery/version_manifest.json
delivery/review_package_manifest.json
delivery/cleanup_execution_plan.md
delivery/delivery_audit_report.md
```

### 3.4 Public Surface Contract Regression Engine

职责：

- 读取 V2.59-V2.62 contract snapshot 和当前 MCP、CLI、HTTP、artifact schema。
- 输出 baseline、diff、compatibility report 和 regression diagnosis。
- 区分 compatible_addition、compatible_schema_extension、breaking_removal、breaking_rename、schema_drift、route_mismatch、tool_command_mismatch、needs_review。

目标 artifact：

```text
contract_regression/contract_baseline.json
contract_regression/contract_diff.json
contract_regression/compatibility_report.json
contract_regression/regression_diagnosis.md
```

## 4. 目标架构关系

```text
V2.54-V2.62 persisted artifacts
  -> External Full E2E Orchestrator
  -> Portal V3+ Experience Composer
  -> Delivery Version Manager
  -> Public Surface Contract Regression Engine
  -> Focused Tests / Real E2E / PRD Review / False-green Audit / Acceptance Audit
```

关系规则：

- External E2E 只记录真实结果或结构化不可用，不伪造 accepted。
- Portal V3+ 只读取 persisted artifacts 和 E2E/contract/delivery 输出，不制造新事实。
- Delivery Version Manager 只生成计划和 manifest，不删除文件。
- Contract Regression Engine 只读取 public adapters 和 snapshot，不修改业务服务。
- 所有组件都不得修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。

## 5. Public Contract

所有新 read output 使用阶段 schema：

```json
{
  "ok": true,
  "schema_version": "v2.63-66",
  "workspace_id": "string",
  "codebase_id": "string",
  "phase": "V2.63|V2.64|V2.65|V2.66",
  "data": {},
  "artifact_refs": [],
  "evidence_refs": [],
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

Public payload 禁止包含：

- 本地 absolute path；
- secret、token；
- raw traceback；
- 未经证据支持的 accepted claim；
- 将 relationship chain、impact candidate 写成 full call graph 或 runtime call。

## 6. 架构门禁

- 每个 accepted capability 必须有 artifact path、focused test、真实 E2E 或明确的结构化证据。
- `structured_unavailable`、`structured_blocker`、`needs_review` 不能计入 accepted。
- Portal 中每个状态项必须有 artifact_ref、evidence_ref 或 unresolved reason。
- Contract regression 的 breaking change 必须进入 needs_review 或 structured_blocker，不能静默 accepted。
- Delivery cleanup 只能输出人工可审查计划，不能自动删除用户文件。
- 受保护 legacy 文件不得修改，除非用户明确批准。
