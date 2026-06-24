# V2.54-V2.58 PRD：Human / Agent Deepening and Regression Expansion

## 1. 阶段定位

V2.54-V2.58 承接已验收的 V2.46-V2.53 Agent Productization 与 Acceptance Infrastructure。目标是在不扩大静态分析承诺的前提下，把项目理解能力继续做深：

- 人类维护者能更快读懂项目状态、风险和下一步动作。
- Codex / Copilot 类 Agent 能按任务稳定消费 bounded context、impact candidates 和 suggested tests。
- 架构审计者能持续跟踪 doc-code claim、review finding 和 governance overlay。
- 多项目回归从 closure summary 进一步走向 artifact diff、趋势和迁移恢复可诊断。

本阶段不是 full design-intent recovery、full call graph、runtime topology、data/control flow 或 type inference 阶段。

## 2. 用户问题

当前 V2.46-V2.53 已解决产品化入口和验收可复现问题，但仍存在：

- Human Portal 能打开，但项目故事、风险排序、阅读路径和图表解释还不够面向维护者。
- Agent Playbook 可用，但针对具体修改任务的执行链路仍偏 artifact 组合，缺少更明确的 stop condition 和 failure handling。
- Doc-Code Governance 已有 feedback/rule/overlay，但 evidence review、历史决策和漂移趋势还不够闭环。
- 四项目持续验收已有 accepted matrix，但缺少跨版本 artifact diff、趋势观察和迁移失败诊断。
- 新机器恢复流程已记录，但依赖、沙箱限制、验收命令、常见失败解释还没有形成完整 onboarding UX。

## 3. 目标体验

### 3.1 人类维护者

打开项目理解入口后，可以看到：

- 项目定位、当前架构摘要、主要入口和边界。
- target/current/diff 变化点和 high-risk / needs_review 优先级。
- 推荐阅读路径、下一步审计动作、当前验收状态。
- 图表直接表达项目事实，不需要阅读 Mermaid 源码。

### 3.2 Coding Agent

在修改代码前，Agent 可以获得：

- task-aware reading order；
- bounded impact candidates；
- suggested tests；
- required constraints / stop conditions；
- evidence-backed recommendations 或 needs_review。

Agent 不应把 relationship chain 当成 full call graph，也不应把 impact candidate 写成确定 runtime call。

### 3.3 架构审计者

审计者可以：

- 查看 doc claim、code fact、supported/weak/unsupported/contradicted 状态；
- 记录 review decision；
- 通过 read-time overlay 观察 approved rule 的影响；
- 查看跨版本或跨项目的 drift / regression trend。

### 3.4 项目维护与迁移

维护者可以按单一命令恢复验收环境、运行验收、定位失败属于依赖漂移、沙箱限制、artifact 缺失、public surface 变化还是真实实现回归。

## 4. In Scope

| 阶段 | 名称 | 目标 |
| --- | --- | --- |
| V2.54 | Human Portal Deepening | 提升项目理解首页、图表质量、风险排序、阅读路径 |
| V2.55 | Agent Task Workflow Hardening | 强化 task navigation、impact candidates、suggested tests、playbook stop condition |
| V2.56 | Doc-Code Governance Evidence Loop | 加强 doc-code evidence review、decision history、read-time overlay 可解释性 |
| V2.57 | Multi-project Regression Expansion | 扩展四项目 artifact diff、趋势、回归诊断 |
| V2.58 | Developer Onboarding / Restore UX | 完整化恢复、依赖、验收命令、失败诊断入口 |

## 5. Out of Scope

- 不自动修改被分析项目代码。
- 不自动重写项目文档。
- 不声称完整恢复复杂项目设计意图。
- 不声称 full call graph、runtime topology、data/control flow 或 type inference。
- 不把 documentation claim 当作 code fact。
- 不把 needs_review、structured_unavailable、structured_blocker 写成 accepted。
- 不修改 legacy 大文件 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`，除非有明确批准。

## 6. 完成定义

V2.54-V2.58 完成必须满足：

1. 每个阶段开始前有 development plan、acceptance plan、pre-implementation audit。
2. 每个阶段结束后有 focused tests、真实项目 E2E、PRD/spec review、false-green audit、acceptance audit。
3. Human Portal 的新增信息只来自 persisted artifacts 或有明确 evidence_refs。
4. Agent task workflow 的每条建议有 evidence_refs 或 needs_review，并带 stop condition。
5. Doc-Code Governance 不改写原始 docs 或上游 code facts，只产生治理 artifact 或 read-time overlay。
6. Multi-project regression 不把 unavailable 项目写成 accepted。
7. Restore UX 能让新环境安装 test deps 并运行 canonical acceptance runner。
8. public payload 不泄露 absolute path、secret、token、raw traceback。
