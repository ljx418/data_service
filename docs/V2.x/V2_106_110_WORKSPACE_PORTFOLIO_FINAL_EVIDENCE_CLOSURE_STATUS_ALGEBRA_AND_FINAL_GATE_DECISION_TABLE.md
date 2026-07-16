# V2.106-V2.110 Status Algebra and Final Gate Decision Table

## 1. Purpose

This document closes the P0 status model gap. It separates execution status, acceptance status and scope status so implementation does not invent status rules.

## 2. Execution Status

Execution status describes what happened during a command or job:

```text
pending
queued
running
succeeded
failed
timeout
skipped
unavailable
cancelled
```

Rules:

- `succeeded` does not imply `accepted`.
- `skipped` and `timeout` never imply `accepted`.
- `unavailable` must include failure category and next action.

## 3. Acceptance Status

Acceptance status describes whether evidence is sufficient:

```text
accepted
needs_review
structured_unavailable
structured_blocker
out_of_scope
```

Rules:

- `accepted` requires evidence refs and PRD/spec-compatible behavior.
- `needs_review` means evidence or human decision is missing.
- `structured_unavailable` means external dependency, path, permission, browser or OCR is unavailable.
- `structured_blocker` means implementation, safety, contract or environment blocks continuation.
- `out_of_scope` requires explicit scope decision evidence and cannot be silently inferred by code.

## 4. Scope Status

Scope status is optional row metadata:

```text
in_scope
candidate_scope
out_of_scope_proposed
out_of_scope_approved
```

Only `out_of_scope_approved` may map to acceptance status `out_of_scope`.

## 5. High-risk Row Definition

A row is high-risk if any condition is true:

- It is required by PRD target experience.
- It affects `portfolio_final_status`.
- It can create false-green if missing, especially OCR/media, project build, source trace, UI evidence, public surface or release gate rows.
- It touches external project execution or user-provided files.
- It has no evidence refs but would otherwise be marked accepted.

## 6. Acceptance Priority

For final gate aggregation, use this worst-status order:

```text
structured_blocker
structured_unavailable
needs_review
out_of_scope
accepted
```

`out_of_scope` is lower risk than `needs_review` only when approved by explicit evidence. Otherwise it must remain `needs_review`.

## 7. Implementation Status Decision

`implementation_status` is the worst status over implementation capabilities:

| Condition | implementation_status |
| --- | --- |
| Any required implementation artifact missing | `needs_review` |
| Any contract or safety blocker | `structured_blocker` |
| Required external dependency unavailable but feature handles it structurally | `accepted` if unavailable is expected and tested |
| Focused tests, real E2E, PRD/spec review and false-green audit pass | `accepted` |

Implementation accepted does not imply portfolio final accepted.

## 8. Portfolio Final Status Decision

`portfolio_final_status` is the worst acceptance status over high-risk gate rows:

| High-risk rows | portfolio_final_status |
| --- | --- |
| Any `structured_blocker` | `structured_blocker` |
| Else any `structured_unavailable` | `structured_unavailable` |
| Else any `needs_review` | `needs_review` |
| Else all rows `accepted` or approved `out_of_scope` | `accepted` |

## 9. Mixed-run Rule

If final gate inputs have incompatible `run_id`, stale input hash, missing artifact ref or mismatched workspace fingerprint:

```text
execution_status=failed
acceptance_status=structured_blocker
failure_category=mixed_run_rejected
```

The final gate must not merge mixed-run artifacts into accepted evidence.

