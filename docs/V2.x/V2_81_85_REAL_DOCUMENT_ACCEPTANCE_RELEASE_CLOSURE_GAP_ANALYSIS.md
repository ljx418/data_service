# V2.81-V2.85 Gap Analysis

## 1. 当前架构与目标架构差异

| 差异 | 当前状态 | 目标状态 | 风险 |
| --- | --- | --- | --- |
| 真实文档资料人工验收 | 思维导图方向基本 OK，但未用真实资料 | 使用真实资料完成导入、解析、检索/GraphRAG、Source trace、质量治理补验 | 方向体验被误写成真实资料 accepted |
| Source trace 验收 | 自动化报告主要证明阶段能力和截图 | 真实资料查询结果必须能追溯 source / unit / evidence | 检索体验无法审计 |
| 质量治理体验 | 质量能力存在，但未用真实资料补验 | 真实资料触发 low-signal / feedback / correction 路径 | 质量问题被 UI 或报告隐藏 |
| Release readiness | V2.80 为 `structured_unavailable` | 汇总真实资料补验、外部项目状态、human approval | 最终 release 过度承诺 |
| 外部项目路径 | `codexPat`、`HarnessOS`、`Navia` 无真实路径 | 有真实路径则 rerun，无路径保持 structured unavailable | unavailable 被误 accepted |

## 2. False-green 风险

- 用示例页面或截图替代真实文档资料。
- 用 mock-only evidence 证明真实资料体验。
- 把 Source trace 缺失写成 accepted。
- 把 GraphRAG 结果描述为完整架构或运行拓扑。
- 把人工体验方向 OK 写成 release accepted。
- 外部项目仍不可用却写成 accepted。

## 3. 风险缓解

- 真实资料样本 contract 必须先于补验执行。
- 每个 accepted 步骤必须绑定 artifact refs、截图证据、命令或 API/CLI/MCP 结果。
- Source trace 缺失必须进入 `needs_review` 或 `structured_blocker`。
- 质量治理必须保留 low-signal、feedback、correction review 状态。
- release closure 必须保留 external project 和 human approval 状态。

## 4. 技术路线判断

推荐路线：新增独立 `real_document_acceptance` code asset package，并把真实资料来源分为四条路线：

- Route A：用户提供真实或脱敏真实资料，用于最终代表性验收。
- Route B：使用仓库内 `docs/` 真实项目文档，用于自动化 dry run 和工程烟测。
- Route C：无可用真实资料时记录 `structured_unavailable`。
- Route D：mock 或 synthetic 资料只能用于开发 fixture，不能作为 accepted evidence。

优点：

- 不修改 legacy 大文件；
- 避免在用户真实资料路径不明确前过度承诺；
- 可以复用现有 Knowledge Console、workspace/source/query/GraphRAG/quality API；
- 可以清晰分离自动化阶段验收和人工真实资料验收。
- Route B 能降低自动化开发阻塞，但最终用户代表性验收仍需要 Route A 或明确的人类接受。

不推荐路线：

- 在现有 HTML 报告中硬编码真实资料 accepted；
- 直接修改 legacy route/service；
- 用截图或演示页面替代真实资料导入；
- 在 drawio 中使用抽象概念而不列具体代码实体。

## 5. 当前文档支撑度

本文件落盘后，文档集预计支撑：

- 阶段级文档开发支撑：约 98%。
- 立即进入真实资料补验计划：约 94%。
- 立即进入代码实现规划：约 94%。
- 立即进入自动化实现：约 90%，前提是 Route B 可作为自动化 dry run 数据源。
- 最终用户代表性验收支撑：约 80%，因为 Route A 真实资料和 human approval 仍是外部条件。
- implementation acceptance：0%，因为本阶段尚未实现或补验。

剩余主要风险不是文档结构，而是真实资料样本、外部项目路径、Source trace 质量和 human approval 这些运行时/人工条件。
