# V2.46-V2.52 Development and Acceptance Plan

## 1. 共享开发规则

- 每个阶段开始前必须产出 phase-specific development plan、acceptance plan、pre-implementation audit。
- 每个阶段完成后必须产出 acceptance audit report。
- 使用真实项目：data_service、HarnessOS、Navia、codexPat。
- 真实项目不可用时只能 structured unavailable，不能 accepted。
- 所有 public output 必须 repo-relative path，不能泄露 secret、token、raw traceback。
- 所有 accepted recommendation 必须有 evidence_refs 或 needs_review。

### 1.1 外部审计建议跟进门槛

本阶段文档可以声明 `planning / implementation baseline ready`，但不能声明功能已实现。任何 `accepted` 实现结论必须等对应 phase 完成真实项目 E2E、artifact inspection、HTTP/MCP/CLI parity、redaction/no-hardcode audit 和 acceptance audit 后才能成立。

Phase 123 进入代码实现前必须关闭以下 pre-implementation gates：

- V2.39-V2.45 closure audit 存在且无 open fatal/major。
- data_service、HarnessOS、Navia、codexPat 路径可用；不可用只能记录 structured unavailable。
- 当前 worktree clean，或所有 changed files 已列入 pre-implementation audit。
- MCP registry 读取方式、Codex CLI guide 产物路径、tool catalog 比对口径已冻结。
- public redaction、artifact inspection、HTTP/MCP/CLI parity 测试计划已冻结。
- Phase 123 无 open fatal/major finding。

如果 Phase 125 或后续阶段新增 direct UI route，必须补充 route path、read contract、artifact_refs、error shape，并在 HTTP/MCP/CLI parity 中纳入该 route；如果该 route 明确是 UI-only read view，必须记录例外理由和等价 artifact read contract。

## 2. Phase 123 / V2.46：MCP 使用产品化

开发：

- 生成 Codex CLI MCP 接入指南。
- 生成 Agent 操作协议：import、snapshot、overview、scale、profile、relationship、context pack。
- 增加 MCP tool catalog 的用户说明和 recommended workflow。

验收：

- 人类能按文档在另一个 Codex CLI 窗口配置 MCP。
- Agent playbook 能说明每一步调用目的、输入、输出和失败处理。
- MCP 工具列表与实际 registry 一致。
- 未配置 MCP 时返回结构化诊断。

## 3. Phase 124 / V2.47：Project Profile Onboarding

开发：

- 增加 profile draft builder。
- 增加 taxonomy suggestion、authority rule suggestion、path pattern suggestion。
- 增加 no-hardcode audit。

验收：

- data_service、HarnessOS、Navia、codexPat 生成 profile 或 structured unavailable。
- Navia/HarnessOS 特殊术语只出现在 profile artifact。
- 通用 extractor 扫描不得出现项目专用 hardcode。

## 4. Phase 125 / V2.48：Human Architecture Portal

开发：

- 生成项目理解首页 JSON。
- 渲染 HTML：项目定位、入口、模块、关系链、target/current/diff、risks、reading path。
- 原位渲染 Mermaid/SVG。

验收：

- HTML 不展示 Mermaid 源码。
- 每个图节点都可回溯到 persisted artifact。
- HTML/Mermaid escaping 通过。
- data_service 和 HarnessOS 至少各生成一份可读报告。
- 如新增 direct UI route，必须完成 route contract、error envelope、artifact_refs 和 parity/例外说明。

## 5. Phase 126 / V2.49：Task Navigation and Impact v2

开发：

- 消费 relationship chain、module reading pack、test selection、doc-code finding。
- 输出 task-aware reading order、impact candidates、suggested tests。

验收：

- 给定真实任务，输出不超过 token budget 的 reading order。
- 每个 suggested test 有 evidence 或 needs_review。
- impact candidate 不得表述为确定 runtime call。

## 6. Phase 127 / V2.50：Doc-Code Governance Workflow

开发：

- 将 doc-code verification finding 接入 governance feedback。
- 支持 review status、approved rule、revoke、correction plan。
- read-time overlay 应用规则。

验收：

- approve rule 后 read output 出现 applied_rules。
- revoke rule 后 read output 不再应用。
- 原始 docs 和上游 artifacts hash 不变。

## 7. Phase 128 / V2.51：Agent Context Playbooks

开发：

- 定义 maintainer、coding_agent、documentation_agent、architecture_reviewer playbooks。
- 每个 playbook 包含 MCP 调用顺序、推荐问题、输出解释和停止条件。
- Context Pack 输出 token ledger、omitted_items、cache refs。

验收：

- 小 token budget 下不保留无 evidence 建议。
- playbook 输出能被 Agent 直接复制使用。
- 每条开发建议有 evidence_refs 或 needs_review。

## 8. Phase 129 / V2.52：Multi-project Continuous Acceptance

开发：

- 建立四项目持续回归矩阵。
- 记录 accepted、structured blocker、provider unavailable、needs_review。
- 汇总 closure audit。

验收：

- data_service、HarnessOS、Navia、codexPat 均有结果。
- no-hardcode audit 通过。
- HTTP/MCP/CLI parity 通过。
- direct UI route parity 或 UI-only read exception 完成审计。
- 无 open fatal / major。

## 9. 停止条件

发现以下情况必须停止：

- accepted 结论缺 evidence。
- profile 规则被写入通用 extractor。
- HTML 报告引入 artifact 外事实。
- Mermaid/HTML 未 escape。
- Agent playbook 建议没有 evidence 或 needs_review。
- structured blocker 被写成 accepted。
- 真实项目 E2E 全部被 mock 替代。
