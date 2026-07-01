# V2.86-V2.90 Milestones and Exit Gates

## 1. 里程碑

| 里程碑 | 阶段 | 进入条件 | 完成条件 | 不能 accepted 的情况 |
| --- | --- | --- | --- | --- |
| M1 全量文档验收路径 | V2.86 | V2.81-V2.85 Route B evidence 可读 | `docs/V2.x` 全量导入、解析、构建、查询结果可审计 | HTML extractor 失败被隐藏；全量构建未完成且无 blocker |
| M2 Route A 资料包 | V2.87 | 用户代表性资料或缺失状态已确认 | 资料包合同、脱敏说明、人工验收记录可审计 | Route A 缺失却写 accepted；mock-only 充当真实资料 |
| M3 质量治理审查 | V2.88 | V2.84 quality artifact 可读 | 人工 quality review、correction decision、rule effect review 可审计 | 无人工审查却写 accepted；改写上游 artifact |
| M4 外部项目闭环 | V2.89 | 外部项目路径重新确认 | 每个项目 accepted 或 structured unavailable/blocker | 缺路径项目计入 accepted |
| M5 发布出门判断 | V2.90 | M1-M4 状态已汇总 | release gate 明确 final status、证据和 next action | human approval 缺失却 final accepted |

## 2. 阶段出门条件

### V2.86

- 全量真实文档输入范围明确。
- HTML、Markdown、JSON、drawio 的处理状态可见。
- `Section` 错误修复或结构化阻断。
- 有全量构建 artifact、parser failure artifact 和截图/自动化证据。

### V2.87

- Route A sample pack contract 存在。
- redaction review 存在。
- manual acceptance record 存在。
- 未提供代表性资料时状态为 `needs_review`。

### V2.88

- human quality review artifact 存在。
- correction decision history 存在。
- rule effect review 存在。
- 无人工确认的建议保持 `needs_review`。

### V2.89

- `data_service` 真实 E2E 状态存在。
- `codexPat`、`HarnessOS`、`Navia` 路径状态重新确认。
- 不可用项目写 `structured_unavailable` 或 `structured_blocker`。
- unavailable 不计 accepted。

### V2.90

- release gate summary 存在。
- restore/smoke 状态存在。
- dependency hygiene 状态存在。
- protected legacy file diff check 存在。
- human approval 缺失时 final release 不能 accepted。

## 3. 最终出门条件

最终 release accepted 必须同时满足：

1. Route A 用户代表性真实资料验收 accepted。
2. Route B 仓内真实文档验收 accepted。
3. 全量 `docs/V2.x` E2E accepted，或不属于 release 范围且有明确批准的 scope exception。
4. Source trace 可追溯到真实资料。
5. 质量治理和纠错链路有人工审查结论。
6. 外部项目均有 accepted 或明确不可用结论，且不可用不计 accepted。
7. restore/smoke 和 dependency hygiene 状态可审计。
8. human release approval 已记录。
9. false-green audit 无 fatal/major。
10. 受保护 legacy 文件无未批准 diff。

## 4. 阻断规则

以下任一情况必须阻断 final release accepted：

- Route A 未完成。
- HTML extractor 失败导致全量构建不可审计。
- quality review 缺人工确认。
- 外部项目缺路径却被计入 accepted。
- human approval 缺失。
- 报告隐藏 `needs_review`、`structured_unavailable` 或 `structured_blocker`。
- 文档或报告声称 full call graph、runtime topology、data/control flow、type inference 或完整设计意图恢复。
