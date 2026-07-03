# V2.96-V2.100 Phase Readiness and Schema Contracts

## 1. Unified Response Contract

所有 build/read 返回结构必须包含：

```json
{
  "ok": true,
  "schema_version": "v2.96-100",
  "workspace_id": "string",
  "codebase_id": "string",
  "phase": "V2.96|V2.97|V2.98|V2.99|V2.100",
  "status": "accepted|needs_review|structured_unavailable|structured_blocker|failed",
  "artifact_refs": ["repo-relative path"],
  "evidence_refs": ["repo-relative path or command id"],
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

- `accepted`：真实证据完整，可复跑，可审计。
- `needs_review`：缺人工判断、真实资料或高风险确认。
- `structured_unavailable`：外部路径、资料或环境不可用，不是 accepted。
- `structured_blocker`：依赖、实现或环境阻断，不是 accepted。
- `failed`：命令或流程失败，不能被 release gate 放行。

## 3. Schema Requirements

### V2.96 CLI Gap

必须记录：

- default shell command。
- parser inventory command。
- MCP tool inventory。
- HTTP route inventory。
- gap status。

### V2.97 Route A Evidence

必须记录：

- material refs。
- source type。
- redaction policy。
- evidence capture refs。
- manual confirmation state。

### V2.98 Quality Workbench

必须记录：

- recommendation id。
- risk level。
- evidence refs。
- recommended decision。
- human decision state。

### V2.99 External Path Registry

必须记录：

- project id。
- path status。
- smoke/E2E status。
- command refs。
- unavailable reason。

### V2.100 Release Evidence Gate

必须记录：

- upstream phase status。
- dependency hygiene state。
- restore smoke state。
- human approval state。
- final status。
- false-green audit result。

## 4. Public Output Redaction

public artifacts 禁止包含本地绝对路径、secret、token、raw traceback、私有 virtualenv 路径或未证实 accepted claim。
