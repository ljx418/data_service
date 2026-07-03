# V2.91-V2.95 Phase Readiness and Schema Contracts

## 1. 统一响应合同

所有 build/read public surface 返回：

```json
{
  "ok": true,
  "schema_version": "v2.91-95",
  "workspace_id": "string",
  "codebase_id": "string",
  "phase": "V2.91|V2.92|V2.93|V2.94|V2.95",
  "status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "data": {},
  "artifact_refs": ["repo-relative path or artifact ref"],
  "evidence_refs": ["repo-relative path or artifact id"],
  "warnings": ["string"],
  "unresolved": [
    {
      "id": "string",
      "kind": "needs_review|structured_unavailable|structured_blocker",
      "status": "needs_review|structured_unavailable|structured_blocker",
      "reason": "string",
      "evidence_refs": ["string"],
      "next_action": "string"
    }
  ],
  "next_actions": ["string"]
}
```

Public artifact 禁止包含 secret、token、raw traceback、machine-specific virtualenv path、未脱敏私有资料内容。允许记录 repo-relative path 和 artifact id。

## 2. V2.91 Runtime Restore Schema

`runtime_diagnosis.json`：

```json
{
  "schema_version": "v2.91-95",
  "phase": "V2.91",
  "status": "accepted|structured_blocker|structured_unavailable",
  "python_runtime": {
    "system_python_available": true,
    "venv_create_available": true,
    "pytest_available": true,
    "legacy_venv_status": "usable|broken|not_found"
  },
  "commands": [
    {
      "command_id": "focused_regression",
      "command": "string",
      "exit_code": 0,
      "status": "accepted|failed|structured_blocker"
    }
  ],
  "unresolved": []
}
```

Acceptance rule：只有真实 pytest 命令 exit code 0，才可 accepted。

## 3. V2.92 Route A Closure Schema

`material_manifest.json`：

```json
{
  "schema_version": "v2.91-95",
  "phase": "V2.92",
  "status": "accepted|needs_review",
  "materials": [
    {
      "material_id": "string",
      "source_type": "document|html|markdown|json|drawio|other",
      "source_ref": "repo-relative or artifact ref",
      "redaction_status": "accepted|needs_review|structured_blocker",
      "evidence_refs": ["string"]
    }
  ],
  "manual_review": {
    "reviewer": "string",
    "decision": "accepted|needs_review|rejected",
    "decision_at": "ISO-8601 string",
    "evidence_refs": ["string"]
  },
  "unresolved": []
}
```

Acceptance rule：无真实资料或无人工 decision 时必须 `needs_review`。

## 4. V2.93 Quality Decision Schema

`rule_effect_closure.json`：

```json
{
  "schema_version": "v2.91-95",
  "phase": "V2.93",
  "status": "accepted|needs_review",
  "upstream_hashes": [
    {
      "artifact_ref": "string",
      "sha256": "string",
      "hash_unchanged": true
    }
  ],
  "decisions": [
    {
      "decision_id": "string",
      "target_ref": "string",
      "reviewer": "string",
      "decision": "approved|rejected|needs_review|revoked",
      "reason": "string",
      "evidence_refs": ["string"]
    }
  ],
  "unresolved": []
}
```

Acceptance rule：自动建议无人工 decision 时必须 `needs_review`。

## 5. V2.94 External Project Schema

`e2e_result_matrix.json`：

```json
{
  "schema_version": "v2.91-95",
  "phase": "V2.94",
  "status": "accepted|structured_unavailable|structured_blocker",
  "projects": [
    {
      "project_id": "data_service|codexPat|HarnessOS|Navia",
      "path_status": "readable|missing|permission_denied|needs_review",
      "e2e_status": "accepted|structured_unavailable|structured_blocker|failed",
      "command_refs": ["string"],
      "artifact_refs": ["string"],
      "unresolved": []
    }
  ]
}
```

Acceptance rule：缺路径项目不能 accepted，且不能计入 accepted count。

## 6. V2.95 Release Finalizer Schema

`final_gate_summary.json`：

```json
{
  "schema_version": "v2.91-95",
  "phase": "V2.95",
  "final_release_status": "accepted|needs_review|structured_unavailable|structured_blocker",
  "checks": [
    {
      "check_id": "runtime|route_a|route_b|full_corpus|quality|external_project|dependency_hygiene|restore_smoke|human_approval",
      "status": "accepted|needs_review|structured_unavailable|structured_blocker",
      "evidence_refs": ["string"],
      "unresolved": []
    }
  ],
  "false_green_audit": {
    "passed": true,
    "rejected_claims": ["string"]
  }
}
```

Acceptance rule：final release status 采用最高风险 non-accepted 状态；human approval 缺失不能 accepted。

## 7. Phase Readiness Gate

进入任何实现子阶段前必须满足：

- Phase-specific development plan 已落盘。
- Phase-specific acceptance plan 已落盘。
- Phase-specific pre-implementation audit 无 fatal 或 major。
- Artifact schema 与 focused test 已冻结。
- 受保护 legacy 文件无需修改，或已有用户明确批准。

