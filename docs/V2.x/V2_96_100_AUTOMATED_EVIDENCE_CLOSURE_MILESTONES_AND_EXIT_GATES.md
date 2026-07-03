# V2.96-V2.100 Milestones and Exit Gates

## M0：文档基线

出门条件：

- PRD、目标架构、开发验收计划、实现蓝图、schema、test mapping、coverage matrix、gap、audit、drawio 已落盘。
- drawio 页数不超过 8 页，中文书写，实体状态和交互关系清晰。
- 文档结论仅为 implementation guidance。

## M1：V2.96 CLI Closure

出门条件：

- 默认 shell CLI 有真实执行结果。
- MCP/HTTP/CLI surface 差异被记录。
- CLI gap 未修复时不能 accepted。

## M2：V2.97 Route A Evidence

出门条件：

- 真实资料、脱敏审查、截图/headless evidence、人工确认均有状态。
- 缺任一高风险证据时保持 `needs_review`。
- `docs/present` 图文不能作为 Route A accepted evidence。

## M3：V2.98 Quality Decision

出门条件：

- 高风险建议有 reviewer decision 或 `needs_review`。
- 低风险自动预审有 evidence refs 和规则说明。
- 自动建议不得替代人工 accepted。

## M4：V2.99 External Project E2E

出门条件：

- `data_service`、`codexPat`、`HarnessOS`、`Navia` 均有真实状态。
- 缺路径项目只允许 `structured_unavailable`。
- E2E 命令、artifact refs、unresolved reason 可复核。

## M5：V2.100 Release Evidence Gate

出门条件：

- runtime、Route A、Route B、Full Corpus、Quality、External、dependency hygiene、restore smoke、human approval 均有状态。
- final release status 使用最差高风险状态。
- 只有所有高风险项 accepted 后，final release 才能 accepted。

## 禁止出门条件

- 文档描述当作 code fact。
- mock-only、sample-only、展示图作为 accepted evidence。
- `needs_review`、`structured_unavailable`、`structured_blocker` 被计入 accepted。
- 受保护 legacy 大文件被未授权修改。
