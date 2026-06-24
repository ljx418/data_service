# V2.59-V2.62 PRD：Public Surface Stabilization, E2E Expansion, Packaging, Portal UX Integration

## 1. 阶段定位

V2.59-V2.62 承接已验收的 V2.54-V2.58 Human-Agent Deepening。上一阶段已经把 Human Portal、Agent Task Workflow、Doc-Code Governance Evidence Loop、Multi-project Regression、Restore UX 做到可实现、可验收、可恢复。本阶段目标不是继续扩大分析承诺，而是把已实现能力稳定成更可交付、更可复现、更可被人类使用的产品化层。

本阶段包含四个目标：

| 阶段 | 名称 | 核心目标 |
| --- | --- | --- |
| V2.59 | Public Surface Stabilization | 固化 Human-Agent Deepening 的 MCP、CLI、HTTP 合同和兼容性快照 |
| V2.60 | Real Project E2E Expansion | 扩展 HarnessOS、Navia、codexPat 的真实项目 E2E，减少 `structured_unavailable` |
| V2.61 | Acceptance Artifact Cleanup and Packaging | 整理验收产物、临时文件、依赖、handoff、交付包 |
| V2.62 | Human Portal UX Integration | 把 V2.54-V2.61 的状态、证据、恢复入口整合进人类 Portal 体验 |

## 2. 用户问题

当前项目已经具备阶段能力，但交付和持续演进仍有缺口：

- Public surface 已新增，但缺少独立的 contract snapshot、兼容性迁移说明和 drift 诊断。
- V2.57 中 HarnessOS、Navia 仍是 `structured_unavailable`，没有进一步拆分为路径缺失、时间预算、依赖限制、artifact 缺失或真实回归。
- 当前工作树含 `.tmp/`、测试依赖和大量新增文档，缺少明确的交付边界、版本控制清单和清理策略。
- Human Portal 能生成项目理解页面，但尚未把 public surface 稳定状态、真实 E2E 覆盖、restore readiness、交付状态作为一体化维护者体验呈现。

## 3. 目标体验

### 3.1 人类维护者

维护者可以打开一个阶段 Portal 或验收摘要，直接看到：

- 当前对外能力有哪些，MCP、CLI、HTTP 是否一致；
- 哪些 public surface 是新增、稳定、变更或需要迁移；
- data_service、codexPat、HarnessOS、Navia 的真实 E2E 状态；
- 失败是依赖漂移、沙箱限制、路径不可用、artifact 缺失、public surface drift、真实回归还是需要人工审查；
- 哪些产物应该提交，哪些是本地临时目录；
- 下一步维护动作和出门条件是否满足。

### 3.2 Coding Agent

Agent 在后续修改前可以获得：

- 已冻结的 public surface contract snapshot；
- 变更影响面和兼容性检查命令；
- 真实项目 E2E 的可用性和不可用原因；
- 清晰的禁止事项、stop conditions、required tests；
- Portal 中直接可读的阶段状态和证据路径。

### 3.3 架构审计者

审计者可以检查：

- surface snapshot 与当前注册表是否一致；
- MCP / CLI / HTTP build-read parity 是否完整；
- 真实项目 E2E 是否用真实仓库和真实 artifact，不是 mock-only；
- cleanup 是否删除或忽略了本地临时产物而没有删除验收证据；
- Portal 是否把 `needs_review`、`structured_unavailable`、`structured_blocker` 保持为非 accepted。

## 4. In Scope

- Human-Agent Deepening public surface contract snapshot。
- MCP / CLI / HTTP parity matrix。
- Contract drift report 和 migration note。
- data_service、codexPat、HarnessOS、Navia 的真实项目 E2E 扩展计划与结果记录。
- `.tmp/`、测试依赖、验收产物、文档交付包的 cleanup/package policy。
- Human Portal 集成 public surface status、E2E status、restore readiness、delivery checklist。
- focused tests、public surface guard、real E2E、PRD/spec review、false-green audit、acceptance audit。

## 5. Out of Scope

- 不声称完整恢复复杂项目设计意图。
- 不声称 full call graph、runtime topology、data/control flow 或 type inference。
- 不把 documentation claim 当作 code fact。
- 不把 `needs_review`、`structured_unavailable`、`structured_blocker` 写成 accepted。
- 不为了通过验收而伪造外部项目路径、mock-only evidence 或 hardcoded result。
- 不修改 legacy 大文件 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`，除非用户明确批准。
- 不自动删除未确认归属的用户文件。

## 6. 完成定义

V2.59-V2.62 完成必须满足：

1. 每个阶段开始前有 development plan、acceptance plan、pre-implementation audit。
2. 每个阶段结束后有 focused tests、真实项目 E2E、PRD/spec review、false-green audit、acceptance audit。
3. Public surface snapshot、parity matrix、drift report 均有 artifact path 和测试证据。
4. 外部项目不可用必须记录为 `structured_unavailable` 或 `structured_blocker`，不能 accepted。
5. Cleanup/package policy 明确哪些文件提交、哪些忽略、哪些需要人工确认。
6. Portal 集成展示只读取 persisted artifacts，不创造 artifact 外事实。
7. 出门验收必须包含 V2.46-V2.58 baseline regression、V2.59-V2.62 focused tests、public surface guard、real E2E、diff check、protected file diff check。
