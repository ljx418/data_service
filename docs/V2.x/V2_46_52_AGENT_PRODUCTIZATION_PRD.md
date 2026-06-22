# V2.46-V2.52 PRD：面向 Agent 的项目理解产品化与持续架构看护

## 1. 阶段定位

V2.46-V2.52 承接已验收的 V2.39-V2.45 大项目 scale、语义抽取、关系链、token budget、profile/taxonomy 和持续回归能力，目标是把这些能力进一步产品化为人类和 Codex/Copilot 类 Agent 可直接使用的本地项目理解服务。

本阶段重点不是继续扩大静态分析承诺，而是把已有 evidence-first 项目智能能力做成稳定、可读、可配置、可回归、可被 MCP 调用的开发辅助系统。

## 2. 用户问题

当前项目已经能生成大量 artifacts，但用户和 Agent 仍会遇到这些问题：

- 不知道在另一个 Codex CLI 窗口里如何正确调用本服务。
- 大项目报告仍偏工程化，缺少面向人类的项目理解首页。
- Profile/taxonomy 能力存在，但还没有成为项目接入的标准流程。
- relationship chain、文档代码核查、context pack 的组合使用路径不够清晰。
- 多项目持续回归集有基础，但缺少面向新项目接入和长期看护的验收标准。

## 3. 目标体验

### 3.1 人类维护者

维护者导入一个项目后，可以打开一个可读的项目理解首页，快速看到：

- 项目定位和主要技术栈。
- 公开入口、服务边界、文档权威入口。
- target/current/diff 架构摘要。
- 高风险、弱证据、needs_review、structured blocker。
- 推荐阅读路径和下一步审计动作。

### 3.2 Codex CLI / Copilot 类 Agent

Agent 在修改代码前，可以通过 MCP 获取：

- task-aware reading order。
- capability-to-implementation chain。
- module reading pack。
- architecture constraints。
- token budget ledger。
- 可引用 evidence 的建议。

Agent 不需要反复扫描整个仓库，从而降低 token 消耗和重复阅读成本。

### 3.3 架构审计者

审计者可以使用项目 profile 和文档代码核查结果，观察代码是否偏离原始架构设计：

- supported 必须有 document evidence 和 code evidence。
- weakly_supported、unsupported、contradicted 必须显式展示。
- drawio/Markdown claim 不能直接冒充 code fact。
- 项目专用术语必须进入 profile，不得硬编码进通用 extractor。

## 4. In Scope

1. MCP 使用产品化和 Codex CLI 接入指南。
2. 项目 Profile / Taxonomy 接入流程增强。
3. 人类可读架构报告和项目理解首页增强。
4. 任务导航、调用链路和变更影响辅助增强。
5. 文档代码架构核查的操作化流程。
6. 真实项目持续回归集扩展到 data_service、HarnessOS、Navia、codexPat。
7. HTML/SVG/Mermaid 图表渲染质量增强。
8. Agent Context Pack 使用手册和验收样例。

## 5. Out of Scope

- 不声称完整恢复人类设计意图。
- 不声称 full call graph、data flow、control flow、runtime trace、type inference。
- 不自动修改目标项目代码。
- 不自动重写目标项目文档。
- 不把 HarnessOS、Navia 或 codexPat 的专用规则写进通用 extractor。
- 不把没有双边 evidence 的结论标记为 accepted。

## 6. 阶段拆分

| 阶段 | 名称 | 目标 |
| --- | --- | --- |
| V2.46 / Phase 123 | MCP 使用产品化 | Codex CLI 接入指南、Agent 操作手册、工具调用路径 |
| V2.47 / Phase 124 | Project Profile Onboarding | 项目 profile 创建、taxonomy、authority rules、no-hardcode gate |
| V2.48 / Phase 125 | Human Architecture Portal | 项目理解首页、可读图表、target/current/diff/risks |
| V2.49 / Phase 126 | Task Navigation and Impact v2 | task-aware reading、relationship chain 消费、影响面和测试建议 |
| V2.50 / Phase 127 | Doc-Code Governance Workflow | 文档代码核查工作流、evidence review、governance feedback |
| V2.51 / Phase 128 | Agent Context Playbooks | 面向不同 Agent 角色的 context pack playbook 和 token 验收 |
| V2.52 / Phase 129 | Multi-project Continuous Acceptance | data_service、HarnessOS、Navia、codexPat 持续回归和 closure |

## 7. 完成定义

V2.46-V2.52 完成必须满足：

1. 本地 MCP 接入文档能让另一个 Codex CLI 窗口完成项目导入、摘要、context pack 和 relationship chain 调用。
2. 至少 data_service、HarnessOS、Navia、codexPat 四个项目有 profile 或 structured unavailable 记录。
3. 人类可读 HTML 报告原位渲染关键图表，不展示 Mermaid 源码，不引入 artifact 外事实。
4. Agent context pack 每条建议必须有 evidence_refs 或 needs_review。
5. 文档代码核查报告区分 document claim、code fact、supported、weak、unsupported、contradicted。
6. no-hardcode audit 通过。
7. HTTP/MCP/CLI 读接口保持 schema、artifact refs、warnings、unresolved、error code parity。
8. 无 open fatal 或 major finding。

