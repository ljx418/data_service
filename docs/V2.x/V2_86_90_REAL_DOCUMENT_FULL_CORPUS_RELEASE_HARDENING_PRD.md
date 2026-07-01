# V2.86-V2.90 PRD：全量真实文档验收与发布闭环加固

## 1. 阶段定位

V2.86-V2.90 承接 V2.81-V2.85 的真实文档资料验收与发布闭环结果。本阶段不扩大代码理解承诺，不声称完整恢复复杂项目设计意图，不声称 full call graph、runtime topology、data/control flow 或 type inference。

当前已确认事实：

- V2.81-V2.83 Route B 仓内真实文档验收已 accepted。
- V2.84 质量治理仍为 `needs_review`，原因是缺少人工质量审查。
- V2.85 release closure 仍为 `structured_unavailable`，原因是外部项目路径和 human approval 缺失。
- Route A 用户代表性真实资料验收未完成，不能作为 final accepted。
- 完整 `docs/V2.x` 全量文档构建暴露 HTML extractor 问题，错误包含 `name 'Section' is not defined`，不能 accepted。

本阶段目标是把“仓内真实文档小样本验收可用”推进为“全量真实文档、用户代表性资料、质量治理人工审查、外部项目状态、发布出门判断均可被明确执行、审计和阻断”。

## 2. 阶段目标

| 阶段 | 名称 | 目标体验 |
| --- | --- | --- |
| V2.86 | Full Corpus E2E Hardening | 维护者能对 `docs/V2.x` 全量真实文档执行导入、解析、构建、查询和失败分类 |
| V2.87 | Route A Representative Material Acceptance | 维护者能用用户代表性真实资料包完成脱敏、导入、截图和人工验收记录 |
| V2.88 | Quality Governance Human Review Closure | 维护者能审查质量建议、纠错建议和规则影响，并把审查结果落成证据 |
| V2.89 | External Project E2E Closure | 维护者能看到 `codexPat`、`HarnessOS`、`Navia` 的真实路径、可用状态和 E2E 结论 |
| V2.90 | Release Gate and Restore Hygiene | 维护者能基于真实资料、外部项目、human approval、恢复体验和依赖状态做最终出门判断 |

## 3. 目标用户体验

### 3.1 维护者

维护者应能：

- 选择或创建真实文档工作区，导入 `docs/V2.x` 全量文档。
- 看到 HTML、Markdown、JSON、drawio 等不同资料的解析结果和失败分类。
- 对真实资料执行 Wiki、检索、GraphRAG 和 Source trace 体验。
- 在质量治理页面或报告中看到低信号资料、纠错建议、人工审查状态和下一步动作。
- 在发布闭环报告中看到 Route A、Route B、外部项目、human approval、restore/smoke、dependency hygiene 的状态。
- 明确知道哪些项目 accepted，哪些仍是 `needs_review`、`structured_unavailable` 或 `structured_blocker`。

### 3.2 审计者

审计者应能确认：

- accepted 结论均来自真实资料、真实命令、真实 API/CLI/MCP 结果、截图或 artifact refs。
- Route B 仓内真实文档不能替代 Route A 用户代表性真实资料验收。
- HTML extractor 失败不会被隐藏或写成 accepted。
- 外部项目路径缺失不会被计入 accepted。
- 质量治理和纠错建议没有绕过人工审查。
- 报告没有把 documentation claim 当作 code fact。

### 3.3 Coding Agent

Coding Agent 应能读取本阶段文档后明确：

- 哪些代码实体已存在，哪些是后续候选实现。
- 每个阶段的开发入口、artifact contract、验收命令和出门条件。
- 何时必须保持 `needs_review`、`structured_unavailable` 或 `structured_blocker`。
- 受保护 legacy 文件默认不应修改。

## 4. In Scope

- 全量 `docs/V2.x` 真实文档 E2E 验收路径。
- HTML extractor 已知失败的复现、修复验收标准和 blocker 分类。
- Route A 用户代表性资料包合同、脱敏规则、截图标准和人工验收记录。
- V2.84 质量治理人工审查与纠错链路闭环。
- 外部项目真实路径绑定和 structured unavailable 规则。
- Release gate、restore/smoke、dependency hygiene 和工作树清理审计。
- PRD、目标架构、开发验收计划、里程碑、coverage matrix、gap、test mapping、pre-implementation audit 和 drawio。

## 5. Out of Scope

- 不新增复杂项目设计意图恢复承诺。
- 不声称 full call graph、runtime topology、data/control flow 或 type inference。
- 不把 Route B 小样本验收写成 Route A 代表性验收。
- 不把外部项目缺失路径写成 accepted。
- 不自动删除 `.tmp/`、`backend/.tmp/` 或任何未确认归属文件。
- 不默认修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。

## 6. 完成定义

本阶段文档完成必须满足：

1. PRD、目标架构、开发验收计划、里程碑、coverage matrix、gap、test mapping、drawio 术语一致。
2. 每个目标体验映射到具体代码实体、计划 artifact、真实 E2E 或明确 unresolved reason。
3. drawio 页数不超过 8 页，中文书写，展示当前架构到目标架构的差异、实体关系、开发计划、里程碑、验收门槛和出门条件。
4. `needs_review`、`structured_unavailable`、`structured_blocker` 不被写成 accepted。
5. pre-implementation audit 结论只能是 `pass for implementation guidance` 或列出 fatal/major blocker，不能写成 implementation acceptance。
