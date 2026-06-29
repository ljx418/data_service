# V2.76-V2.80 PRD：项目验收硬化与发布闭环

## 1. 阶段定位

V2.76-V2.80 承接 V2.71-V2.75 已实现并本地验收的 Agent memory、CI governance、interactive console、release restore 能力。本阶段只把已暴露的剩余缺口转成可实现、可验收、可审计的产品目标，不扩大代码理解承诺。

当前事实：

- `data_service` 已可作为真实项目完成本地 E2E。
- `codexPat`、`HarnessOS`、`Navia` 仍缺少真实可读路径，不能 accepted。
- V2.71-V2.75 coverage matrix 仍有 planning baseline 回填不一致风险。
- warnings 已被治理为可见状态，但尚未形成削减闭环和 release gate。
- 维护者控制台仍是 artifact-backed HTML 原型，不是完整产品化面板体验。
- release readiness 保持 `needs_review`，需要 restore verification、smoke run records 和人工出门条件。

本阶段目标是把“阶段验收已通过”推进为“可重复接入外部项目、可追踪 warning 收敛、可交互审查、可发布恢复”的闭环。

| 阶段 | 名称 | 用户目标 |
| --- | --- | --- |
| V2.76 | Acceptance Matrix Reconciliation | 维护者能看到文档矩阵、验收报告和真实 artifact 状态一致 |
| V2.77 | External Project Real Binding | 维护者能配置外部项目真实路径并执行 preflight/E2E rerun |
| V2.78 | CI Warning Reduction | 维护者能看到 warning owner、削减计划、预算变化和 release gate |
| V2.79 | Maintainer Console Productization | 维护者能在统一控制台理解状态、风险、下一步和证据跳转 |
| V2.80 | Release Readiness Closure | 维护者能基于 restore verification、smoke records 和出门条件判断是否发布 |

## 2. 目标体验

### 2.1 维护者

维护者打开控制台或验收报告后，可以完成四件事：

- 判断哪些 PRD 能力已经有真实 evidence，哪些仍是 `planned`、`needs_review` 或 `structured_unavailable`。
- 为外部项目填写真实路径，运行 preflight，看到不可用原因和下一步。
- 查看 warning 是否减少、是否超预算、是否阻断 release。
- 按 release checklist 运行 restore、MCP/CLI/HTTP smoke，并获得可审计的出门结论。

### 2.2 Coding Agent

Agent 在开发前可以读取：

- 最新 acceptance matrix reconciliation；
- 外部项目 binding/preflight/E2E 状态；
- warning reduction plan 与建议测试；
- 控制台产品化 schema 和 stop conditions；
- release readiness gate 与 restore/smoke run records。

Agent 不得把文档声明当作代码事实，不得把 `structured_unavailable`、`structured_blocker`、`needs_review` 写成 accepted。

### 2.3 审计者

审计者需要能检查：

- coverage matrix 是否由真实 artifact/test/report 回填；
- 外部项目 accepted 是否有真实 repo path、依赖检查和 E2E result；
- warning reduction 是否只是隐藏 warning；
- 控制台是否保留 non-accepted 状态；
- release readiness 是否泄露本地绝对路径、secret、token、raw traceback 或 private venv path。

## 3. In Scope

- V2.71-V2.75 matrix/status/report 一致性回填计划。
- 外部项目真实路径接入、preflight、E2E rerun 和结构化不可用策略。
- CI warning owner、budget、reduction plan、release gate。
- 维护者控制台产品化信息架构、面板 schema、证据跳转和审计入口。
- release readiness、restore verification、smoke run records、handoff package。
- 每个子阶段的 development plan、acceptance plan、pre-implementation audit、focused tests、真实 E2E、PRD/spec review、false-green audit、final acceptance audit。

## 4. Out of Scope

- 不承诺完整恢复复杂项目设计意图。
- 不承诺 full call graph、runtime topology、data/control flow 或 type inference。
- 不把 documentation claim 当作 code fact。
- 不把 `needs_review`、`structured_unavailable`、`structured_blocker` 写成 accepted。
- 不伪造外部项目路径、mock-only evidence 或 hardcoded accepted result。
- 不自动删除 `.tmp/` 或任何未确认归属文件。
- 不修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`，除非用户明确批准。

## 5. 完成定义

文档开发完成必须满足：

1. PRD、目标架构、开发验收计划、里程碑、验收门槛、coverage matrix、schema contracts、drawio 术语一致。
2. 所有 V2.76-V2.80 能力在代码实现前均标记为 `planned`，不能写成 implemented 或 accepted。
3. 每个目标能力映射到计划代码实体、artifact、adapter surface 和验收证据。
4. drawio 页数不超过 8 页，中文书写，包含当前/目标差异、架构实体、开发验收计划、里程碑、出门条件。
5. 外部项目无真实路径时只能记录 `structured_unavailable` 或 `structured_blocker`。
6. 后续实现开始前必须完成 phase-specific development plan、acceptance plan、pre-implementation audit，并关闭 fatal/major 审计意见。
