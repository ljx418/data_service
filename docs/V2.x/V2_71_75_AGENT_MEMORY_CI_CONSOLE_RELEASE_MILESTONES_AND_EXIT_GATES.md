# V2.71-V2.75 Milestones and Exit Gates

## 1. 里程碑

| 里程碑 | 阶段 | 完成物 | 用户可见效果 |
| --- | --- | --- | --- |
| M1 | V2.71 | external closure artifacts | 看清外部项目路径、E2E、不可用原因 |
| M2 | V2.72 | CI matrix、warning budget、diagnosis | 看清测试稳定性、warning 风险、失败归因 |
| M3 | V2.73 | memory index、evidence index、acceptance state | Agent 能读取项目长期记忆和证据边界 |
| M4 | V2.74 | console model、status panels、HTML | 维护者首页能集中展示状态、风险、下一步 |
| M5 | V2.75 | release manifest、MCP template、smoke、runbook | 本地发布恢复路径可执行、可审计 |

## 2. 阶段进入条件

每个子阶段进入开发前必须具备：

- development plan；
- acceptance plan；
- pre-implementation audit；
- PRD/spec review；
- protected legacy file strategy；
- false-green risk checklist；
- 真实数据验收策略。

Fatal 或 major 审计意见未关闭时不得进入实现。

## 3. 阶段出门条件

每个子阶段结束必须具备：

- focused tests；
- 真实 `data_service` E2E；
- 外部项目 accepted 或 structured unavailable/blocker 证据；
- PRD/spec review；
- false-green audit；
- acceptance audit report；
- public surface guard；
- protected legacy diff check。

## 4. 阻断条件

出现以下情况必须停止并回到开发计划：

- 把 `structured_unavailable`、`structured_blocker`、`needs_review` 写成 accepted；
- 以文档声明替代代码事实；
- 以 mock-only evidence 证明外部项目 accepted；
- 控制台隐藏 non-accepted 状态；
- public artifact 泄露本地绝对路径、secret、token、raw traceback；
- 需要修改 protected legacy 文件但没有用户明确批准；
- 验收测试不通过且无法用结构化 blocker 解释。

