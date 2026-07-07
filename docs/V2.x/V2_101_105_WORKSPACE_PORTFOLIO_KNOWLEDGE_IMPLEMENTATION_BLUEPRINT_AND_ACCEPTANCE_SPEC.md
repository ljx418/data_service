# V2.101-V2.105 Implementation Blueprint and Acceptance Spec

## 1. 实现边界

本文件是实现指导，不是实现完成证据。V2.101-V2.105 进入代码阶段前，必须重新生成 phase-specific plan、acceptance plan 和 pre-implementation audit。

默认不修改：

- `backend/app/api/v1/data_service.py`
- `backend/data_service/service.py`

## 2. GitHub CLI 设计转化

| GitHub CLI 机制 | data_service 转化 |
| --- | --- |
| core/additional command 分组 | 新增 `portfolio` 顶级命令组，避免继续塞入 `code` 阶段命令 |
| alias 可组合命令 | 后续可提供只读 command recipe，但本阶段不实现用户自定义 alias |
| extension 扩展命令 | 仅采用 adapter 插拔思想；不执行外部不可信插件 |
| `gh api` 通用 façade | 保持 CLI/MCP/HTTP parity，所有入口读取同一 artifact |
| extension 不覆盖 core command | `portfolio` 不覆盖 `ingest`、`code`、`query` 现有语义 |

## 3. 建议代码落点

```text
backend/data_service/workspace_portfolio/
  __init__.py
  schemas.py
  persistence.py
  discovery.py
  classifier.py
  document_intake.py
  project_builder.py
  media_probe.py
  release_gate.py
  report.py

backend/data_service/cli_portfolio.py
backend/data_service/mcp_workspace_portfolio_tools.py
backend/app/api/v1/workspace_portfolio.py
```

前端落点：

```text
frontend/src/pages/KnowledgePage.vue
frontend/src/api/portfolio.ts
```

`KnowledgePage.vue` 的本阶段目标不是新增说明页，而是把已落盘 artifact 转成可人工巡检的维护者首页与状态面板。UI 组件至少包括：

- `PortfolioStatusHeader`：读取 `release_gate.json`，展示 final status、阻断数、next action。
- `ProjectRegistrySummary`：读取 `project_registry.json`，展示 code_project、doc_project、media_corpus、needs_review、structured_unavailable 计数。
- `BuildRunSummary`：读取 `project_build_runs.json`，展示 accepted、failed、structured_blocker、structured_unavailable 计数。
- `MediaReadinessSummary`：读取 `media_readiness.json`，展示 OCR provider、conversion provider、ocr_required rows。
- `ProjectRegistryTable`：读取 `project_registry.json.projects[]`，展示 classification、status、evidence refs、next action。
- `ProjectDetailDrawer`：读取 `project_build_runs.json` 和 `portfolio_index.json`，展示单项目 build steps、artifact refs、query entrypoints、project brief refs、可用 context refs 或结构化缺口。
- `ReleaseGatePanel`：读取 `release_gate.json` 和 `false_green_audit.md`，展示 No-Go 与出门状态。

## 4. Artifact Layout

```text
workspace/{workspace_id}/portfolio/
  project_registry.json
  source_candidate_matrix.json
  media_readiness.json
  project_build_runs.json
  portfolio_index.json
  release_gate.json
  portfolio_report.html
```

## 5. 关键实现策略

- `discovery.py`：只读枚举一级目录，跳过 `.git`、`node_modules`、`.venv`、cache、generated artifact。
- `classifier.py`：基于 `.git`、README、docs、package.json、pyproject.toml、requirements.txt、AGENTS.md、图片/PPT/PDF 统计生成分类。
- `project_builder.py`：对 `code_project` 执行有界 code asset service 编排，默认至少完成 import/snapshot/inventory/symbols/project brief；overview/context pack 可在可复跑条件满足时作为增强证据；对 `doc_project` 优先生成 source candidate/readiness，只有实际完成 ingest/query/source trace 时才能写成 ingest accepted；失败写入 build run status。
- `media_probe.py`：检查 extractor 和 provider readiness，不运行高成本 OCR，除非显式允许并记录 provider health。
- `report.py`：从 persisted artifacts 渲染 HTML，不重新扫描文件系统。
- `/knowledge`：读取 HTTP read API，不直接读取 workspace 内部文件。
- 前端截图验收只证明真实 UI 读取了真实 API 响应；不得把截图作为 project build、docs ingest、source trace 或 OCR accepted 的替代证据。
- 真实 workspace E2E 必须支持 bounded scan/build 参数；超出有界范围的项目必须记录为 `needs_review` 或待执行 next action，不能 silent skip，也不能计入 accepted。
- `portfolio.ts` 必须定义与 HTTP read contract 对齐的 typed client；若接口不可用，UI 必须展示 `structured_unavailable` 或 `structured_blocker`，不能回退到硬编码示例数据。
- `release_gate.py` 必须同时输出 `implementation_status` 和 `portfolio_final_status`；前者用于判断本阶段功能是否实现，后者用于判断 workspace 项目组合是否全绿。OCR/provider 缺失时不得把 `portfolio_final_status` 写成 accepted。

## 6. Accepted 条件

| 阶段 | Accepted 条件 | Non-accepted 条件 |
| --- | --- | --- |
| V2.101 | 真实 workspace scan 生成 project registry，分类有 evidence | 只列目录名、无分类证据 |
| V2.102 | 至少一个真实代码项目生成 codebase import、snapshot、inventory/symbols、project brief 或 overview artifacts；失败或未构建项目有 structured reason | 全部 mock、只生成 README 摘要，或把未构建项目计入 accepted |
| V2.103 | 文档/媒体 readiness 覆盖真实 PPT/PDF/DOCX/图片样本 | 图片/扫描件无 OCR 证据却 accepted |
| V2.104 | `/knowledge` 读取 persisted artifacts 并有 headless 截图 | UI 硬编码状态或只打开空页面 |
| V2.105 | release gate 聚合所有状态并拒绝 false-green | 阻断项被隐藏或计入 accepted |

## 7. False-green 审计

实现必须拒绝：

- 将 `/knowledge` 截图替代 build/query/source trace evidence。
- 将 OCR 不可用的图片资料写成 accepted。
- 将 docs claim 写成 code fact。
- 将目录扫描成功等同于项目理解成功。
- 将不可读项目 silent skip。
