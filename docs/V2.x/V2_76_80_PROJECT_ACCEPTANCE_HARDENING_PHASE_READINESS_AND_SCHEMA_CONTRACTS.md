# V2.76-V2.80 Phase Readiness and Schema Contracts

## 1. Phase Readiness Gate

每个子阶段开始实现前必须具备：

- phase-specific development plan；
- phase-specific acceptance plan；
- phase-specific pre-implementation audit；
- fatal/major finding 为 0；
- protected legacy file strategy；
- real data E2E strategy；
- false-green checklist。

## 2. 共享 Response Contract

```json
{
  "ok": true,
  "schema_version": "v2.76-80",
  "workspace_id": "string",
  "codebase_id": "string",
  "phase": "V2.76|V2.77|V2.78|V2.79|V2.80",
  "artifact_type": "string",
  "data": {},
  "artifact_refs": ["repo-relative path or artifact uri"],
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

## 3. Status Contract

允许状态：

- `planned`：文档规划，不能作为实现证据。
- `accepted`：必须有真实 artifact、命令、结果、PRD/spec review 和 false-green audit。
- `needs_review`：证据弱、缺失或需要人工判断。
- `structured_unavailable`：外部条件不可用，不是 accepted。
- `structured_blocker`：阻断，需要人工或环境变化。
- `out_of_scope`：明确不属于本阶段。

禁止状态转换：

- `structured_unavailable` -> `accepted`，除非真实路径、preflight、E2E 全部存在。
- `needs_review` -> `accepted`，除非补齐 evidence。
- `planned` -> `accepted`，除非实现、测试、E2E、审计全部完成。

## 4. Artifact Contract

每个 public artifact 必须满足：

- 含 `schema_version`、`workspace_id`、`codebase_id`、`phase`、`generated_at`。
- 引用路径使用 repo-relative path 或 artifact URI。
- 不包含本地绝对路径、secret、token、raw traceback、private virtualenv path。
- accepted row 必须含 evidence refs。
- unresolved row 必须含 reason 和 next_action。

## 5. 子阶段 Schema

### V2.76 Reconciled Matrix

必含字段：

- `capability_id`
- `prd_ref`
- `planned_status`
- `observed_status`
- `evidence_refs`
- `status_diff`
- `decision`

### V2.77 External Binding

必含字段：

- `project_id`
- `repo_path_status`
- `preflight_status`
- `e2e_status`
- `decision_status`
- `unresolved`

### V2.78 Warning Reduction

必含字段：

- `warning_id`
- `category`
- `owner`
- `baseline_count`
- `current_count`
- `budget`
- `release_gate_status`

### V2.79 Console Productization

必含字段：

- `panel_id`
- `source_artifact_ref`
- `status`
- `actions`
- `evidence_refs`
- `unresolved`

### V2.80 Release Readiness

必含字段：

- `restore_status`
- `smoke_status`
- `warning_gate_status`
- `external_project_status`
- `redaction_status`
- `human_approval_status`
- `readiness_status`

## 6. Public Output Redaction

发现以下内容必须标记 `structured_blocker`：

- 本地绝对路径；
- secret、token、authorization、bearer；
- raw traceback；
- private virtualenv path；
- 未经证据支持的 accepted claim。
