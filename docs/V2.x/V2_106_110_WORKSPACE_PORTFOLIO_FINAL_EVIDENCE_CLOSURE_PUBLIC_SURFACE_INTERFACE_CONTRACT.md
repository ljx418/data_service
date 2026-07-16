# V2.106-V2.110 Public Surface Interface Contract

## 1. Purpose

This document closes the CLI/MCP/HTTP contract gap. Public surface names alone are not enough for automated implementation.

## 2. Shared Request Fields

All plan/build/read/report surfaces use these shared fields where applicable:

```json
{
  "workspace_id": "string, required",
  "root": "configured allowed root or redacted root ref, required for plan/build",
  "run_id": "optional existing run id",
  "max_code_projects": "integer, default 3, min 0",
  "timeout_seconds": "integer, default 120, min 10",
  "dry_run": "boolean, default false",
  "include_ui_evidence": "boolean, default true",
  "allow_dependency_enablement": "boolean, default false"
}
```

Defaults must be recorded in run metadata.

## 3. CLI Contract

Commands:

```text
python -m data_service portfolio-final-evidence plan --workspace-id ID --root ROOT [--max-code-projects N] [--timeout-seconds N] [--dry-run]
python -m data_service portfolio-final-evidence build --workspace-id ID --root ROOT [--max-code-projects N] [--timeout-seconds N] [--include-ui-evidence true|false]
python -m data_service portfolio-final-evidence read --workspace-id ID [--run-id RUN]
python -m data_service portfolio-final-evidence report --workspace-id ID [--run-id RUN]
```

Exit codes:

| Exit code | Meaning |
| --- | --- |
| 0 | command completed and returned valid structured payload, even if payload status is non-accepted |
| 1 | invalid input or schema validation error |
| 2 | unsafe command or protected path violation |
| 3 | artifact missing, stale or mixed-run blocker |
| 4 | unexpected implementation failure |

CLI output must be JSON for plan/build/read and path or JSON envelope for report.

## 4. MCP Contract

Tools:

```text
knowledge_workspace_portfolio_final_evidence_plan
knowledge_workspace_portfolio_final_evidence_build
knowledge_workspace_portfolio_final_evidence_read
knowledge_workspace_portfolio_final_evidence_report
```

Input schema mirrors shared request fields. Output schema is the common artifact envelope with `data` matching the artifact schema contract.

MCP tools must not execute unsafe project commands unless build runtime policy approves them.

## 5. HTTP Contract

Routes:

```text
POST /api/workspaces/{workspace_id}/portfolio-final-evidence/plan
POST /api/workspaces/{workspace_id}/portfolio-final-evidence/build
GET  /api/workspaces/{workspace_id}/portfolio-final-evidence
GET  /api/workspaces/{workspace_id}/portfolio-final-evidence/report
```

HTTP status codes:

| Code | Meaning |
| --- | --- |
| 200 | structured payload returned |
| 400 | invalid request |
| 404 | workspace/run/artifact not found |
| 409 | lock conflict, stale artifact, mixed-run rejection |
| 422 | schema validation failure |
| 500 | unexpected implementation failure |

Error body:

```json
{
  "ok": false,
  "status": "failed|structured_blocker",
  "error_code": "string",
  "message": "safe public message",
  "unresolved": [],
  "next_actions": []
}
```

## 6. Idempotency and Concurrency

- `plan` is idempotent for the same root, input hashes and options.
- `build` creates a new run unless `run_id` is provided for safe resume.
- Concurrent build for the same workspace is rejected with HTTP 409 / CLI exit 3 unless dry-run.
- `read` returns latest compatible run unless `run_id` is specified.
- `report` reads existing artifacts; it must not fabricate missing evidence.

## 7. Registration Coverage

Implementation acceptance requires CLI, MCP and HTTP registration tests. A core JSON artifact implementation alone is insufficient for V2.110 stage acceptance.

