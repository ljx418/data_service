# V2.101-V2.105 Prototype UX Spec：知识运营台项目组合体验

## 1. 体验目标

本原型规格用于约束 V2.101-V2.105 的 `/knowledge` 项目组合知识化体验。它不是实现完成证据，也不能替代真实 scan/build/query/source trace evidence；source trace 只在文档 ingest accepted 时作为必需证据。

目标体验：

- 维护者打开 `/knowledge` 后，能快速判断 workspace 下有哪些项目和资料目录。
- 维护者能看到每个项目的状态、证据、建库进度、不可用原因和下一步动作。
- Agent 能从同一套 persisted artifacts 获取项目组合状态，而不是依赖 UI 文案。
- 审计者能用截图确认 UI 展示路径，同时用 artifacts 和命令结果确认事实。

## 2. 首屏：维护者首页 / 状态面板

### 2.1 页面实体

| UI 实体 | 目标数据来源 | 状态 |
| --- | --- | --- |
| Portfolio Status Header | `release_gate.json` | 待新增 |
| Project Registry Summary | `project_registry.json` | 待新增 |
| Build Run Summary | `project_build_runs.json` | 待新增 |
| Media Readiness Summary | `media_readiness.json` | 待新增 |
| Next Actions List | `release_gate.json.unresolved[]` | 待新增 |

### 2.2 用户看到的效果

维护者首屏应能看到：

- 本次扫描的 root ref。
- 项目总数、accepted、needs_review、structured_unavailable、structured_blocker 数量。
- 哪些项目已有 project brief、code asset refs 或可用 context refs，可供 Agent 后续使用。
- 哪些资料因为 OCR、格式、依赖或权限不能入库。
- 出门状态是 accepted、needs_review、structured_unavailable 还是 structured_blocker。

### 2.3 验收截图要求

Headless 截图必须能证明：

- 页面打开的是 `/knowledge`。
- 首屏显示 portfolio 状态。
- non-accepted 状态没有被隐藏。
- 页面展示的统计值可追溯到 persisted artifacts。

## 3. 项目组合列表

### 3.1 页面实体

| UI 实体 | 目标数据来源 | 状态 |
| --- | --- | --- |
| Project Registry Table | `project_registry.json.projects[]` | 待新增 |
| Classification Badge | `classification` | 待新增 |
| Evidence Link Cell | `evidence_refs[]` | 待新增 |
| Build Status Cell | `project_build_runs.json.runs[]` | 待新增 |
| Next Action Cell | `next_actions[]` | 待新增 |

### 3.2 用户看到的效果

列表必须让人快速识别：

- 哪些目录是代码项目。
- 哪些目录是纯文档或媒体资料库。
- 哪些目录被忽略以及原因。
- 哪些项目已完成 code asset build。
- 哪些项目需要补路径、补 OCR、补人工确认或调整 ignore rule。

## 4. 项目详情

### 4.1 页面实体

| UI 实体 | 目标数据来源 | 状态 |
| --- | --- | --- |
| Project Identity Panel | `project_registry.json.projects[]` | 待新增 |
| Code Asset Panel | `project_build_runs.json` | 待新增 |
| Docs Ingest Panel | `source_candidate_matrix.json` | 待新增 |
| Agent Context Panel | `portfolio_index.json` | 待新增 |
| Evidence Trace Panel | `evidence_refs[]` | 待新增 |

### 4.2 用户看到的效果

项目详情必须展示：

- 分类依据：README、docs、manifest、技术栈 marker、media counts。
- code asset 是否完成 snapshot、inventory/symbols、project brief、overview 或 context pack；未生成的增强证据必须显示结构化缺口。
- docs 是否完成 readiness；只有实际完成 ingest/query/source trace 的资料才能显示为 ingest accepted。
- 不可用原因和下一步动作。
- 明确提示：该项目不是完整设计意图恢复。

## 5. 文档与媒体 readiness

### 5.1 页面实体

| UI 实体 | 目标数据来源 | 状态 |
| --- | --- | --- |
| Source Candidate Matrix | `source_candidate_matrix.json` | 待新增 |
| Media Readiness Matrix | `media_readiness.json` | 待新增 |
| OCR Provider Status | provider health artifact | 待新增 |
| Unsupported Reason Badge | `unsupported_reason` | 待新增 |

### 5.2 用户看到的效果

维护者必须能区分：

- 文本可抽取并可入库的资料。
- 可以入库但需要人工复核的资料。
- 因 OCR provider 缺失而不能 accepted 的图片或扫描件。
- 因 LibreOffice/soffice 缺失而不能转换的 legacy PPT。
- 被跳过的缓存、生成文件、私有文件或超大文件。

## 6. Release Gate 面板

### 6.1 页面实体

| UI 实体 | 目标数据来源 | 状态 |
| --- | --- | --- |
| Release Status Banner | `release_gate.json.status` | 待新增 |
| Phase Status Matrix | `release_gate.json.phase_statuses` | 待新增 |
| False-green Audit Panel | `false_green_audit.md` | 待新增 |
| Blocker Summary | `release_gate.json.unresolved[]` | 待新增 |

### 6.2 用户看到的效果

Release Gate 必须说明：

- 哪些阶段通过。
- 哪些阶段被 `needs_review`、`structured_unavailable` 或 `structured_blocker` 阻断。
- 阻断是否来自 OCR、路径、权限、UI-only、scan-only、docs claim 或 silent skip 风险。
- 下一步由系统自动处理还是需要人类确认。

## 7. No-Go UX

- 不用大段说明文字替代真实状态面板。
- 不隐藏 `needs_review`、`structured_unavailable`、`structured_blocker`。
- 不把截图、卡片或颜色写成验收事实。
- 不把项目名称、README 标题或 docs claim 写成 code fact。
- 不在 UI 中暗示图片、扫描件或复杂 PPT 已被理解，除非存在 OCR/视觉证据。

## 8. 验收路径

最小验收路径：

1. 执行 portfolio scan，生成 `project_registry.json`。
2. 执行 portfolio build，生成 `project_build_runs.json`、`source_candidate_matrix.json`、`media_readiness.json`。
3. 打开 `/knowledge`。
4. 截取维护者首页。
5. 打开一个代码项目详情并截图。
6. 打开媒体 readiness 面板并截图。
7. 打开 release gate 面板并截图。
8. 对照 artifacts、截图和 false-green audit 判定是否可出门。
