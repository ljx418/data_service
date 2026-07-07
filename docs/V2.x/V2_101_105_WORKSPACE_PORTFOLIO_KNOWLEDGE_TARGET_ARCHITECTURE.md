# V2.101-V2.105 Target Architecture：Workspace 项目组合知识化

## 1. 架构原则

- 扫描外部 workspace 只读执行，不写入被扫描项目目录。
- 所有 public output 必须包含 `schema_version`、`workspace_id`、`status`、`artifact_refs`、`evidence_refs`、`warnings`、`unresolved`、`next_actions`。
- build 接口生成 persisted artifacts；read 接口只读取 persisted artifacts。
- `/knowledge` 只能展示 persisted artifacts 和 API 返回结果，不能硬编码 accepted 结论。
- OCR、LibreOffice、pdftoppm、tesseract 缺失时输出结构化状态，不自动安装。
- 不扩大项目理解承诺，不声明 full call graph、runtime topology、data/control flow 或 type inference。

## 2. 当前架构实体

| 实体 | 当前状态 | 职责 |
| --- | --- | --- |
| `backend/data_service/code_assets/registry.py` | 已实现 | 注册单个 codebase root |
| `backend/data_service/code_assets/snapshot.py` | 已实现 | 生成 repo file manifest、stats、warnings |
| `backend/data_service/code_assets/inventory.py` | 已实现 | 生成 public surface inventory |
| `backend/data_service/code_assets/symbols.py` | 已实现 | 生成 Python symbol index |
| `backend/data_service/code_assets/overview.py` | 已实现 | 生成 evidence-backed project overview |
| `backend/data_service/code_assets/context/service.py` | 已实现 | 生成 Agent context pack |
| `backend/data_service/service.py` | 已实现，受保护 | DataService ingest/query 基础能力 |
| `backend/app/llmwiki/extractors/*` | 已实现 | 文本、HTML、CSV、JSON、PDF、PPTX、PPT、DOCX、YAML 抽取器 |
| `backend/data_service/research_notebook/providers/ocr_tesseract.py` | 已实现，当前环境不可用 | OCR provider adapter |
| `frontend/src` 与 `backend/app/static/knowledge_console` | 已实现基础控制台 | `/knowledge` 静态 UI |

## 3. 目标新增实体

| 目标实体 | 状态 | 职责 |
| --- | --- | --- |
| Workspace Portfolio Scanner | 待新增 | 枚举 allowed roots 下一级目录，生成 project candidates |
| Project Classifier | 待新增 | 根据 `.git`、README、docs、package/pyproject/requirements、媒体文件等信号分类 |
| Project Build Orchestrator | 待新增 | 对代码项目执行有界 code asset build；对 docs/media 生成 ingest/readiness/source candidate 状态；重型 context pack/source trace 只在可复跑条件满足时执行 |
| Document Media Intake Probe | 待新增 | 生成格式 readiness、extractor status、OCR requirement、unsupported reason |
| Portfolio Persistence | 待新增 | 写入 `workspace/{workspace_id}/portfolio/*` artifacts |
| Portfolio API Adapter | 待新增 | 暴露 CLI/MCP/HTTP build/read/report parity |
| Knowledge Console Portfolio Panel | 待修改 | 展示项目组合状态、建库状态、OCR 缺口和 next actions |
| Portfolio Release Gate | 待新增 | 聚合 scan/build/media/UI/E2E/false-green 状态 |

### 3.1 `/knowledge` 目标 UI 实体

| UI 实体 | 状态 | 目标数据来源 | 职责 |
| --- | --- | --- | --- |
| Portfolio Status Header | 待新增 | `release_gate.json` | 展示本阶段总状态和阻断摘要 |
| Project Registry Summary | 待新增 | `project_registry.json` | 展示项目总数、分类统计和 root ref |
| Project Registry Table | 待新增 | `project_registry.json.projects[]` | 展示每个目录分类、证据、next action |
| Project Detail Drawer | 待新增 | `project_build_runs.json`、`portfolio_index.json` | 展示单项目 code asset、project brief、docs/media readiness、可用 context refs 或结构化缺口 |
| Media Readiness Panel | 待新增 | `media_readiness.json`、`source_candidate_matrix.json` | 展示 OCR、PPT/PDF/DOCX/YAML readiness |
| Release Gate Panel | 待新增 | `release_gate.json`、`false_green_audit.md` | 展示出门状态、false-green 检查和补证路径 |

## 4. 建议代码落点

优先新增独立包：

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
```

Adapter 计划：

```text
backend/data_service/cli_portfolio.py
backend/data_service/mcp_workspace_portfolio_tools.py
backend/app/api/v1/workspace_portfolio.py
frontend/src/pages/KnowledgePage.vue
frontend/src/api/portfolio.ts
```

默认不修改：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

如后续必须修改受保护文件，必须先写入 phase-specific audit 并取得明确批准。

## 5. 分层关系

| 层级 | 具体实体 | 交互 |
| --- | --- | --- |
| 用户入口层 | `/knowledge`、HTML report、CLI、MCP、HTTP | 发起 scan/build/read/report，查看状态 |
| Adapter 层 | `cli_portfolio.py`、MCP tools、HTTP router、`frontend/src/api/portfolio.ts` | 参数校验、调用 service、统一 envelope |
| Portfolio Service 层 | discovery、classifier、project_builder、media_probe、release_gate | 生成项目组合事实、建库结果和阻断项 |
| Existing Capability 层 | code assets、DataService ingest、llmwiki extractors、OCR provider | 被编排复用，不改变原有 contract |
| Persistence 层 | `workspace/{workspace_id}/portfolio/*` | 持久化 artifacts、reports、evidence refs |
| Gate 层 | false-green audit、release gate | 根据最差高风险状态决定 final status |

## 6. Public Surface 目标

CLI：

```text
python -m data_service portfolio scan --workspace-id ... --root /mnt/c/workspace
python -m data_service portfolio build --workspace-id ...
python -m data_service portfolio read --workspace-id ...
python -m data_service portfolio report --workspace-id ...
```

MCP：

```text
knowledge_workspace_portfolio_scan
knowledge_workspace_portfolio_build
knowledge_workspace_portfolio_read
knowledge_workspace_portfolio_report
```

HTTP：

```text
POST /api/workspaces/{workspace_id}/portfolio/scan
POST /api/workspaces/{workspace_id}/portfolio/build
GET  /api/workspaces/{workspace_id}/portfolio
GET  /api/workspaces/{workspace_id}/portfolio/report
```

## 7. Artifact Layout

```text
workspace/{workspace_id}/portfolio/
  project_registry.json
  source_candidate_matrix.json
  media_readiness.json
  project_build_runs.json
  portfolio_index.json
  release_gate.json
  false_green_audit.md
  portfolio_report.html
```

## 8. No-Go 设计

- 不允许以文件夹名或 README 标题作为 accepted 项目理解证据。
- 不允许把 OCR 缺失的图片/扫描件写成 accepted。
- 不允许把 `/knowledge` 截图当作建库成功证据。
- 不允许把 docs claim 写成 code fact。
- 不允许将未扫描目录静默忽略；必须记录 ignored reason 或 unresolved reason。

## 9. 目标体验与架构映射

| 目标体验 | 架构实体 | Artifact | 验收证据 |
| --- | --- | --- | --- |
| 维护者看到 workspace 项目组合总览 | Portfolio Status Header、Project Registry Summary | `project_registry.json`、`release_gate.json` | API read result、headless screenshot |
| 维护者理解每个项目分类原因 | Project Registry Table、Project Classifier | `project_registry.json` | classification evidence refs |
| Agent 获取项目简报和可用上下文入口 | Project Build Orchestrator、Project Detail Drawer | `project_build_runs.json`、`portfolio_index.json` | code asset artifact refs、project brief refs、context availability status |
| 维护者识别 OCR 和媒体缺口 | Media Readiness Panel、Media Probe | `media_readiness.json`、`source_candidate_matrix.json` | provider health、ocr_required rows |
| 审计者判断能否出门 | Release Gate Panel、Portfolio Release Gate | `release_gate.json`、`false_green_audit.md` | PRD/spec review、false-green audit |
