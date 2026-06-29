# V2.71-V2.75 Detailed PRD：Agent 长期记忆、CI 治理、维护者控制台与发布恢复

## 1. 文档状态

Status: Draft v0.1.

Scope: product requirement and acceptance baseline.

Boundary: 本文用于指导 V2.71-V2.75 后续实现和验收，不证明任何 V2.71-V2.75 功能已经实现，也不是 implementation acceptance 证据。

本阶段继续基于 V2.0-V2.70 已验收能力推进，但不得声明完整恢复复杂项目设计意图、full call graph、runtime topology、data/control flow 或 type inference。

## 2. 目标用户

### 2.1 维护者

维护者需要在一个统一入口中判断：

- 当前项目是否可继续开发；
- 哪些外部项目真实可用；
- CI、warning、public surface 是否稳定；
- Agent 读取的长期记忆是否有证据支撑；
- 当前是否可以发布、恢复或需要人工审查。

### 2.2 Coding Agent

Agent 需要在任务开始前读取：

- 项目长期记忆；
- 证据索引；
- 当前验收状态；
- stop conditions；
- 建议测试；
- 不可越界的状态规则。

### 2.3 审计者

审计者需要验证：

- accepted 是否有真实证据；
- unavailable、blocker、needs_review 是否被保留；
- 控制台是否隐藏风险；
- 发布恢复包是否泄露本地敏感信息；
- public surface 是否进入 guard。

## 3. P0 功能需求

### 3.1 V2.71 External Project Binding Closure

目标：维护者能判断每个目标项目是否真实可用。

P0 要求：

- 系统必须读取 V2.63 external E2E 与 V2.67 path binding artifact。
- `data_service` 可使用当前仓库真实路径作为 accepted 候选。
- `codexPat`、`HarnessOS`、`Navia` 没有真实可读路径时必须标记为 `structured_unavailable` 或 `structured_blocker`。
- 不可用项目不能计入 accepted。
- 每个项目必须有 `status`、`reason`、`evidence_refs` 或 `unresolved`、`next_action`。

用户验收：

- 维护者能看到哪些项目能用、哪些不能用、为什么不能用。
- 报告不能把 unavailable 写成 accepted。

### 3.2 V2.72 CI and Warning Governance

目标：维护者能判断测试和 warning 风险是否可控。

P0 要求：

- 系统必须输出 CI matrix、warning budget、failure diagnosis、CI readiness report。
- warning 超预算时不能 accepted。
- 失败分类只能使用：
  - `dependency_drift`
  - `sandbox_limit`
  - `artifact_missing`
  - `public_surface_drift`
  - `real_regression`
  - `needs_review`
- 不允许通过删除测试覆盖制造 false green。

用户验收：

- 维护者能看到慢测试、warning 数量、预算、失败归因和下一步动作。
- CI readiness 不能只引用文档声明，必须绑定真实测试或结构化说明。

### 3.3 V2.73 Agent Long-term Memory Productization

目标：Agent 能读取项目情报长期记忆，但不获得无证据事实。

P0 要求：

- 系统必须输出：
  - `memory_index.json`
  - `evidence_index.json`
  - `acceptance_state.json`
  - `task_briefing.json`
  - `retention_policy.md`
- 每个 memory item 必须有 `source_artifact_ref`。
- 每条 recommendation 必须有 `evidence_refs` 或 `needs_review`。
- 不声明通用聊天长期记忆，只声明项目情报长期记忆。

用户验收：

- Agent 能读取项目状态、证据边界、建议阅读路径、stop conditions 和建议测试。
- 缺证据内容不会显示为事实。

### 3.4 V2.74 Interactive Maintainer Console

目标：维护者可以通过首页或控制台快速判断项目状态。

P0 要求：

- 系统必须输出：
  - `console_model.json`
  - `navigation_model.json`
  - `status_panels.json`
  - `maintainer_console.html`
- 每个 panel 必须包含 `status`、`artifact_ref`、`evidence_ref` 或 `unresolved`。
- 控制台必须显示 `needs_review`、`structured_unavailable`、`structured_blocker`。
- HTML 只能展示 artifact 中已有事实，不硬编码 accepted 结论。

用户验收：

- 维护者一页看到外部项目状态、CI 风险、Agent memory 状态、发布恢复状态和出门条件。
- 控制台不能隐藏 non-accepted 状态。

### 3.5 V2.75 Release and Restore Packaging

目标：维护者可以按 runbook 恢复本地能力并执行 smoke test。

P0 要求：

- 系统必须输出：
  - `release_manifest.json`
  - `mcp_config_template.json`
  - `smoke_commands.md`
  - `restore_runbook.md`
  - `release_readiness_report.md`
- smoke commands 必须覆盖 MCP、CLI、HTTP、focused tests。
- public artifact 不得包含本地绝对路径、secret、token、raw traceback、private venv path。
- release readiness 不能把外部 unavailable 写成 accepted。

用户验收：

- 维护者能按文档恢复环境、配置 MCP、运行 smoke test。
- 发布包能说明哪些能力可用、哪些仍需人工审查。

## 4. P1 功能需求

- 控制台支持按阶段、风险等级、状态过滤。
- Agent memory 支持按任务类型生成读取路径。
- CI governance 支持历史 warning 趋势。
- Release restore 支持区分本地开发、CI、交付审查三种运行上下文。

P1 不应阻断 P0 出门验收，除非 P1 实现引入 public surface 回归、false-green 风险或 artifact 泄露风险。

## 5. 明确非目标

- 不做云端同步。
- 不做通用聊天记忆。
- 不做完整项目语义理解承诺。
- 不自动删除本地文件。
- 不修改 protected legacy 文件，除非用户明确批准。
- 不把外部项目 mock evidence 作为 accepted。
- 不把 documentation claim 当作 code fact。

## 6. 总体验收门槛

本阶段完成必须满足：

- V2.71-V2.75 focused tests passed。
- V2.63-V2.70 regression passed。
- `test_public_surface_guard.py` passed。
- `compileall` passed。
- `git diff --check` passed。
- protected legacy diff empty。
- 真实 `data_service` E2E passed。
- 外部项目无真实路径时保持 `structured_unavailable` 或 `structured_blocker`。
- PRD/spec review completed。
- false-green audit completed。
- final acceptance audit report created。

## 7. 失败处理

必须打回开发计划阶段的情况：

- accepted 无真实 evidence；
- unavailable 被写成 accepted；
- warning 超预算仍 accepted；
- 控制台隐藏 non-accepted；
- memory item 无 source artifact；
- public artifact 泄露本地敏感路径、secret、token 或 raw traceback；
- 新 public surface 未进入 guard；
- protected legacy 文件被修改但无用户批准。

可以继续推进但必须结构化记录的情况：

- 外部项目真实路径缺失；
- 外部项目依赖不可安装；
- 本地沙箱限制导致 E2E 无法完整执行；
- CI 环境缺少必须依赖；
- artifact 缺失但可由 build step 重新生成。

## 8. 开放风险

- `codexPat`、`HarnessOS`、`Navia` 是否能 accepted 取决于真实路径和依赖环境，文档无法消除该风险。
- warning 治理能否降到目标预算取决于后续真实测试结果。
- 交互式控制台的体验质量需要后续 UI/E2E 截图验收确认。
- Agent memory 的质量取决于上游 persisted artifacts 的完整性；缺失事实必须保留为 `needs_review`。

## 9. PRD 审计结论

本 Detailed PRD 补齐阶段级 PRD 中缺少的用户故事、P0/P1、用户验收、失败处理和开放风险。它可以作为后续自动化开发的产品规格入口，但仍不构成实现完成证据。

