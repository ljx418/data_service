# V2.76-V2.80 Milestones and Exit Gates

## 1. 里程碑

| 里程碑 | 阶段 | 完成物 | 用户可见效果 |
| --- | --- | --- | --- |
| M1 | V2.76 | reconciled matrix、status diff | 维护者能判断文档状态与真实验收是否一致 |
| M2 | V2.77 | project preflight、E2E rerun records | 维护者能接入外部项目并看到真实不可用原因 |
| M3 | V2.78 | warning inventory、reduction plan、release gate | 维护者能看到 warning 是否影响发布 |
| M4 | V2.79 | experience model、panel contract、action registry | 控制台目标体验和动作入口清晰 |
| M5 | V2.80 | readiness gate、restore verification、smoke records | 发布恢复路径可执行、可审计、可阻断 |

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

## 4. 最终出门条件

V2.76-V2.80 最终 accepted 需要：

- 所有 coverage matrix row 从 `planned` 转为 `accepted` 前必须有真实 evidence；
- V2.76-V2.80 focused tests 全部通过；
- V2.71-V2.75 回归通过；
- full coverage matrix 完成 evidence 回填；
- `codexPat`、`HarnessOS`、`Navia` 有 accepted 或 structured unavailable/blocker，不可用不算 accepted；
- warning gate 为 accepted 或 structured blocker，不能被隐藏；
- release readiness 为 accepted 或保留人工 `needs_review`；
- 可视化验收报告和截图证据存在；
- protected legacy 文件无 diff。

## 5. 阻断条件

出现以下情况必须停止并回到开发计划：

- 把 `structured_unavailable`、`structured_blocker`、`needs_review` 写成 accepted；
- 以文档声明替代代码事实；
- 以 mock-only evidence 证明外部项目 accepted；
- 控制台隐藏 non-accepted 状态；
- warning 通过删除测试覆盖而不是治理降低；
- public artifact 泄露本地绝对路径、secret、token、raw traceback；
- 需要修改 protected legacy 文件但没有用户明确批准；
- 验收测试不通过且无法用结构化 blocker 解释。
