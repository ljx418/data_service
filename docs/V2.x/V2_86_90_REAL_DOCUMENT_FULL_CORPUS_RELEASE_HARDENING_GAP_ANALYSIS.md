# V2.86-V2.90 Gap Analysis

## 1. 当前差距

| Gap | 当前事实 | 风险 | 目标处理 |
| --- | --- | --- | --- |
| G1 全量 `docs/V2.x` 构建未 accepted | 小样本 Route B 可用，全量构建暴露 HTML extractor `Section` 错误 | 把小样本误当全量验收 | V2.86 修复或结构化阻断 |
| G2 Route A 缺代表性资料 | 用户代表性真实资料未提供 | final real-document UX false-green | V2.87 保持 needs_review，提供资料后才可 accepted |
| G3 质量治理缺人工审查 | V2.84 当前为 `needs_review` | 自动建议被误写 accepted | V2.88 增加人工 review artifact |
| G4 外部项目路径缺失 | `codexPat`、`HarnessOS`、`Navia` 缺真实可读路径 | unavailable 被计入 accepted | V2.89 路径可用才跑 E2E，不可用保持 structured unavailable |
| G5 Release approval 缺失 | human release approval 仍为 `needs_review` | final release 误 accepted | V2.90 release gate 强制阻断 |
| G6 依赖与工作树卫生 | 前端重建产物和 npm audit 风险存在 | 恢复体验或交付审计不清晰 | V2.90 记录 dependency hygiene 和 worktree cleanup plan |

## 2. 目标架构差异

当前架构已经具备：

- `RealDocumentAcceptanceService` 生成 V2.81-V2.85 artifacts。
- HTTP/CLI/MCP build/read surface。
- Knowledge Console 可进行工作区体验。
- V2.81-V2.85 文档和可视化审计报告。

目标架构需要补齐：

- 全量文档 E2E runner。
- HTML extractor hardening。
- Route A acceptance pack。
- Quality review recorder。
- External project closure。
- Release gate aggregator。

## 3. False-green 风险

必须拒绝以下结论：

- “Route B accepted，所以 Route A accepted。”
- “小样本真实文档 accepted，所以全量 `docs/V2.x` accepted。”
- “GraphRAG 有结果，所以具备 full call graph 或 runtime topology。”
- “外部项目没有路径，但整体 accepted。”
- “quality suggestion 已生成，所以质量治理 accepted。”
- “human approval 缺失但 final release accepted。”

## 4. 消减策略

| Gap | 消减动作 | 验收动作 | 未消减状态 |
| --- | --- | --- | --- |
| G1 | 修复 HTML extractor 或记录 blocker | 全量 build + parser failure audit | `structured_blocker` |
| G2 | 定义 Route A 资料包合同 | 人工验收记录 + 截图证据 | `needs_review` |
| G3 | 定义人工质量审查记录 | reviewer decision history | `needs_review` |
| G4 | 重新确认外部路径 | 项目 E2E records | `structured_unavailable` |
| G5 | 定义 release approval gate | release readiness report | `needs_review` |
| G6 | 定义依赖和工作树审计 | dependency/worktree hygiene report | `needs_review` |

## 5. 审计结论

当前文档开发方向可以支撑下一阶段实现规划，但不能证明 V2.86-V2.90 已实现。进入代码实现前必须完成 pre-implementation audit，并确认无 fatal/major 规格偏差。
