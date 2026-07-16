# V2.106-V2.110 Milestones and Exit Gates

## M1：V2.106 Coverage and Architecture State Closure

出门条件：

- V2.101-V2.105 coverage matrix 已回填实现状态。
- 目标架构和 drawio 不再把已实现实体写成 planned。
- non-accepted 状态没有被隐藏。
- document audit 记录 pass for implementation guidance。

## M2：V2.107 OCR and Media Evidence Closure

出门条件：

- `ocr_provider_health.json` 存在。
- `media_evidence_matrix.json` 覆盖真实图片、扫描 PDF、PPT/PPTX、PDF、DOCX rows。
- OCR/provider 缺失时 media rows 保持 `structured_unavailable`。
- 只有真实 OCR/文本抽取证据存在时才允许 accepted。

## M3：V2.108 Full Workspace Project Build Governance

出门条件：

- `full_build_queue.json` 存在。
- 每个项目有 queue status、cache policy、timeout policy 或 structured reason。
- `project_build_diagnosis.json` 解释 accepted、failed、timeout、skipped、structured_unavailable。
- skipped/timeout 不得计入 accepted。

## M4：V2.109 Document Ingest / Query / Source Trace Closure

出门条件：

- `document_source_trace_closure.json` 存在。
- 每个 accepted 文档 row 有 source import evidence、query evidence、source trace evidence。
- readiness-only rows 不得 accepted。
- 缺 source trace 时必须 `needs_review` 或 `structured_unavailable`。

## M5：V2.110 Portfolio Final Release Gate

出门条件：

- `final_release_gate.json` 聚合项目、媒体、文档、UI、public surface、false-green audit。
- `final_evidence_report.html` 中文、可读、证据路径清晰。
- `false_green_recheck.md` 覆盖 scan-only、readiness-only、UI-only、OCR、silent skip、docs claim 风险。
- `portfolio_final_status` 遵循最差高风险状态。

## No-Go

- 高风险 `needs_review` 被计入 accepted。
- OCR 缺失媒体被 accepted。
- UI 截图或 HTML report 替代 build/source trace evidence。
- 未构建项目 silent skip。
- 受保护 legacy 文件未授权修改。
- 自动安装系统依赖。

