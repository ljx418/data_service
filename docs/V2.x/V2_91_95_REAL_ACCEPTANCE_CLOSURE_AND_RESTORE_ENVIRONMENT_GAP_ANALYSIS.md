# V2.91-V2.95 Gap Analysis

## 1. 当前架构与目标架构差异

| 当前状态 | 目标状态 | Gap |
| --- | --- | --- |
| V2.86 Full Corpus 已 accepted | 全部 release gate 高风险项可验收 | Route A、quality、external project、human approval 未闭环 |
| 服务可运行 | focused regression 可复跑 | 当前迁移 venv 不可靠，系统 Python 缺 pytest/venv |
| Route A 合同结构存在 | Route A 有真实资料和人工验收 | 缺用户代表性资料包、脱敏、截图、reviewer decision |
| Quality review 结构存在 | 质量建议有人工决策 | 缺 human quality decisions |
| External project closure 结构存在 | 外部项目均有路径或 unavailable 决议 | codexPat/HarnessOS/Navia 缺真实可读路径 |
| Release Gate 可聚合阻断项 | Final release 可明确出门或明确阻断 | dependency hygiene、restore smoke、human approval 缺证据 |

## 2. 主要风险

- False-green：把服务启动成功写成测试通过。
- False-green：把 Full Corpus accepted 写成 Route A accepted。
- False-green：把自动质量建议写成人工审查 accepted。
- False-green：把外部项目 unavailable 计入 accepted。
- False-green：human approval 缺失时仍声明 final release accepted。
- 过度承诺：声称完整项目设计意图恢复、full call graph、runtime topology、data/control flow 或 type inference。

## 3. 缓解策略

- 所有 public output 保留 `needs_review`、`structured_unavailable`、`structured_blocker`。
- 所有 accepted row 绑定真实 artifact、命令结果、API/CLI/MCP 结果或人工签核。
- Route A 和 Quality 阶段必须允许人工输入缺失时自然停在 `needs_review`。
- External Project 阶段必须允许缺路径项目自然停在 `structured_unavailable`。
- Release Gate 阶段以最差高风险状态作为 final release status。

## 4. 文档阶段判定

当前文档目标可以支撑下一阶段实施规划，但不能作为 V2.91-V2.95 实现完成证据。进入实现前仍需 phase-specific development plan、acceptance plan 和 pre-implementation audit。

