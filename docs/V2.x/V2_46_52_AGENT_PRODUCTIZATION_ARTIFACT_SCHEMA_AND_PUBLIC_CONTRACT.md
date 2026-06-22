# V2.46-V2.52 Artifact Schema and Public Contract

## 1. Common Fields

所有 artifact 必须包含：

```json
{
  "schema_version": "v2.46-52",
  "workspace_id": "...",
  "codebase_id": "...",
  "snapshot_id": "...",
  "artifact_id": "...",
  "created_at": "...",
  "source_phase": "V2.46",
  "artifact_refs": [],
  "warnings": [],
  "unresolved": []
}
```

## 2. MCP Usage Guide Artifact

```json
{
  "artifact_type": "mcp_usage_guide",
  "codex_config": {},
  "recommended_workflows": [
    {
      "workflow_id": "coding_task_context",
      "steps": [
        {
          "tool": "knowledge_codebase_import",
          "purpose": "register project",
          "required": true
        }
      ],
      "failure_modes": []
    }
  ]
}
```

## 3. Project Profile Onboarding Artifact

```json
{
  "artifact_type": "project_profile_onboarding",
  "profile_id": "...",
  "terms": [],
  "entrypoint_patterns": [],
  "workflow_patterns": [],
  "authority_rules": [],
  "hardcode_audit": {
    "status": "passed",
    "violations": []
  }
}
```

## 4. Human Architecture Portal Artifact

```json
{
  "artifact_type": "human_architecture_portal",
  "title": "...",
  "sections": [],
  "charts": [
    {
      "chart_id": "...",
      "chart_type": "mermaid | svg | table | heatmap",
      "node_refs": [],
      "evidence_refs": []
    }
  ],
  "html_ref": "artifact://..."
}
```

## 5. Task Navigation Impact Artifact

```json
{
  "artifact_type": "task_navigation_impact_v2",
  "task": "...",
  "reading_order": [],
  "impact_candidates": [],
  "suggested_tests": [],
  "token_budget": {},
  "needs_review": []
}
```

## 6. Governance Workflow Artifact

```json
{
  "artifact_type": "doc_code_governance_workflow",
  "feedback": [],
  "rules": [],
  "reviews": [],
  "plans": [],
  "applied_rules": []
}
```

## 7. Agent Context Playbook Artifact

```json
{
  "artifact_type": "agent_context_playbook",
  "role": "maintainer | coding_agent | documentation_agent | architecture_reviewer",
  "mcp_steps": [],
  "recommended_prompts": [],
  "stop_conditions": [],
  "example_outputs": []
}
```

## 8. Public Envelope

Success：

```json
{
  "ok": true,
  "schema_version": "v2.46-52",
  "workspace_id": "...",
  "codebase_id": "...",
  "snapshot_id": "...",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

Error：

```json
{
  "ok": false,
  "schema_version": "v2.46-52",
  "workspace_id": "...",
  "codebase_id": "...",
  "snapshot_id": null,
  "error": {
    "code": "AGENT_PRODUCTIZATION_ARTIFACT_NOT_FOUND",
    "message": "...",
    "retryable": false
  },
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

## 9. Error Codes

- `MCP_PRODUCTIZATION_NOT_BUILT`
- `PROJECT_PROFILE_ONBOARDING_NOT_BUILT`
- `HUMAN_PORTAL_NOT_BUILT`
- `TASK_NAVIGATION_IMPACT_NOT_BUILT`
- `DOC_CODE_GOVERNANCE_WORKFLOW_NOT_BUILT`
- `AGENT_CONTEXT_PLAYBOOK_NOT_BUILT`
- `CONTINUOUS_ACCEPTANCE_NOT_BUILT`
- `PROJECT_REPO_UNAVAILABLE`
- `PROFILE_HARDCODE_VIOLATION`
- `PUBLIC_PAYLOAD_REDACTION_FAILED`

## 10. HTTP / MCP / CLI Parity

三端必须比较：

- `schema_version`
- `workspace_id`
- `codebase_id`
- `snapshot_id`
- artifact refs count
- warnings count
- unresolved count
- error code
- redaction status

## 11. Direct UI Route Contract

V2.48 Human Portal 默认可以作为 persisted HTML artifact 生成。如果实现新增 direct UI route，必须补充以下 contract，并纳入 V2.52 parity / exception audit：

```json
{
  "route_path": "/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/portal",
  "route_kind": "artifact_read | ui_only_read",
  "schema_version": "v2.46-52",
  "artifact_refs": [],
  "error_codes": [],
  "parity_mode": "http_mcp_cli | ui_only_exception",
  "exception_reason": null
}
```

规则：

- `artifact_read` route 必须有等价 MCP/CLI read contract，并比较 stable ids、artifact refs、warnings、unresolved、error code 和 redaction status。
- `ui_only_read` route 必须说明为什么不存在等价 MCP/CLI 输出，并指向可由 MCP/CLI 读取的底层 artifact。
- direct UI route 不得引入 persisted artifacts 中不存在的新事实。
- direct UI route public payload 不得泄露 absolute path、secret、token、raw traceback。

## 12. Accepted Implementation Evidence

任何 coverage matrix 行从 `planned` 改为 `accepted` 前，必须补齐：

```json
{
  "test_command": "...",
  "test_result": "passed",
  "artifact_path": "...",
  "real_repo_results": {
    "data_service": "accepted | structured_blocker | unavailable",
    "HarnessOS": "accepted | structured_blocker | unavailable",
    "Navia": "accepted | structured_blocker | unavailable",
    "codexPat": "accepted | structured_blocker | unavailable"
  },
  "parity_result": "passed | not_applicable_with_reason",
  "redaction_result": "passed",
  "no_hardcode_result": "passed",
  "acceptance_audit_ref": "docs/..."
}
```

缺少上述字段时，该行只能保持 `planned`、`not_implemented`、`structured_blocker`、`provider_unavailable` 或 `needs_review`，不得标记为 `accepted`。
