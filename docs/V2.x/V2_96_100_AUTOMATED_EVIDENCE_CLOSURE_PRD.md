# V2.96-V2.100 PRD：少人工真实验收与出门证据闭环

## 1. 阶段定位

V2.96-V2.100 承接 V2.91-V2.95 的阶段验收结论：文档完整支撑范围内的自动化实现已完成，但 final release 仍为 `structured_blocker`。本阶段目标不是扩大项目理解承诺，而是减少人工验收负担，把仍需人工判断或外部输入的高风险项转化为可复跑、可审计、可明确阻断的证据流程。

本阶段不声明，也不得在验收中暗示：

- 不得声称已完整恢复复杂项目设计意图。
- 不得声称已具备 full call graph、runtime topology、data/control flow 或 type inference。
- 不得声称 Route B / Full Corpus 能替代 Route A 用户代表性资料。
- 不得将 `needs_review`、`structured_unavailable`、`structured_blocker` 计入 accepted。

## 2. 当前事实基线

| 能力 | 当前事实 | 下一阶段目标 |
| --- | --- | --- |
| Focused tests | V2.86-V2.95 focused tests 与 public surface guard 通过 | 保持回归可复跑，并覆盖 V2.96-V2.100 |
| 默认 shell CLI | `python -m data_service code real-acceptance-closure --help` 仍被 legacy parser 拒绝 | 修复默认入口或调整文档命令，使 shell CLI 有真实 accepted 证据 |
| Route A | 结构已实现，缺真实资料、脱敏、截图/headless evidence、人工验收 | 自动生成 Route A 证据包，人类只确认高风险项 |
| Quality Review | 结构已实现，缺 reviewer decision | 自动预审建议并生成最小人工决策队列 |
| External Project E2E | data_service 可跑，codexPat/HarnessOS/Navia 缺路径 | 提供路径配置、可读性检查、E2E 或 structured unavailable 决议 |
| Release Gate | 可聚合阻断，final release 未 accepted | 自动聚合 runtime、Route A、Route B、Full Corpus、Quality、External、dependency、human approval |
| 展示材料 | `docs/present/` 已生成理解材料，imag2 生图环境缺失 | 可作为理解材料，不作为代码验收证据 |

## 3. 阶段目标

| 阶段 | 名称 | 目标体验 |
| --- | --- | --- |
| V2.96 | Default CLI Gap Closure | 维护者能通过默认 shell CLI 访问 real-acceptance-closure 命令族，或看到明确不可用原因 |
| V2.97 | Route A Evidence Automation | 维护者提供真实资料后，系统自动完成资料清单、脱敏检查、截图/headless evidence 和人工最小确认记录 |
| V2.98 | Human Quality Decision Minimization | 系统自动汇总质量建议、证据、风险等级和推荐决策，人类只处理高风险或证据不足项 |
| V2.99 | External Project E2E Governance | 维护者能配置外部项目路径，系统自动检查可读性、执行 scoped smoke/E2E 或形成 unavailable 决议 |
| V2.100 | Automated Release Evidence Gate | 系统自动聚合所有出门证据，明确 final release accepted、needs_review、structured_unavailable 或 structured_blocker |

## 4. 目标用户体验

### 4.1 维护者

维护者应能在一个报告或面板中看到：

- 默认 CLI、MCP、HTTP surface 是否一致。
- Route A 资料从输入到验收的证据链。
- 哪些质量建议已由机器预审，哪些需要人工确认。
- 外部项目路径是否可读、E2E 是否可跑、不可用原因是什么。
- final release 为什么能出门或不能出门。

### 4.2 Coding Agent

Coding Agent 应能：

- 使用 CLI/MCP/HTTP 任一入口读取同一组 persisted artifacts。
- 按 `artifact_refs`、`evidence_refs`、`unresolved` 和 `next_actions` 判断任务状态。
- 在缺证据时保持 `needs_review` 或 `structured_unavailable`，不自行改写为 accepted。

### 4.3 审计者

审计者应能：

- 复跑 focused tests、CLI 命令、HTTP read、MCP tool inventory。
- 验证 Route A、Quality、External 和 Release Gate 每项 accepted 均绑定真实证据。
- 确认 `docs/present/` 仅为说明材料，不替代验收。

## 5. In Scope

- 默认 shell CLI gap closure 的文档和验收计划。
- Route A 真实资料证据自动化计划。
- 质量决策少人工工作流计划。
- 外部项目路径治理与 E2E 计划。
- dependency hygiene、restore smoke、human approval 的 release gate 证据计划。
- PRD、目标架构、开发验收计划、实现蓝图、schema contract、phase package、coverage matrix、milestones、gap、test mapping、pre-implementation audit、document audit、drawio。

## 6. Out of Scope

- 不做代码实现。
- 不自动删除任何工作树文件。
- 不默认修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。
- 不用展示图、文档描述、mock-only、sample-only 证据作为 accepted。

## 7. 完成定义

本阶段文档完成必须满足：

1. 每个目标体验映射到具体代码实体、artifact、public surface、focused test 或 unresolved reason。
2. drawio 不超过 8 页，中文书写，展示当前架构到目标架构差异、实体关系、开发计划、里程碑、验收门槛和出门条件。
3. 文档明确 V2.96-V2.100 是 implementation guidance，不是 implementation acceptance。
4. coverage matrix 明确 accepted、needs_review、structured_unavailable、structured_blocker 的证据门槛。
5. `docs/present/` 被标注为理解材料，不作为代码验收证据。
