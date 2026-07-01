# V2.81-V2.85 Phase Readiness and Schema Contracts

## 1. 统一响应 contract

后续实现或补验 artifact 应保持以下公共字段：

```json
{
  "ok": true,
  "schema_version": "v2.81-85",
  "workspace_id": "string",
  "codebase_id": "string",
  "phase": "V2.81|V2.82|V2.83|V2.84|V2.85",
  "artifact_type": "string",
  "artifact_refs": ["repo-relative path or artifact URI"],
  "evidence_refs": ["repo-relative path or artifact URI"],
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

## 2. 状态 contract

- `accepted`：真实资料、真实命令/API/CLI/MCP、artifact refs、截图、PRD/spec review、false-green audit 均存在。
- `needs_review`：真实资料未提供、人工判断缺失、source trace 弱、质量审查缺失。
- `structured_unavailable`：外部项目路径、浏览器能力、真实资料访问条件不可用。
- `structured_blocker`：依赖、沙箱、权限、格式解析等阻断。

禁止转换：

- `needs_review` -> `accepted`，除非补齐真实证据。
- `structured_unavailable` -> `accepted`，除非外部条件真实可用并重新执行。
- `planned` -> `accepted`，除非实现、补验、审计全部完成。

## 3. Artifact schema 要求

### Sample Contract

必填字段：

- `sample_id`
- `source_type`
- `redaction_status`
- `acceptance_scope`
- `expected_paths`
- `privacy_warnings`
- `unresolved`

### Real Document E2E

必填字段：

- `workspace_id`
- `source_refs`
- `import_status`
- `build_status`
- `wiki_artifact_refs`
- `screenshot_refs`
- `failure_category`

### Query / GraphRAG / Source Trace

必填字段：

- `query_text`
- `result_status`
- `source_refs`
- `evidence_refs`
- `trace_status`
- `boundary_notes`

### Quality Governance

必填字段：

- `low_signal_findings`
- `feedback_refs`
- `correction_plan_refs`
- `review_status`
- `unresolved`

### Release Closure Rerun

必填字段：

- `real_document_acceptance_status`
- `external_project_status`
- `warning_gate_status`
- `restore_smoke_status`
- `human_approval_status`
- `final_release_status`

## 4. Public artifact 禁止内容

Public artifact 不得包含：

- 本地绝对路径；
- secret、token、private key；
- raw traceback；
- private virtualenv path；
- 未经证据支持的 accepted claim；
- 真实敏感文档原文。
