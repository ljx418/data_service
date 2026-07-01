# V2.86-V2.90 Phase Readiness and Schema Contracts

## 1. 统一响应合同

所有 V2.86-V2.90 public build/read payload 必须遵循：

```json
{
  "ok": true,
  "schema_version": "v2.86-90",
  "workspace_id": "string",
  "codebase_id": "string",
  "phase": "V2.86|V2.87|V2.88|V2.89|V2.90",
  "status": "planned|accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "artifact_refs": ["repo-relative path or artifact id"],
  "evidence_refs": ["repo-relative path or artifact id"],
  "warnings": ["string"],
  "unresolved": [
    {
      "kind": "needs_review|structured_unavailable|structured_blocker",
      "reason": "string",
      "next_action": "string"
    }
  ],
  "next_actions": ["string"],
  "data": {}
}
```

## 2. 状态规则

- `accepted`：必须有真实资料、真实执行、artifact refs、证据引用、PRD/spec review 和 false-green audit。
- `needs_review`：缺人工判断、缺 Route A、缺质量审查、证据弱或需维护者确认。
- `structured_unavailable`：路径、权限、资料或外部项目不可用；不是 accepted。
- `structured_blocker`：实现、依赖或环境阻断；不是 accepted。
- `failed`：真实执行失败，必须有 failure category 和 next action。

禁止把 `needs_review`、`structured_unavailable`、`structured_blocker`、`failed` 计入 accepted。

## 3. Full Corpus Schema

`full_corpus_e2e/full_corpus_run.json`：

```json
{
  "schema_version": "v2.86-90",
  "phase": "V2.86",
  "source_root": "docs/V2.x",
  "included_files": ["repo-relative path"],
  "excluded_files": ["repo-relative path"],
  "processed_count": 0,
  "accepted_count": 0,
  "failure_count": 0,
  "status": "accepted|needs_review|structured_blocker|failed",
  "artifact_refs": [],
  "evidence_refs": [],
  "unresolved": []
}
```

`full_corpus_e2e/parser_failures.json`：

```json
{
  "schema_version": "v2.86-90",
  "phase": "V2.86",
  "failures": [
    {
      "path": "repo-relative path",
      "parser": "markdown|html|json|drawio|unknown",
      "category": "extractor_bug|unsupported_format|empty_content|dependency_drift|sandbox_limit|needs_review",
      "message": "redacted summary",
      "status": "needs_review|structured_blocker|failed",
      "next_action": "string"
    }
  ]
}
```

Raw traceback 不得进入 public artifact。

## 4. Route A Schema

`route_a_acceptance/sample_pack_contract.json`：

```json
{
  "schema_version": "v2.86-90",
  "phase": "V2.87",
  "source_type": "user_representative|redacted_user_representative|structured_unavailable",
  "sample_pack_ref": "repo-relative path or artifact id",
  "redaction_policy_ref": "repo-relative path or artifact id",
  "acceptance_scope": "string",
  "status": "accepted|needs_review|structured_unavailable",
  "unresolved": []
}
```

`route_a_acceptance/manual_acceptance_record.md` 必须包含：

- 资料来源说明。
- 脱敏确认。
- 最小人工体验步骤。
- 截图或 headless evidence refs。
- reviewer decision。
- release impact。

## 5. Quality Review Schema

`quality_review/human_quality_review.json`：

```json
{
  "schema_version": "v2.86-90",
  "phase": "V2.88",
  "reviewer": "human|structured_unavailable",
  "decisions": [
    {
      "recommendation_id": "string",
      "decision": "accepted|rejected|needs_review",
      "evidence_refs": [],
      "reason": "string",
      "next_action": "string"
    }
  ],
  "status": "accepted|needs_review"
}
```

`quality_review/correction_decision_history.jsonl` 每行必须是独立 JSON，包含 recommendation id、decision、evidence refs、timestamp 和 reviewer state。

## 6. External Project Schema

`external_project_closure/path_manifest.json`：

```json
{
  "schema_version": "v2.86-90",
  "phase": "V2.89",
  "projects": [
    {
      "project_id": "data_service|codexPat|HarnessOS|Navia",
      "path_status": "available|structured_unavailable|structured_blocker",
      "path_ref": "redacted path label or repo-relative ref",
      "reason": "string",
      "next_action": "string"
    }
  ]
}
```

`external_project_closure/project_e2e_records.json`：

```json
{
  "schema_version": "v2.86-90",
  "phase": "V2.89",
  "records": [
    {
      "project_id": "string",
      "e2e_status": "accepted|structured_unavailable|structured_blocker|failed",
      "command_ref": "string",
      "artifact_refs": [],
      "evidence_refs": [],
      "unresolved": []
    }
  ]
}
```

External unavailable 不得计入 accepted。

## 7. Release Gate Schema

`release_gate/release_gate_summary.json`：

```json
{
  "schema_version": "v2.86-90",
  "phase": "V2.90",
  "route_a_status": "accepted|needs_review|structured_unavailable",
  "route_b_status": "accepted|needs_review",
  "full_corpus_status": "accepted|needs_review|structured_blocker|failed",
  "quality_review_status": "accepted|needs_review",
  "external_project_status": "accepted|structured_unavailable|structured_blocker|failed",
  "human_approval_status": "accepted|needs_review",
  "restore_smoke_status": "accepted|needs_review|failed",
  "dependency_hygiene_status": "accepted|needs_review|failed",
  "final_release_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "blocking_reasons": ["string"],
  "artifact_refs": [],
  "evidence_refs": []
}
```

`final_release_status` 只能在所有必要条件 accepted 后为 `accepted`。

## 8. Readiness Checklist

进入每个子阶段代码实现前必须具备：

1. 子阶段 development plan。
2. 子阶段 acceptance plan。
3. pre-implementation audit，无 fatal/major。
4. schema contract 已冻结。
5. focused test 名称已确定。
6. 真实资料或 structured unavailable 路径已定义。
7. false-green 风险已列出。

未满足以上条件时，不进入实质开发。
