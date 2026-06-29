# V2.76-V2.80 Gap Analysis

## 1. 当前架构与目标架构差异

| 差异 | 当前状态 | 目标状态 | 风险 |
| --- | --- | --- | --- |
| Coverage matrix 回填 | V2.71-V2.75 matrix 仍有 planned baseline | 由真实 artifact/test/audit 回填 observed status | 文档和实现状态不一致 |
| 外部项目接入 | `codexPat`、`HarnessOS`、`Navia` 无真实路径 | 支持真实路径、preflight、E2E rerun | unavailable 被误 accepted |
| Warning 治理 | 已有 budget，但未形成 reduction closure | warning inventory、owner、reduction plan、release gate | warnings 被忽略 |
| 控制台体验 | artifact-backed HTML 原型 | 产品化面板 contract、action registry、证据跳转 | 控制台隐藏 non-accepted |
| Release readiness | `needs_review` | restore、smoke、warning、external、approval gate | 发布结论过度承诺 |

## 2. False-green 风险

- 文档 planned row 被手动改成 accepted，但没有 artifact/test/E2E。
- 外部项目路径不可读，却通过 mock-only evidence accepted。
- warning 数量仍高，但 release gate 标记 accepted。
- 控制台只展示绿色摘要，隐藏 `needs_review` 或 `structured_unavailable`。
- release package 泄露本地路径或 private virtualenv path。

## 3. 风险缓解

- 每个 accepted row 必须绑定 evidence refs、artifact path、test command/result。
- 外部项目必须执行真实 path/readability/dependency/E2E 检查；路径缺失为 `structured_unavailable`，依赖或沙箱阻断为 `structured_blocker`。
- warning reduction 必须保留 baseline/current/budget/owner。
- 控制台只渲染 structured artifacts。
- release readiness 必须执行 redaction check。

## 4. 技术路线判断

推荐路线：沿用 modular code asset package。

优点：

- 不修改 legacy 大文件；
- 与 V2.63-V2.75 模式一致；
- MCP/CLI/HTTP build/read parity 清晰；
- 可逐阶段 focused test。

不推荐路线：

- 在现有控制台 HTML 中硬编码所有新状态；
- 直接修改 legacy route/service；
- 用单个巨型 service 包含所有验收硬化逻辑；
- 用文档表格替代真实 artifact。

## 5. 当前文档支撑度

本文件落盘后，文档集预计支撑：

- 阶段级开发支撑：约 96%。
- 立即进入 V2.76 phase-specific planning：约 94%。
- 最终出门验收计划支撑：约 93%。
- implementation acceptance：0%，因为尚未实现。

剩余支撑缺口必须在每个子阶段 pre-implementation audit 中关闭。当前主要剩余风险不是文档设计缺口，而是外部项目真实路径、warning 真实基线、release 人工审批这三类外部或运行时条件。
