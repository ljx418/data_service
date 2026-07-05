# V2.96-V2.100 Gap Analysis

## 1. 当前架构与目标架构差异

| 当前状态 | 目标状态 | Gap |
| --- | --- | --- |
| 文档阶段记录 legacy parser 拒绝默认 `code` 入口 | 默认 shell CLI 可直接执行 V2.96-V2.100 命令族 | 已通过 `automated-evidence-closure` 命令族修复；命令级 E2E 证据已落盘 |
| Route A artifact 结构存在 | 真实资料证据链自动生成 | 缺资料扫描、脱敏审查、截图/headless evidence、最小人工确认 |
| Quality decision artifact 结构存在 | 自动预审 + 高风险人工决策 | 缺风险队列、推荐决策、人类 backlog |
| External project validator 存在 | 外部项目路径治理和 E2E 可复跑 | 缺路径 registry、配置入口、不可用决议流程 |
| Release finalizer 可聚合阻断 | 出门证据自动聚合并给补证路径 | dependency hygiene、restore smoke、human approval 未自动化 |
| `docs/present` 可帮助理解 | 展示材料与验收证据分离 | 需明确不作为 accepted evidence |

## 2. 主要风险

- False-green：默认 CLI 没有命令级证据却声明 public surface accepted。
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
- 文档和 drawio 明确实体状态：已实现、needs_review、structured_unavailable、阻断。

## 4. 文档阶段判定

当前 V2.96-V2.100 文档目标可支撑下一阶段自动化开发指导，但不能证明任何 V2.96-V2.100 功能已实现。

## 5. Post-implementation gap status

实现后 gap 判定：

| 项 | 当前状态 | 验收影响 |
| --- | --- | --- |
| Default CLI gap | 已通过 `python -m data_service code automated-evidence-closure <command>` 修复并有命令级 E2E 证据 | V2.96 可声明 implemented-and-tested scope accepted |
| Route A evidence | 代码和 artifact 已实现，仍缺真实代表性资料与人工确认 | 不能 final accepted，保持 `needs_review` |
| Quality decision | 代码和 artifact 已实现，仍缺 high-risk reviewer decision | 不能 final accepted，保持 `needs_review` |
| External project E2E | data_service 可用，codexPat/HarnessOS/Navia 缺真实可读路径 | 不能 final accepted，保持 `structured_unavailable` |
| Release gate | 代码和 false-green recheck 已实现，阻断项仍存在 | 不能声明 final release accepted |

因此，本阶段不得声明“自动化开发阶段已全部完成到出门验收全绿状态”。允许声明的范围仅限：文档完整支撑范围内的实现、测试、命令级 E2E 和审计报告已完成。
