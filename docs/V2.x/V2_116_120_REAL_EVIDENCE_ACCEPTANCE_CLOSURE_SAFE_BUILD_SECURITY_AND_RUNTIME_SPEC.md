# V2.116-V2.120 Safe Build Security and Runtime Spec

## 1. No-execution Default

V2.119 默认只生成 proposed commands 和 allowlist proposal。没有可信 approval 和 managed execution sandbox 时，不得执行外部项目命令。

在 sandbox 未实现并通过 focused tests 前，V2.119 只能输出：

```text
safe_build_allowlist.json
safe_build_governance_report.md
row_acceptance_status=structured_blocker
failure_category=sandbox_not_available
```

不得执行真实外部项目 build/test/lint 命令。

## 2. Command Normalization

`safe_build_allowlist.json` 中的每条命令必须归一化：

```json
{
  "command_id": "string",
  "project_id": "string",
  "project_root": "workspace-relative path",
  "argv": ["string"],
  "cwd": "managed sandbox working copy path",
  "normalized_binding_digest": "sha256",
  "sandbox_policy_digest": "sha256",
  "project_input_hash": "sha256",
  "risk_level": "low|medium|high|critical",
  "approval_decision_id": "string|null",
  "approval_status": "approved|needs_review|rejected"
}
```

禁止：

- `shell=True`
- 单字符串 shell 命令
- shell metacharacter 注入
- 未绑定 approval digest 的命令执行

## 3. Managed Execution Sandbox

真实命令只能在 managed sandbox 内运行，不能以外部项目目录作为直接可写 cwd：

```text
runs/{run_id}/run_sandbox/{project_id}/
  readonly_input/
  working_copy_or_overlay/
  home/
  cache/
  tmp/
  output/
  logs/
```

约束：

- `readonly_input/` 是外部项目的只读快照、只读挂载或 hash-verified copy。
- `working_copy_or_overlay/` 是唯一可写工作目录。
- `HOME`、`TMPDIR`、cache 和 output 必须重定向到 sandbox 内。
- 原始 `/mnt/c/workspace/*` 项目不得被命令写入。
- 如果当前平台无法提供只读输入或可写 overlay，执行结果必须是 `structured_blocker`。

## 4. Path and Workspace Boundary

- `cwd` 必须 realpath 后位于 `working_copy_or_overlay/` 下。
- `readonly_input/` 的 source root 必须位于 configured workspace root 下。
- symlink escape、`..` traversal、绝对路径越界必须拒绝。
- 输出目录必须写入 managed workspace 的 run 目录，不写入被扫描项目。

## 5. Environment Policy

默认 env allowlist：

```text
PATH
HOME
LANG
LC_ALL
PYTHONPATH only when explicitly needed and redacted
```

必须移除或脱敏：

```text
*_TOKEN
*_KEY
*_SECRET
PASSWORD
AUTHORIZATION
HTTP_PROXY
HTTPS_PROXY
```

命令 digest 必须覆盖：

```text
executable_realpath
executable_hash
argv
cwd
environment_policy_digest
project_input_hash
timeout_and_resource_limits
network_policy
output_policy
```

仅绑定 argv 的 approval 不得执行。

## 6. Runtime Limits

每个命令必须配置：

- timeout_seconds
- max_stdout_bytes
- max_stderr_bytes
- process_group kill on timeout
- retry_count
- cache/output directory

如无法限制 CPU、内存、磁盘或网络，必须在 `safe_build_execution_results.json` 中记录 `runtime_limit_unavailable`，不得将该项目 build row 写成 final accepted。

## 7. Execution Result Schema

`safe_build_execution_results.json`：

```json
{
  "schema_version": "v2.116-120",
  "workspace_id": "string",
  "run_id": "string",
  "generated_at": "ISO-8601 string",
  "rows": [
    {
      "command_id": "string",
      "project_id": "string",
      "approval_decision_id": "string|null",
      "normalized_binding_digest": "sha256",
      "sandbox_ref": "runs/{run_id}/run_sandbox/{project_id}",
      "sandbox_policy_digest": "sha256",
      "project_input_hash": "sha256",
      "execution_status": "skipped|succeeded|failed|timeout|blocked",
      "row_acceptance_status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
      "started_at": "ISO-8601 string|null",
      "ended_at": "ISO-8601 string|null",
      "exit_code": 0,
      "stdout_ref": "workspace-relative path|null",
      "stderr_ref": "workspace-relative path|null",
      "stdout_sha256": "string|null",
      "stderr_sha256": "string|null",
      "redaction_passed": true,
      "process_tree_cleanup_passed": true,
      "original_project_write_check_passed": true,
      "timeout_seconds": 120,
      "failure_category": "sandbox_not_available|approval_missing|path_escape_attempt_blocked|path_escape_guard_bypassed|timeout|nonzero_exit|runtime_limit_unavailable|secret_redaction_failure|child_process_cleanup_failed|null"
    }
  ],
  "artifact_refs": ["workspace-relative path"],
  "evidence_refs": ["string"],
  "unresolved": []
}
```

## 8. No-Go

- npm、make、pip、python setup 等项目脚本默认为 high risk。
- 未批准 high-risk command 不执行。
- Approval normalized binding digest 与实际 executable、argv、cwd、env、sandbox、project input、runtime、network 或 output policy 不一致，不执行。
- Approval normalized binding digest 缺少 sandbox、env、executable 或 project input hash，不执行。
- timeout 后子进程未确认清理，不能 accepted。
- path escape、secret redaction failure、child process cleanup failure 为 non-waivable，不得通过 approved out-of-scope 转为 final accepted。
