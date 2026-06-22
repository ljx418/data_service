# V2.46-V2.52 Milestones and Exit Gates

## M0：Pre-implementation Gate

出门条件：

- V2.39-V2.45 closure audit 存在且无 fatal/major。
- 当前仓库 clean，或所有 changed files 已列入 Phase 123 pre-implementation audit。
- 真实项目路径确认或 structured unavailable。
- 本阶段 PRD、目标架构、开发验收计划、E2E matrix、drawio 已落盘。
- Phase 123 development plan、acceptance plan、pre-implementation audit 已落盘。
- MCP registry 读取方式、tool catalog 比对规则、Codex CLI guide 输出路径已冻结。
- public redaction、artifact inspection、HTTP/MCP/CLI parity 测试计划已冻结。
- 无 open fatal / major finding。

## M1：V2.46 MCP Productization

出门条件：

- Codex CLI MCP 使用指南可读。
- Agent 操作协议覆盖常用工具链。
- 工具 catalog 与 registry 一致。
- 未配置 MCP 有结构化诊断。

## M2：V2.47 Profile Onboarding

出门条件：

- data_service、HarnessOS、Navia、codexPat profile 或 unavailable 记录存在。
- taxonomy、authority、entrypoint、workflow patterns 可读。
- no-hardcode audit passed。

## M3：V2.48 Human Portal

出门条件：

- HTML 项目理解首页生成。
- 图表原位渲染。
- target/current/diff/needs_review 可见。
- 不引入 artifact 外事实。
- 如果新增 direct UI route，route contract、error shape、artifact_refs、parity 或 UI-only read exception 已记录。

## M4：V2.49 Task Navigation and Impact

出门条件：

- task-aware reading order 可用。
- impact candidates 有 evidence 或 needs_review。
- suggested tests 可追溯。
- 不声称 runtime call。

## M5：V2.50 Governance Workflow

出门条件：

- feedback/rule/review/plan 可读写。
- approve/revoke 行为通过。
- read-time overlay 不改写原始 artifact。

## M6：V2.51 Agent Context Playbooks

出门条件：

- 四类 Agent playbook 生成。
- token budget 和 omitted_items 可见。
- 小预算下不保留无证据建议。

## M7：V2.52 Closure

出门条件：

- 四项目持续回归矩阵完成。
- HTTP/MCP/CLI parity 通过。
- direct UI route parity 或 UI-only read exception 通过。
- public redaction 通过。
- coverage matrix accepted 行有真实证据。
- 无 open fatal / major。

## Global Claim Boundary

- 本文档的 `planned`、`ready`、`baseline ready` 只表示规划和实施准备完成，不表示功能实现完成。
- 任何 `accepted` implementation claim 必须有真实项目 E2E、artifact path、test command、parity/redaction/no-hardcode 结果和 acceptance audit ref。
- structured unavailable、structured blocker、provider unavailable、needs_review 不得被写成 accepted。
