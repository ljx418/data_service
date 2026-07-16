# V2.106-V2.110 Build Execution Security and Runtime Spec

## 1. Purpose

This document closes the P0 build safety gap. V2.108 may inspect and orchestrate external workspace projects, but must not run arbitrary untrusted project commands without explicit safety controls.

## 2. Default Runtime Mode

Default mode:

```text
read_only_input_with_external_output
```

Rules:

- External project directories are read-only inputs.
- Build outputs, caches and temporary files must be written under the data_service workspace artifact area or a generated temp directory outside the scanned project.
- The implementation must not delete, move, rewrite or format files in scanned projects.
- If read-only execution cannot be guaranteed, the job must be `structured_blocker` or `needs_review`, not accepted.

## 3. Command Source and Allowlist

Allowed command sources:

- data_service-owned code asset commands
- documented safe inspection commands
- explicit user-approved commands recorded as evidence

Forbidden by default:

- project-defined install scripts
- package manager lifecycle scripts
- shell pipelines derived from project files
- commands containing unescaped user/project input
- commands requiring credentials or privileged access

Every command must record:

```text
command_id
argv array
working_directory policy
environment policy
timeout_seconds
network_policy
output_redaction_policy
```

## 4. Process Isolation

Required controls:

- no inherited secrets by default
- minimal environment variables
- bounded stdout/stderr capture
- stdout/stderr redaction before public artifacts
- per-project timeout
- global timeout
- concurrency limit
- process group cleanup on timeout/cancel
- no automatic network access unless explicitly approved

If an implementation cannot enforce a control, it must record the missing control as `structured_unavailable` or `structured_blocker`.

## 5. Resource Limits

Default limits:

| Resource | Default |
| --- | --- |
| per-project timeout | 120 seconds |
| global timeout | 900 seconds |
| parallel projects | 1 |
| stdout/stderr public excerpt | 20 KB after redaction |
| temp output retention | repo artifact or explicit cleanup record |

These defaults may be overridden only by explicit CLI/MCP/HTTP input and must be recorded in `full_build_queue.json`.

## 6. Failure Categories

```text
unsafe_command
sandbox_limit
dependency_drift
timeout
permission_denied
network_blocked
output_redaction_failed
process_cleanup_failed
needs_review
```

Unsafe command or failed redaction is a high-risk blocker.

## 7. Acceptance Rules

- A project build row can be `accepted` only if executed commands are allowlisted, evidence refs exist, outputs are redacted and no high-risk runtime control failed.
- Deferred rows caused by `--max-code-projects` must be `needs_review` with `failure_category=deferred_by_limit`.
- Timeout rows must not be accepted.
- Skipped rows must not disappear from queue or diagnosis artifacts.

