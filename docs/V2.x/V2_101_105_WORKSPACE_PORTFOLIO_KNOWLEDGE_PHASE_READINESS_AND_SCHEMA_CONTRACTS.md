# V2.101-V2.105 Phase Readiness and Schema Contracts

## 1. Unified Response Contract

所有 build/read 返回结构必须包含：

```json
{
  "ok": true,
  "schema_version": "v2.101-105",
  "workspace_id": "string",
  "phase": "V2.101|V2.102|V2.103|V2.104|V2.105",
  "status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "artifact_refs": ["repo-relative path or artifact id"],
  "evidence_refs": ["repo-relative path, command id, api result id, screenshot id"],
  "warnings": ["string"],
  "unresolved": [
    {
      "id": "string",
      "kind": "needs_review|structured_unavailable|structured_blocker",
      "reason": "string",
      "next_action": "string"
    }
  ],
  "next_actions": ["string"],
  "data": {}
}
```

## 2. Status Rules

- `accepted`：真实 workspace、真实命令/API/MCP/UI 证据完整，可复跑，可审计。
- `needs_review`：分类、资料归属、人工确认或风险判断不足。
- `structured_unavailable`：路径、OCR provider、系统依赖、文件格式或权限不可用，不是 accepted。
- `structured_blocker`：实现、依赖或环境阻断，不能被 release gate 放行。
- `failed`：命令或流程失败，必须保留失败原因。

## 3. Artifact Schemas

### 3.1 `project_registry.json`

必须包含：

- `schema_version`
- `workspace_id`
- `root_ref`
- `generated_at`
- `projects[]`
- `ignored[]`
- `warnings[]`
- `unresolved[]`

每个 project row 必须包含：

- `project_id`
- `display_name`
- `classification`
- `status`
- `path_ref`
- `detected_markers`
- `docs_refs`
- `media_summary`
- `evidence_refs`
- `next_actions`

### 3.2 `source_candidate_matrix.json`

必须包含：

- source path ref。
- source format。
- extractor availability。
- import plan。
- status。
- unsupported reason。
- evidence refs。

### 3.3 `media_readiness.json`

必须包含：

- image count。
- pdf count。
- ppt/pptx count。
- docx/yaml count。
- OCR provider health。
- conversion provider health。
- `ocr_required` rows。
- structured unavailable rows。

### 3.4 `project_build_runs.json`

必须包含：

- project id。
- build steps。
- code asset artifact refs。
- docs ingest artifact refs。
- command refs。
- status。
- warnings。
- unresolved。

### 3.5 `portfolio_index.json`

必须包含：

- accepted project count。
- needs_review count。
- structured_unavailable count。
- query entrypoints。
- project brief refs。
- project overview refs 或 structured gap。
- context pack refs 或 context availability status。

### 3.6 `release_gate.json`

必须包含：

- upstream phase statuses。
- UI evidence status。
- false-green audit status。
- `implementation_status`：本阶段功能实现、focused tests、真实 E2E、PRD/spec review、false-green audit 的综合状态。
- `portfolio_final_status`：workspace 项目组合内所有高风险项目、资料和媒体是否全绿 accepted。
- final status。
- blocker summary。
- next actions。

### 3.7 `/knowledge` portfolio read model

前端 read API 必须返回可直接渲染的结构化模型，至少包含：

- `status_header`：`final_status`、`implementation_status`、`portfolio_final_status`、`accepted_count`、`non_accepted_count`、`blocker_count`、`primary_next_action`。
- `registry_summary`：`code_project_count`、`doc_project_count`、`media_corpus_count`、`needs_review_count`、`structured_unavailable_count`。
- `build_summary`：`accepted_count`、`failed_count`、`structured_blocker_count`、`structured_unavailable_count`。
- `media_summary`：`ocr_provider_status`、`conversion_provider_status`、`ocr_required_count`、`unsupported_format_count`。
- `project_rows[]`：`project_id`、`display_name`、`classification`、`status`、`evidence_refs`、`artifact_refs`、`next_action`。
- `release_gate`：`final_status`、`no_go_findings[]`、`false_green_findings[]`、`next_actions[]`。

该 read model 只能由 persisted artifacts 组合而成。若上游 artifact 不存在，字段必须显示 `structured_unavailable` 或 `structured_blocker`，不得使用 demo data。

## 4. Public Output Redaction

Public artifacts 禁止包含：

- 本地绝对路径。
- secret、token、private key。
- raw traceback。
- 私有 virtualenv path。
- 未经证据支持的 accepted claim。

路径必须以 repo-relative、workspace-relative 或 `<workspace-root>/...` 表达。
