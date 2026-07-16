# V2.116-V2.120 Status Algebra and Decision Approval Spec

## 1. 状态分层

必须分离四类状态。Persisted artifact 不再使用泛化 `status` 字段，统一使用以下字段：

```text
execution_status:
  pending | skipped | running | succeeded | failed | timeout | unavailable | blocked

artifact_status:
  accepted | needs_review | structured_unavailable | structured_blocker | failed

row_acceptance_status:
  accepted | needs_review | structured_unavailable | structured_blocker | failed

implementation_delivery_status:
  accepted | needs_review | structured_unavailable | structured_blocker | failed

run_acceptance_status:
  accepted | needs_review | structured_unavailable | structured_blocker | failed

portfolio_final_status:
  accepted | needs_review | structured_unavailable | structured_blocker | failed
```

`implementation_delivery_status=accepted` 可以表示实现机制正确保留了可信 blocker。  
`portfolio_final_status=accepted` 不允许包含未批准的 `needs_review`、`structured_unavailable`、`structured_blocker` 或 `failed`。

## 2. 状态优先级与不可豁免失败

状态优先级从高风险到低风险：

```text
failed
structured_blocker
structured_unavailable
needs_review
accepted
```

以下失败为 non-waivable，不允许通过 `approved_out_of_scope` 变成 final accepted：

```text
mixed_run
stale_or_tampered_input
invalid_approval_accepted
invalid_approval_rejected
path_escape_attempt_blocked
path_escape_guard_bypassed
secret_redaction_failure
child_process_cleanup_failed
artifact_hash_mismatch
schema_validation_failed
```

`approved_out_of_scope` 只可用于真实业务资料缺失、人工样本不足、外部依赖不可用等可审计例外；不得豁免安全、完整性、伪造审批或证据篡改失败。

## 3. Final Gate Decision Table

| 条件 | implementation_delivery_status | run_acceptance_status | portfolio_final_status |
| --- | --- | --- | --- |
| 安全机制自身失效或证据完整性失败 | failed | failed | failed |
| 违规尝试被正确阻断 | accepted | structured_blocker | structured_blocker |
| lineage/source hash stale 或未声明跨 run 引用 | accepted | structured_blocker | structured_blocker |
| 代码机制、测试和报告完整，但真实 OCR/UI/build 证据缺失 | accepted | needs_review 或 structured_unavailable | needs_review 或 structured_unavailable |
| 环境或依赖阻断被如实报告 | accepted | structured_blocker | structured_blocker |
| 所有 high-risk rows accepted | accepted | accepted | accepted |
| high-risk rows 未 accepted，但均有有效且非安全类 `approved_out_of_scope` | accepted | accepted | accepted |
| 任一 high-risk row 为 failed 且无有效例外 | accepted | failed | failed |
| 任一 high-risk row 为 needs_review 且无有效例外 | accepted | needs_review | needs_review |
| 任一 high-risk row 为 structured_unavailable 且无有效例外 | accepted | structured_unavailable | structured_unavailable |
| 任一 high-risk row 为 structured_blocker 且无有效例外 | accepted | structured_blocker | structured_blocker |

失败类别到 final 状态映射：

| failure_category | run_acceptance_status / portfolio_final_status |
| --- | --- |
| `invalid_approval_accepted`、`path_escape_guard_bypassed`、`secret_redaction_failure`、`child_process_cleanup_failed`、`artifact_hash_mismatch` | `failed` |
| `invalid_approval_rejected`、`path_escape_attempt_blocked`、`lineage_mismatch`、`stale_or_tampered_input`、`schema_validation_failed` | `structured_blocker` |
| provider/browser/external path unavailable | `structured_unavailable` |
| human anchor/decision missing | `needs_review` |

## 4. High-risk Row Definition

以下 row 自动视为 high-risk：

- OCR/media row with `ocr_required=true`。
- Source trace row whose source is in-scope。
- UI screenshot scenario required by PRD。
- Safe build command proposed for external project。
- Any final gate dependency row referenced by coverage matrix as required before accepted。

## 5. Run and Decision Lifecycle

不可变 run 与人工决策必须通过独立 lifecycle 闭合：

```text
Proposal Run
  生成 candidate anchors、proposed commands、proposal digests。

Decision Set
  由人类或可信外部 policy 对 proposal digest 作出决策。
  append-only，存放在 decisions/{decision_set_id}.json。
  不写入已完成的 runs/{run_id}/。

Execution Run
  引用 proposal_run_id + decision_set_id。
  校验 decision scope、digest、expiry、revocation 和输入 hash。

Final Gate Run
  引用 execution_run_id、input_manifest_hash、decision_set_id 和 source_run_refs。
```

目录约定：

```text
workspace/{workspace_id}/portfolio_real_evidence_acceptance/
  decisions/{decision_set_id}.json
  runs/{run_id}/...
```

`decisions/{decision_set_id}.json` 是 append-only authority。Run 内不得再保存另一份权威 registry；run 内只保存不可变评估快照：

```text
runs/{run_id}/evidence_decision_snapshot.json
```

该 snapshot 记录 decision set hash、有效决策、撤销/过期决策、scope 校验和 approval binding 校验。

Anchor 相关决策分为两类：

- `anchor_confirmation`：在 OCR 前确认 anchor 文本、source ref、input hash 和 anchor_text_hash，不要求 OCR output hash。
- `ocr_output_confirmation`：在 OCR 后确认 output hash、anchor hit 和 row evidence。

## 6. Decision Set and Snapshot Schema

`decisions/{decision_set_id}.json` 必须包含：

```json
{
  "schema_version": "v2.116-120",
  "workspace_id": "string",
  "decision_set_id": "string",
  "proposal_run_id": "string",
  "parent_decision_set_id": "string|null",
  "generated_at": "ISO-8601 string",
  "decisions": [
    {
      "decision_id": "string",
      "decision_type": "build_approval|anchor_confirmation|ocr_output_confirmation|approved_out_of_scope|revoke",
      "target_type": "ocr_row|source_trace_row|ui_scenario|build_command|final_gate_row",
      "target_id": "string",
      "decision_status": "approved|rejected|revoked|expired",
      "revokes_decision_id": "string|null",
      "supersedes_decision_id": "string|null",
      "approver": {
        "kind": "human|policy",
        "id": "string",
        "display_name": "string"
      },
      "created_at": "ISO-8601 string",
      "expires_at": "ISO-8601 string|null",
      "revoked_at": "ISO-8601 string|null",
      "risk_level": "low|medium|high|critical",
      "scope": {
        "workspace_id": "string",
        "proposal_run_id": "string",
        "execution_run_id": "string|null",
        "artifact_ref": "string",
        "row_id": "string"
      },
      "input_hash": "sha256",
      "output_hash": "sha256|null",
      "command_digest": "sha256|null",
      "scope_digest": "sha256",
      "reason": "string",
      "evidence_refs": ["string"]
    }
  ],
  "artifact_refs": ["workspace-relative path"],
  "evidence_refs": ["string"],
  "unresolved": []
}
```

`runs/{run_id}/evidence_decision_snapshot.json` 必须包含：

```json
{
  "schema_version": "v2.116-120",
  "workspace_id": "string",
  "run_id": "string",
  "artifact_id": "evidence_decision_snapshot",
  "artifact_type": "evidence_decision_snapshot",
  "artifact_status": "accepted|needs_review|structured_blocker|failed",
  "data": {
    "decision_set_ref": "decisions/{decision_set_id}.json",
    "decision_set_hash": "sha256",
    "evaluated_at": "ISO-8601 string",
    "effective_decision_ids": ["string"],
    "revoked_or_expired_decision_ids": ["string"],
    "scope_validation": "matched|mismatch",
    "approval_binding_validation": "matched|mismatch"
  }
}
```

## 7. Approval Validity Rules

- 程序不得自行生成 `approved` 决策。
- `approved_out_of_scope` 必须有 approver、reason、risk_level、scope、input_hash。
- Build approval 必须绑定 normalized command digest、sandbox policy digest 和 project input hash。
- `anchor_confirmation` 必须绑定 target row、input hash 和 anchor_text_hash。
- `ocr_output_confirmation` 必须绑定 target row、input hash、output hash 和 anchor_hit evidence。
- `revoked` 或 `expired` 决策不得参与 final accepted。
- `revoke` 必须提供 `revokes_decision_id`。
- 新决策替代旧决策时必须提供 `supersedes_decision_id`。
- 缺决策时只能是 `needs_review`。
