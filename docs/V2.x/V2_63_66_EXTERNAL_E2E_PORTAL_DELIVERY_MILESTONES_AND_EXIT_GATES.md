# V2.63-V2.66 Milestones and Exit Gates

## 1. 里程碑

| 里程碑 | 阶段 | 交付结果 | 用户可感知效果 |
| --- | --- | --- | --- |
| M0 | 阶段准备 | PRD、目标架构、开发验收计划、gap/drawio、文档审计 | 维护者能判断本阶段是否过度承诺 |
| M1 | V2.63 | 外部项目完整 E2E matrix 和 failure diagnosis | 维护者知道哪些外部项目真实通过，哪些不可用及原因 |
| M2 | V2.64 | Portal V3+ 状态面板和维护者首页 | 维护者能从 Portal 快速理解项目能力、风险和下一步 |
| M3 | V2.65 | version manifest、review package、cleanup plan | 维护者能审查交付包和工作树清理边界 |
| M4 | V2.66 | contract baseline、diff、compatibility report | Agent 和维护者能识别 public surface 回归风险 |
| M5 | 阶段 closure | focused tests、real E2E、PRD review、false-green audit、final acceptance audit | 项目进入可复盘、可交付、可继续演进状态 |

## 2. 阶段入口门槛

进入 V2.63 实现前必须满足：

- 本阶段文档齐全并通过文档审计。
- drawio 已由人类确认方向未偏移、未过度承诺。
- V2.59-V2.62 final acceptance audit 存在。
- 当前外部项目路径、依赖和运行权限被重新确认或结构化标记。
- protected legacy 文件保持不修改，除非用户明确批准。

## 3. 每阶段出门条件

每个子阶段出门必须具备：

- focused test 通过或 failure 被打回开发计划。
- 真实项目 E2E 通过，或以 `structured_unavailable` / `structured_blocker` 记录且不计 accepted。
- PRD/spec review 明确无 fatal/major 规格偏差。
- false-green audit 明确无 accepted 造假、mock-only accepted、unavailable accepted。
- acceptance audit report 给出 pass / structured blocker / needs review 结论。

## 4. 最终出门条件

V2.63-V2.66 最终出门必须满足：

- data_service 真实 E2E accepted。
- codexPat、HarnessOS、Navia 全部 accepted 或有结构化不可用/阻塞说明，并明确不计入 accepted。
- Portal V3+ 展示外部 E2E、合同稳定性、交付状态、下一步动作和出门状态。
- Delivery manifest 能解释新增源码、测试、文档、验收产物和本地临时文件。
- Contract regression 能输出 baseline/diff/compatibility/diagnosis。
- baseline regression、focused tests、public surface guard、compileall、diff check、protected file check 通过。

## 5. 打回规则

出现以下任一情况必须停止进入下一阶段，回到开发计划或请求人类确认：

- fatal 或 major PRD/architecture 偏差。
- 外部项目不可用被写成 accepted。
- Portal 隐藏 needs_review、structured_unavailable、structured_blocker。
- Delivery cleanup 尝试自动删除未确认用户文件。
- Contract breaking change 被静默通过。
- 修改 protected legacy 文件但没有用户明确批准。
