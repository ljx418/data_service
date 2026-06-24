# V2.63-V2.66 Phase Readiness and Schema Contracts

## 1. 阶段 readiness

进入 V2.63 实现前必须确认：

- V2.63-V2.66 总 PRD、目标架构、开发验收计划、milestones、coverage matrix、gap/drawio、implementation blueprint 已存在。
- drawio 已由人类确认方向未偏移、未过度承诺。
- 外部项目路径、依赖和运行权限已重新确认或结构化标记。
- public surface baseline 只能来自实际 adapter 或 persisted artifact，不能只来自文档。
- protected legacy 文件没有未授权修改。

## 2. 共享 response contract

```json
{
  "ok": true,
  "schema_version": "v2.63-66",
  "workspace_id": "string",
  "codebase_id": "string",
  "phase": "V2.63|V2.64|V2.65|V2.66",
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

## 3. V2.63 external E2E schema

```json
{
  "project_id": "data_service|codexPat|HarnessOS|Navia",
  "status": "accepted|needs_review|structured_unavailable|structured_blocker",
  "path_status": "available|path_unavailable|needs_review",
  "dependency_status": "available|dependency_drift|sandbox_limit|needs_review",
  "artifact_status": "accepted|artifact_missing|needs_review",
  "commands": ["string"],
  "evidence_refs": ["repo-relative path"],
  "failure_category": "dependency_drift|sandbox_limit|path_unavailable|artifact_missing|public_surface_drift|real_regression|needs_review|null"
}
```

## 4. V2.64 Portal V3+ schema

```json
{
  "sections": [
    {
      "id": "external_e2e|contract|delivery|risk|next_actions|exit_status",
      "title": "string",
      "status": "accepted|needs_review|structured_unavailable|structured_blocker",
      "artifact_refs": ["repo-relative path"],
      "evidence_refs": ["repo-relative path"],
      "unresolved": []
    }
  ],
  "html_artifact": "repo-relative path"
}
```

## 5. V2.65 delivery schema

```json
{
  "files": [
    {
      "path": "repo-relative path",
      "classification": "commit_candidate|generated_evidence|local_temp|manual_review|out_of_scope",
      "reason": "string",
      "safe_to_delete": false
    }
  ],
  "version_label": "string",
  "review_required": true
}
```

`safe_to_delete` 默认必须为 false，除非用户明确批准执行清理。

## 6. V2.66 contract regression schema

```json
{
  "surface": "mcp|cli|http|artifact_schema",
  "item": "string",
  "change_type": "compatible_addition|compatible_schema_extension|breaking_removal|breaking_rename|schema_drift|route_mismatch|tool_command_mismatch|needs_review",
  "compatibility": "compatible|breaking|needs_review",
  "baseline_ref": "repo-relative path",
  "current_ref": "repo-relative path",
  "diagnosis": "string",
  "next_action": "string"
}
```

## 7. Public artifact redaction

任何 public artifact 禁止包含：

- 本地 absolute path。
- secret、token。
- raw traceback。
- private virtualenv path。
- 未经证据支持的 accepted claim。
