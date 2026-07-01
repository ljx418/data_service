# V2.81-V2.85 PRD：真实文档资料验收与发布闭环

## 1. 阶段定位

V2.81-V2.85 承接 V2.76-V2.80 已实现的项目验收硬化能力。本阶段不扩大代码理解承诺，不声称完整恢复复杂项目设计意图；只把人工体验中暴露的缺口转成可执行、可验收、可审计的真实资料补验目标。

当前事实：

- V2.76-V2.80 代码开发与自动化阶段验收已完成。
- 思维导图 / 可视化理解方向在人工体验中基本 OK。
- 本轮人工验收没有使用真实文档资料，因此真实资料人工验收不能 accepted。
- `codexPat`、`HarnessOS`、`Navia` 仍缺少真实可读路径，不能 accepted。
- human release approval 仍为 `needs_review`。
- 最终 release 仍不能 accepted。

本阶段目标是把“控制台能看、报告能审计”推进为“维护者能用真实文档资料完成端到端体验验收，并把结果接入 release readiness”。

| 阶段 | 名称 | 用户目标 |
| --- | --- | --- |
| V2.81 | Real Document Sample and Scenario Contract | 维护者能确认真实资料样本、验收路径、截图和证据标准 |
| V2.82 | Real Document Import and Wiki Acceptance | 维护者能用真实资料完成导入、解析和 Wiki artifact 验收 |
| V2.83 | Retrieval, GraphRAG and Source Trace Acceptance | 维护者能检索真实资料、查看 GraphRAG 结果并追溯来源 |
| V2.84 | Quality Governance and Correction Acceptance | 维护者能基于真实资料执行质量治理或纠错链路 |
| V2.85 | Release Closure Rerun and Human Sign-off | 维护者能把真实资料补验、外部项目状态和人工审批纳入出门判断 |

## 2. 目标体验

### 2.1 维护者

维护者可以用真实文档资料完成以下路径：

- 创建或选择 workspace；
- 导入真实文档资料；
- 触发解析 / build；
- 查看 Wiki artifact；
- 执行检索或 GraphRAG；
- 查看 Source trace；
- 查看质量治理或纠错建议；
- 在验收报告中看到每一步的截图、状态、证据和未闭环原因。

### 2.2 审计者

审计者需要能确认：

- 验收使用的是真实资料，不是 mock-only evidence；
- 每个 accepted 结论都有真实资料路径说明、执行命令或截图证据；
- 失败项进入 `needs_review`、`structured_unavailable` 或 `structured_blocker`；
- 报告没有把人工体验方向 OK 写成真实资料验收 accepted；
- release readiness 没有绕过外部项目路径和人工审批。

### 2.3 Coding Agent

Agent 在后续实现或补验前必须读取：

- 真实资料样本 contract；
- 执行路径和截图标准；
- source trace / quality governance 验收条件；
- V2.76-V2.80 evidence index；
- release readiness stop conditions。

Agent 不得把 documentation claim 当作 code fact，不得把 `needs_review`、`structured_unavailable`、`structured_blocker` 写成 accepted。

## 3. In Scope

- 真实资料样本选择规则、脱敏规则和验收路径。
- 真实资料导入、解析、Wiki artifact、检索 / GraphRAG、Source trace、质量治理或纠错链路。
- 人工体验截图、步骤、结果和 false-green audit。
- V2.76-V2.80 验收硬化证据的只读引用。
- release readiness 重新汇总真实资料验收、外部项目路径和 human approval。
- PRD、目标架构、开发验收计划、里程碑、验收门槛、coverage matrix、schema contracts、test/E2E mapping 和 drawio。

## 4. Out of Scope

- 不承诺完整恢复复杂项目设计意图。
- 不承诺 full call graph、runtime topology、data/control flow 或 type inference。
- 不把文档标题、截图文案或报告声明当作代码事实。
- 不把真实资料人工体验方向 OK 写成真实资料验收 accepted。
- 不伪造真实文档资料、真实外部项目路径或 human approval。
- 不自动删除 `.tmp/` 或任何未确认归属文件。
- 不修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`，除非用户明确批准。

## 5. 完成定义

文档开发完成必须满足：

1. PRD、目标架构、开发验收计划、里程碑、验收门槛、coverage matrix、schema contracts、test mapping、drawio 术语一致。
2. 所有未执行真实资料补验的项目保持 `needs_review`，不能 accepted。
3. 每个目标体验映射到真实用户路径、现有代码实体、计划 artifact 和验收证据。
4. drawio 页数不超过 8 页，中文书写，包含目标架构与当前架构差异、具体代码实体、开发及验收计划、里程碑、验收门槛和出门条件。
5. 外部项目无真实路径时只能记录 `structured_unavailable` 或 `structured_blocker`。
6. 后续进入代码实现或补验前必须完成 phase-specific development plan、acceptance plan、pre-implementation audit，并关闭 fatal/major 审计意见。
