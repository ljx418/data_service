# V2.101-V2.105 Milestones and Exit Gates

## M1：V2.101 Portfolio Discovery

出门条件：

- `project_registry.json` 存在。
- 至少包含真实 workspace 下的一级目录分类。
- ignored、needs_review、structured_unavailable 不被计入 accepted。
- 路径脱敏通过。

## M2：V2.102 Project Knowledge Builder

出门条件：

- 至少一个真实代码项目生成 code asset artifacts。
- 每个项目 build run 有 command refs、artifact refs 或 structured reason。
- 默认允许有界构建；超出边界的项目必须记录为 `needs_review` 和 next action，不能计入 accepted。
- docs ingest 失败不能 silent skip。
- 不把 README 摘要当作完整项目理解。

## M3：V2.103 Document and Media Intake

出门条件：

- `source_candidate_matrix.json` 覆盖真实 docs 和纯资料目录。
- `media_readiness.json` 明确 OCR/provider 状态。
- 图片、扫描 PDF、图片型 PPT 无 OCR 证据时不能 accepted。
- PPTX/PDF/DOCX 只基于可抽取文本 accepted。

## M4：V2.104 Knowledge Console Portfolio Panel

出门条件：

- `/knowledge` 可展示 portfolio 状态。
- Headless 截图可证明项目列表、项目详情、media readiness 和 release status。
- UI 状态与 persisted artifacts 一致。
- UI-only evidence 不能作为 build accepted。
- 维护者首页包含 portfolio status、project registry summary、build run summary、media readiness summary、next actions。
- 项目详情能展示 artifact refs、evidence refs、query entrypoints、project brief refs、context availability 或结构化缺口。
- API/artifact 缺失时显示 non-accepted 状态，不允许回退到 demo data。

## M5：V2.105 Portfolio Release Gate

出门条件：

- `release_gate.json` 聚合 V2.101-V2.104 状态。
- `false_green_audit.md` 覆盖 scan-only、UI-only、OCR、docs claim、silent skip 风险。
- HTML report 可读、中文、路径脱敏。
- final status 遵循最差高风险项。
- 出门报告必须同步目标架构、当前实现、截图证据、focused tests、真实 workspace E2E、PRD/spec review、false-green audit。

Release gate 必须输出两个状态：

- `implementation_status`：功能实现和自动化验收状态。
- `portfolio_final_status`：workspace 项目组合内所有高风险资料是否全绿 accepted。

当 OCR/provider、权限或人工资料归属缺失时，`implementation_status` 可以在 false-green audit 通过后 accepted，但 `portfolio_final_status` 必须保持 non-accepted，并列出补证路径。

## No-Go

- 任意 non-accepted 状态被计入 accepted。
- 受保护 legacy 文件被未授权修改。
- 自动安装系统依赖。
- 扫描或构建写入外部项目目录。
- 报告隐藏 OCR、路径、权限、人工确认缺口。
