# V2.71-V2.75 PRD：Agent 长期记忆、CI 治理、交互控制台与发布恢复

## 1. 阶段定位

V2.71-V2.75 承接已完成本地验收的 V2.0-V2.70。上一阶段已经证明当前 `data_service` 可以作为真实项目执行本地 E2E，并产出 Portal、Dashboard、外部项目路径绑定、交付清单和 public surface baseline。仍需继续推进的事实是：

- `codexPat`、`HarnessOS`、`Navia` 未提供真实可读路径，仍是 `structured_unavailable`，不能写成 accepted。
- 测试 warnings 较高，慢测试和 CI 分组仍需要可审计治理。
- 当前 Agent 能读取项目情报和上下文包，但尚未形成面向长期记忆的稳定产品边界、读取契约和保留策略。
- Portal/Dashboard 已是持久化 artifact，但维护者仍缺少交互式首页/控制台的统一体验规划。
- 本地恢复、MCP 配置、发布包和 smoke test 需要形成更明确的交付体验。

本阶段目标不是扩大代码理解承诺，而是把已形成的项目情报能力产品化为可恢复、可审计、可回归、可被 Agent 长期读取的本地能力。

| 阶段 | 名称 | 目标 |
| --- | --- | --- |
| V2.71 | External Project Binding Closure | 对外部项目真实路径、依赖、E2E 状态和不可用原因做闭环 |
| V2.72 | CI and Warning Governance | 拆分慢测试、定义 warning budget、输出 CI readiness 和失败归因 |
| V2.73 | Agent Long-term Memory Productization | 将项目情报、证据索引、验收状态包装为 Agent 可长期读取的记忆 surface |
| V2.74 | Interactive Maintainer Console | 规划交互式维护者首页、状态面板、证据跳转和人工决策入口 |
| V2.75 | Release and Restore Packaging | 规划本地发布包、MCP 配置模板、恢复脚本和 smoke test |

## 2. 目标用户体验

### 2.1 维护者

维护者可以打开控制台或报告，直接看到：

- 当前 `data_service`、`codexPat`、`HarnessOS`、`Navia` 哪些已绑定真实路径，哪些仍不可用，以及下一步动作；
- 哪些测试分组慢、哪些 warning 超预算、哪些失败属于依赖漂移、沙箱限制、artifact 缺失、public surface drift 或真实回归；
- Agent 长期记忆当前覆盖哪些 artifact、证据、验收状态和过期策略；
- 发布包是否包含 MCP 配置、CLI smoke、HTTP smoke、恢复 checklist、版本化 artifact manifest；
- 能否进入实现、发布、人工审查，或必须退回开发计划阶段。

### 2.2 Coding Agent

Agent 在后续任务开始前可以读取：

- 稳定的 memory index、evidence index、acceptance state、stop conditions；
- 当前项目允许使用的 MCP/CLI/HTTP surface；
- 真实 E2E 结果和未接受状态；
- 针对当前任务的建议读取路径和建议测试；
- 明确禁止事项：不可把 impact candidate 写成 runtime call，不可把 documentation claim 写成 code fact，不可把 `needs_review` 或 `structured_unavailable` 写成 accepted。

### 2.3 审计者

审计者可以检查：

- 长期记忆是否只引用 persisted artifacts 和 evidence refs；
- 控制台是否保留 non-accepted 状态；
- CI/warning 治理是否使用真实测试输出，而不是文档声明；
- 发布恢复包是否泄露本地绝对路径、token、secret、raw traceback 或虚拟环境私有路径；
- 新增 surface 是否有 build/read parity 和 public surface guard。

## 3. In Scope

- 外部项目路径绑定闭环和真实 E2E 状态汇总。
- CI 分组、warning budget、失败归因和 release readiness 文档化。
- Agent 长期记忆 artifact：memory index、evidence index、acceptance state、task briefing、retention policy。
- 交互式维护者控制台的目标体验、数据模型、路由、面板和证据跳转规划。
- 发布与恢复体验：MCP 配置模板、CLI/HTTP smoke commands、restore checklist、release manifest。
- 每阶段 development plan、acceptance plan、pre-implementation audit、focused tests、真实 E2E、PRD/spec review、false-green audit、final acceptance audit 的文档化要求。

## 4. Out of Scope

- 不声称完整恢复复杂项目设计意图。
- 不声称 full call graph、runtime topology、data/control flow 或 type inference。
- 不把 documentation claim 当作 code fact。
- 不把 `needs_review`、`structured_unavailable`、`structured_blocker` 写成 accepted。
- 不伪造外部项目路径、mock-only evidence 或 hardcoded accepted result。
- 不自动删除 `.tmp/` 或任何未确认归属文件。
- 不修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`，除非用户明确批准。

## 5. 完成定义

V2.71-V2.75 文档完成必须满足：

1. PRD、目标架构、开发验收计划、里程碑、验收门槛、coverage matrix、schema contracts、drawio 之间术语一致。
2. 所有 planned 能力只写为计划，不写成 implemented 或 accepted。
3. 每个目标能力都能映射到计划代码实体、artifact、adapter surface 和验收证据。
4. drawio 页数不超过 8 页，中文书写，包含当前/目标差异、架构实体、开发验收计划、里程碑、出门条件。
5. 外部项目无真实路径时只能记录 `structured_unavailable` 或 `structured_blocker`。
6. 后续实现开始前必须完成 phase-specific development plan、acceptance plan、pre-implementation audit，并关闭 fatal/major 审计意见。

