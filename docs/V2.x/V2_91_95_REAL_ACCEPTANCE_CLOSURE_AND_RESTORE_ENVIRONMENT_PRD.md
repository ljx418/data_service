# V2.91-V2.95 PRD：真实验收闭环与本机恢复环境加固

## 1. 阶段定位

V2.91-V2.95 承接 V2.86-V2.90 的真实文档全量验收结果。本阶段不是重新扩大项目理解能力，也不声明完整恢复复杂项目设计意图、full call graph、runtime topology、data/control flow 或 type inference。

当前已确认事实：

- V2.86 Full Corpus E2E 已能以 `docs/V2.x` 为真实输入产出 accepted artifact。
- V2.87 Route A 仍为 `needs_review`，原因是缺用户代表性真实资料包、脱敏审查、截图或人工验收记录。
- V2.88 Quality Governance Human Review 仍为 `needs_review`，原因是缺真实人工质量审查 decision。
- V2.89 External Project E2E 仍为 `structured_unavailable`，原因是 `codexPat`、`HarnessOS`、`Navia` 缺真实可读路径。
- V2.90 Release Gate 仍为 `structured_unavailable`，原因是 Route A、质量人工复核、外部项目、human approval、restore/dependency hygiene 未全部闭环。
- 当前本机测试环境存在恢复缺口：迁移后的 `backend/.venv` 不可作为可靠 pytest runtime，系统 Python 可运行服务但缺 pytest 和 `python3.12-venv`。

本阶段目标是把“自动化实现范围已完成但最终发布不能 accepted”的状态推进为“验收环境可复跑、真实资料可审计、人工决策可追踪、外部项目状态可验证、最终出门门禁可明确通过或明确阻断”。

## 2. 阶段目标

| 阶段 | 名称 | 目标体验 |
| --- | --- | --- |
| V2.91 | Restoreable Acceptance Runtime | 维护者能在本机恢复可运行 pytest/venv/dependency baseline，并复跑 V2.81-V2.90 focused regression |
| V2.92 | Route A Representative Material Closure | 维护者能用用户代表性真实资料包完成脱敏、导入、截图或 headless evidence、人工验收记录 |
| V2.93 | Human Quality Decision Closure | 维护者能审查质量建议、纠错建议和 rule effect，并把人工决策落成证据 |
| V2.94 | External Project E2E Path Closure | 维护者能绑定 `codexPat`、`HarnessOS`、`Navia` 真实路径，执行 E2E 或形成 structured unavailable 决议 |
| V2.95 | Final Release Gate Closure | 维护者能聚合 Route A、Route B、Full Corpus、Quality Review、External Project、restore、dependency hygiene、human approval 并做最终出门判断 |

## 3. 目标用户体验

### 3.1 维护者

维护者应能：

- 看到本机验收环境是否可复跑，若不可复跑能看到具体依赖缺口和修复命令。
- 提供 Route A 代表性资料后，看到资料来源、脱敏结果、导入状态、截图证据和人工验收结论。
- 对质量建议和纠错建议做人工确认、拒绝或继续 review，并看到 decision history。
- 对外部项目路径做一次性绑定检查，明确哪些项目可跑 E2E，哪些只能 structured unavailable。
- 在 Release Gate 面板或报告中看到 final release 是否可 accepted，以及所有阻断项的证据路径。

### 3.2 审计者

审计者应能确认：

- accepted 只来自真实资料、真实命令、真实 API/CLI/MCP 结果、截图或人工签核。
- Route B 和 Full Corpus 不替代 Route A 用户代表性资料。
- 自动质量建议不替代人工质量审查。
- 外部项目路径缺失不计入 accepted。
- dependency/restore 风险不被隐藏。
- 文档描述不当作 code fact。

### 3.3 Coding Agent

Coding Agent 应能读取本阶段文档后明确：

- 哪些代码实体已实现，哪些实体需要新增或修改。
- 每个子阶段的 artifact contract、public surface、验收命令和出门门槛。
- 何时必须保持 `needs_review`、`structured_unavailable` 或 `structured_blocker`。
- 不得默认修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。

## 4. In Scope

- 本机 pytest/venv/dependency baseline 恢复计划和验收标准。
- Route A 用户代表性资料包、脱敏审查、截图 evidence、人工验收记录。
- 质量治理人工审查、纠错 decision history、rule effect review。
- 外部项目路径绑定、真实 E2E、structured unavailable 决议。
- Release Gate finalizer、restore/smoke、dependency hygiene、human approval。
- PRD、目标架构、开发验收计划、实现蓝图、schema contract、phase detailed package、里程碑、coverage matrix、gap analysis、test mapping、pre-implementation audit、document audit、drawio。

## 5. Out of Scope

- 不新增完整设计意图恢复承诺。
- 不声明 full call graph、runtime topology、data/control flow 或 type inference。
- 不把 Route B 或 Full Corpus 结果替代 Route A。
- 不把外部项目 unavailable 写成 accepted。
- 不自动删除 `.tmp/`、`backend/.tmp/` 或任何未确认归属文件。
- 不默认修改 legacy 大文件。

## 6. 完成定义

本阶段文档完成必须满足：

1. PRD、目标架构、计划、实现蓝图、schema contract、phase detailed package、里程碑、coverage matrix、gap、test mapping、document audit、drawio 术语一致。
2. 每个目标体验映射到具体代码实体、计划 artifact、真实 E2E 或明确 unresolved reason。
3. drawio 页数不超过 8 页，中文书写，展示当前架构到目标架构差异、实体关系、开发计划、里程碑、验收门槛和出门条件。
4. `needs_review`、`structured_unavailable`、`structured_blocker` 不被写成 accepted。
5. Pre-implementation audit 只能给出 implementation guidance readiness，不能提前声明 implementation acceptance。
