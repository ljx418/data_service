# V2.54-V2.58 Target Architecture：Human / Agent Deepening and Regression Expansion

## 1. 架构目标

V2.54-V2.58 在 V2.46-V2.53 之上增加五个加深层：

```text
V2.46-V2.53 accepted baseline
  -> Human Portal Deepening
  -> Agent Task Workflow Hardening
  -> Doc-Code Governance Evidence Loop
  -> Multi-project Regression Expansion
  -> Developer Onboarding / Restore UX
```

目标是提高现有 artifacts 的可读性、可执行性、可回归性和可恢复性，不新增超出 evidence-first 边界的推断能力。

## 2. 当前架构

当前已存在：

- `agent_productization/` artifacts：mcp usage、profile onboarding、portal、task navigation、governance、playbooks、closure。
- HTTP/MCP/CLI 三出口。
- V2.53 canonical acceptance runner。
- focused tests 和 public surface guard。

当前边界：

- relationship chain 是候选关系，不是 full call graph。
- impact candidate 是启发式影响面，不是 runtime call。
- document claim 不等于 code fact。
- accepted 必须有 artifact path、test result、real repo result 或明确 structured rationale。

## 3. 目标组件

### 3.1 Human Portal Deepening

职责：

- 从 persisted artifacts 汇总项目 story、risk priority、reading path、acceptance state。
- 生成更清晰的图表和维护者下一步动作。
- 为每个新增展示项保留 evidence_refs。

边界：

- 不从 HTML 模板创造 artifact 外事实。
- UI-only route 只能读取 persisted portal artifact 或等价 read contract。

### 3.2 Agent Task Workflow Hardening

职责：

- 将 task navigation、playbook、suggested tests、constraints、stop conditions 组合为 task workflow。
- 输出 bounded context，包含 omitted_items 和 token budget rationale。
- 给 Agent 提供可复制的执行序列。

边界：

- 不自动应用 patch。
- 不把 low confidence 建议写成 accepted recommendation。

### 3.3 Doc-Code Governance Evidence Loop

职责：

- 将 doc-code findings、review decisions、rules、overlay 连接为可追踪 evidence loop。
- 展示 decision history 和 rule effect。
- 保持原始 docs / code facts 不变。

边界：

- approved rule 只作为 read-time overlay。
- revoked rule 不得继续影响 read output。

### 3.4 Multi-project Regression Expansion

职责：

- 对 data_service、HarnessOS、Navia、codexPat 生成 expanded regression matrix。
- 记录 artifact availability、diff summary、trend、failure diagnosis。
- 区分 accepted、accepted_with_blockers、structured_unavailable、needs_review。

边界：

- 不把 unavailable 项目计入 accepted。
- 不把 mock-only evidence 当作 real repo E2E。

### 3.5 Developer Onboarding / Restore UX

职责：

- 固化依赖安装、验收命令、沙箱限制和失败诊断。
- 生成 restore checklist 和 acceptance troubleshooting。
- 保持 V2.53 runner 为 canonical check，允许后续扩展。

边界：

- 不依赖本机私有路径。
- 不要求用户手动猜测 test dependency 版本。

## 4. Artifact Layout

新阶段 artifacts 应位于：

```text
workspace/assets/codebase/{codebase_id}/human_agent_deepening/
  human_portal_deepening/
  agent_task_workflow/
  doc_code_evidence_loop/
  regression_expansion/
  restore_ux/
```

如果复用 `agent_productization/` 既有 artifacts，必须通过 read-only reference 或生成新版本命名空间，不得静默覆盖 V2.46-V2.52 evidence。

## 5. Public Contract

所有 read output 继续使用 V2 envelope：

```json
{
  "ok": true,
  "schema_version": "v2.54-58",
  "workspace_id": "...",
  "codebase_id": "...",
  "data": {},
  "artifact_refs": [],
  "warnings": [],
  "unresolved": [],
  "next_actions": []
}
```

错误输出必须结构化，不泄露 absolute path、secret、token、raw traceback。

## 6. 架构门禁

- 新增能力必须有 phase-specific PRD/spec review。
- accepted 行必须绑定 artifact evidence、focused test、真实项目结果或 structured rationale。
- 文档 claim、code fact、review decision、overlay rule 必须分层。
- 任何新增 direct UI route 必须有 parity evidence 或 UI-only exception。
- 新阶段不得修改 legacy 大文件，除非明确批准。
