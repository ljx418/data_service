# V2.91-V2.95 Milestones and Exit Gates

## M0：文档基线

出门条件：

- PRD、目标架构、开发验收计划、coverage matrix、gap、test mapping、pre-implementation audit、drawio 已落盘。
- Drawio 页数不超过 8 页，中文书写，包含具体代码实体、状态、分层和交互关系。
- 文档明确当前为 implementation guidance，不是 implementation acceptance。

## M1：V2.91 Runtime Restore

出门条件：

- 可运行 pytest runtime 已恢复，或记录可复现 blocker。
- V2.81-V2.90 focused regression 可复跑，或 `structured_blocker` 明确说明依赖缺口。
- 本机环境诊断不泄露 private path、secret、raw traceback。

## M2：V2.92 Route A Closure

出门条件：

- 有用户代表性真实资料包或明确 `needs_review`。
- 有脱敏审查结果、截图/headless evidence 和人工验收记录。
- Route A 缺任一高风险证据时不能 accepted。

## M3：V2.93 Quality Decision Closure

出门条件：

- 每条质量建议有 reviewer decision 或 `needs_review`。
- Decision history 可追溯。
- Rule effect review 不改写上游 artifact。

## M4：V2.94 External Project Closure

出门条件：

- `data_service`、`codexPat`、`HarnessOS`、`Navia` 均有 accepted、structured_unavailable 或 structured_blocker。
- 缺路径项目不计入 accepted。
- E2E command、artifact refs 和 unresolved reason 可复核。

## M5：V2.95 Final Release Gate

出门条件：

- Runtime restore、Route A、Route B、Full Corpus、Quality、External Project、dependency hygiene、human approval 均有状态。
- 所有 blocking states 在 report 和 artifact 中保留。
- 只有全部高风险项 accepted 后，final release 才能 accepted。

## 禁止出门条件

- 把 documentation claim 当作 code fact。
- 把 `needs_review` / `structured_unavailable` / `structured_blocker` 写成 accepted。
- 把 mock-only 或 sample-only 证据当作真实验收。
- 把服务能启动当作 pytest 全量验收通过。

