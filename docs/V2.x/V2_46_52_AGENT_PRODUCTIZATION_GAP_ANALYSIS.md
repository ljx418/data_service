# V2.46-V2.52 Gap Analysis

## 1. 当前能力

V2.39-V2.45 已接受：

- 大项目 scale 和 scan budget。
- language provider contract。
- workflow/runtime candidates。
- relationship chain v3。
- document semantics v3。
- token budget/context cache。
- profile/taxonomy regression。

## 2. 当前 GAP

| Gap | Impact | Planned Phase |
| --- | --- | --- |
| MCP 使用路径不够产品化 | 其它 Codex 窗口难以稳定调用 | V2.46 |
| 新项目 profile 接入仍靠人工经验 | 大项目效果不稳定 | V2.47 |
| 报告可读性仍偏工程 artifact | 人类理解成本高 | V2.48 |
| task navigation 未形成标准开发路径 | Agent 仍可能重复读仓库 | V2.49 |
| doc-code finding 未完全进入治理闭环 | 架构偏差难以持续追踪 | V2.50 |
| Agent playbook 不够标准化 | 不同 Agent 使用方式不一致 | V2.51 |
| 多项目持续回归未产品化 | 未来阶段容易假通过 | V2.52 |

## 3. 风险

- 过度承诺完整架构理解。
- 把 profile 做成项目特化硬编码。
- HTML 报告美化掉 unresolved/needs_review。
- Agent playbook 给出无 evidence 建议。
- 真实项目不可用时被误写 accepted。

## 4. 缓解措施

- 所有 accepted 结论必须绑定 evidence。
- no-hardcode audit 每阶段执行。
- HTML 必须显示 unresolved/needs_review。
- structured blocker 是合法结果，但不能当作 accepted。
- closure matrix 必须逐行绑定 test command、artifact path 和 audit report。

