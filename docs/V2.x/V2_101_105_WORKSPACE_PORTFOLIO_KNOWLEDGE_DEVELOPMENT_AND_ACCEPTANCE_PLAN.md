# V2.101-V2.105 Development and Acceptance Plan

## 1. 阶段计划

| 阶段 | 开发目标 | 计划产物 | 用户可见体验 |
| --- | --- | --- | --- |
| V2.101 | Workspace Portfolio Discovery | `project_registry.json`、`discovery_report.md` | 用户看到 workspace 下每个目录的分类、证据和 next action |
| V2.102 | Project Knowledge Builder | `project_build_runs.json`、`portfolio_index.json` | Agent 可读取项目的 code asset、project brief、docs/media readiness、可用 context refs 或结构化缺口 |
| V2.103 | Document and Media Intake | `source_candidate_matrix.json`、`media_readiness.json` | 用户看到 PPT/PDF/DOCX/YAML/图片/扫描件的可抽取性和 OCR 缺口 |
| V2.104 | Knowledge Console Portfolio Panel | `/knowledge` portfolio panel、headless screenshots | 用户在控制台看到真实项目组合状态和建库路径 |
| V2.105 | Portfolio Release Gate | `release_gate.json`、`false_green_audit.md`、`portfolio_report.html` | 用户看到下一阶段能否出门，以及阻断项补证路径 |

## 1.1 原型体验计划

`/knowledge` 目标体验按 `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_PROTOTYPE_UX_SPEC.md` 执行。实现完成后用户应看到：

- 维护者首页：总状态、项目数量、build 状态、media readiness、next actions。
- 项目组合列表：分类、证据、build 状态、不可用原因。
- 项目详情：code asset、project brief、docs/media readiness、可用 context refs、evidence trace 或结构化缺口。
- 媒体 readiness：PPT/PDF/DOCX/YAML/图片/扫描件的可抽取性和 OCR/provider 状态。
- Release Gate：phase 状态、false-green audit、阻断项和补证路径。

## 2. 子阶段流程

每个子阶段开始前必须落盘：

- phase-specific development plan。
- phase-specific acceptance plan。
- pre-implementation audit。
- GitHub CLI 参考设计是否仍适用的轻量复核。

每个子阶段结束后必须落盘：

- focused test result。
- real workspace E2E result。
- PRD/spec review。
- false-green audit。
- acceptance audit report。

## 3. 验收规则

- workspace scan 必须使用真实 `/mnt/c/workspace` 或配置的真实 allowed root；实现阶段允许使用有界扫描和有界构建参数，但必须记录截断策略、未构建项目和 next action。
- 代码项目 accepted 必须有 codebase import、snapshot、inventory/symbols、project brief 或 overview artifact；不得要求默认生成 full trace 或完整 context pack。
- 文档目录如果声明 ingest accepted，必须有 ingest/query/source trace；如果仅完成 readiness，则状态必须为 `needs_review` 或 `structured_unavailable`，不能混写为 ingest accepted。
- 图片、扫描 PDF、图片型 PPT 在 OCR 不可用时必须为 `ocr_required` 或 `structured_unavailable`。
- `/knowledge` 面板 accepted 必须通过 API 读取 persisted artifacts，不能硬编码。
- 所有 public output 必须做路径脱敏，不能泄露本机绝对路径、secret、token、raw traceback。
- UI 截图只证明用户体验路径存在；build accepted 仍必须由 artifacts、命令/API/MCP 结果支撑。source trace 只在文档 ingest accepted 时作为必需证据。

### 3.1 验收状态分级

每轮阶段验收必须同时输出：

- `implementation_status`：判断本阶段功能是否真实实现、可复跑、可审计。
- `portfolio_final_status`：判断 workspace 内所有高风险项目、资料和媒体是否全部 accepted。

如果 OCR/provider、外部路径、权限或人工资料归属缺失导致 `portfolio_final_status` 非 accepted，只要系统正确输出 `needs_review`、`structured_unavailable` 或 `structured_blocker`，且 false-green audit 通过，`implementation_status` 仍可 accepted。报告必须明确这不是“全部资料已被完整理解”。

## 4. 真实数据要求

验收优先使用：

- `/mnt/c/workspace/data_service`
- `/mnt/c/workspace/codexPat`
- `/mnt/c/workspace/harnessOS`
- `/mnt/c/workspace/navia`
- `/mnt/c/workspace/xpert`
- `/mnt/c/workspace/技术分享`
- `/mnt/c/workspace/1-AI教案`
- `/mnt/c/workspace/我在城市的深海里漂流`

不可读、依赖缺失或无权限时必须保留 `structured_unavailable`，不能 silent skip。

## 5. 停止条件

出现以下情况必须停止实现并返回计划阶段：

- 需要修改受保护 legacy 大文件但没有明确批准。
- 需要自动安装系统依赖才能让验收变绿。
- 需要把 OCR 缺失、外部路径不可读或 UI-only 截图写成 accepted。
- project registry 与 `/mnt/c/workspace` 实际目录明显不一致。
- `/knowledge` 展示与 persisted artifacts 不一致。

## 6. 文档阶段出门门槛

当前文档开发阶段出门必须满足：

- PRD、目标架构、原型 UX、开发验收计划、实现蓝图、schema、coverage、E2E、gap、里程碑、审计、drawio 均已落盘。
- drawio 页数不超过 8，中文书写，并包含目标/当前架构差异、代码实体分层、开发验收计划、验收门槛和 No-Go。
- 所有文档均明确 implementation guidance，不是 implementation acceptance。
- 文档没有将 OCR 缺失、UI-only、scan-only、docs claim 写成 accepted。
- 文档明确区分 `implementation_status` 与 `portfolio_final_status`，避免把结构化不可用误读为全绿。
