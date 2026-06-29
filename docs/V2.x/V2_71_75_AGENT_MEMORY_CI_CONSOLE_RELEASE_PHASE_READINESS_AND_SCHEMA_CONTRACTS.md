# V2.71-V2.75 Phase Readiness and Schema Contracts

## 1. 统一响应契约

计划新增 public artifact 和 adapter response 使用：

```json
{
  "ok": true,
  "schema_version": "v2.71-75",
  "workspace_id": "string",
  "codebase_id": "string",
  "phase": "V2.71|V2.72|V2.73|V2.74|V2.75",
  "data": {},
  "artifact_refs": ["repo-relative path"],
  "evidence_refs": ["repo-relative path or artifact id"],
  "warnings": ["string"],
  "unresolved": [
    {
      "kind": "needs_review|structured_unavailable|structured_blocker",
      "reason": "string",
      "next_action": "string"
    }
  ],
  "next_actions": ["string"]
}
```

## 2. Artifact 目录

计划输出目录：

```text
workspace/assets/codebase/{codebase_id}/agent_memory_release/
  external_project_closure/
  ci_warning_governance/
  agent_memory/
  interactive_console/
  release_restore/
```

## 3. Schema 要求

### V2.71 External Closure

必须包含：

- project_id；
- path_binding_status；
- e2e_status；
- accepted；
- evidence_refs；
- unresolved；
- next_action。

### V2.72 CI Warning Governance

必须包含：

- test_group；
- command；
- duration_budget；
- warning_budget；
- observed_warning_count；
- failure_category；
- next_action。

### V2.73 Agent Memory

必须包含：

- memory_item_id；
- source_artifact_ref；
- evidence_refs；
- confidence；
- status；
- retention_policy；
- expires_or_review_after。

### V2.74 Console

必须包含：

- panel_id；
- title；
- status；
- artifact_ref；
- evidence_ref；
- unresolved；
- next_action；
- user_visible_goal。

### V2.75 Release Restore

必须包含：

- release_item；
- classification；
- artifact_ref；
- smoke_command；
- redaction_status；
- restore_step；
- readiness_status。

## 4. Readiness Gate

实现开始前必须确认：

- 文档审计无 fatal/major。
- drawio 与 PRD/target architecture 一致。
- protected legacy 文件不需要修改。
- 新 surface 已纳入 public surface guard 计划。
- 真实数据验收使用当前 `data_service`。
- 外部项目路径不可用时不进入 accepted。

