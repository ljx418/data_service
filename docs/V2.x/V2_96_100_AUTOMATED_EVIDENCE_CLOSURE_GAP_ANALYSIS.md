# V2.96-V2.100 Gap Analysis

## 1. 当前架构与目标架构差异

| 当前状态 | 目标状态 | Gap |
| --- | --- | --- |
| code parser inventory 包含 real-acceptance-closure | 默认 shell CLI 可直接执行 | legacy parser 仍拒绝 `code` |
| Route A artifact 结构存在 | 真实资料证据链自动生成 | 缺资料扫描、脱敏审查、截图/headless evidence、最小人工确认 |
| Quality decision artifact 结构存在 | 自动预审 + 高风险人工决策 | 缺风险队列、推荐决策、人类 backlog |
| External project validator 存在 | 外部项目路径治理和 E2E 可复跑 | 缺路径 registry、配置入口、不可用决议流程 |
| Release finalizer 可聚合阻断 | 出门证据自动聚合并给补证路径 | dependency hygiene、restore smoke、human approval 未自动化 |
| `docs/present` 可帮助理解 | 展示材料与验收证据分离 | 需明确不作为 accepted evidence |

## 2. 主要风险

- False-green：默认 CLI 仍失败却声明 public surface accepted。
- False-green：Route A 无真实资料却 accepted。
- False-green：质量自动建议替代人工决策。
- False-green：外部项目路径缺失却计入 accepted。
- False-green：展示图或 HTML 报告替代真实 E2E。
- 过度承诺：声称完整项目设计意图恢复或 full call graph。

## 3. 缓解策略

- 每个 accepted row 必须绑定 command/API/MCP result 和 artifact refs。
- Route A 缺真实资料时必须自然停在 `needs_review`。
- 外部项目缺路径时必须自然停在 `structured_unavailable`。
- Release Gate 使用最差高风险状态。
- 文档和 drawio 明确实体状态：已实现、待新增、需修改、阻断。

## 4. 文档阶段判定

当前 V2.96-V2.100 文档目标可支撑下一阶段自动化开发指导，但不能证明任何 V2.96-V2.100 功能已实现。
