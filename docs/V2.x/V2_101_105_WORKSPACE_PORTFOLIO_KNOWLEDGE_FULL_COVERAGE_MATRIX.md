# V2.101-V2.105 Full Coverage Matrix

| 能力 | 阶段 | 目标实体 | Planned artifact | 当前状态 | Required evidence |
| --- | --- | --- | --- | --- | --- |
| Workspace 一级目录发现 | V2.101 | Workspace Portfolio Scanner | `project_registry.json` | planned | 真实 `/mnt/c/workspace` scan command、project rows、ignored rows |
| 项目分类证据 | V2.101 | Project Classifier | `project_registry.json` | planned | `.git`、README、docs、package/pyproject、media counts evidence |
| 忽略/不可用记录 | V2.101 | Discovery Auditor | `discovery_report.md` | planned | ignored reason、structured unavailable reason、next action |
| 代码项目 build 编排 | V2.102 | Project Build Orchestrator | `project_build_runs.json` | planned | codebase import、snapshot、inventory/symbols、project brief 或 overview refs；未构建项目必须有 structured reason |
| 项目 docs ingest/readiness | V2.102 | Document Build Adapter | `project_build_runs.json` | planned | ingest accepted 时必须有 command/API result、source refs、query/source trace refs；readiness-only 时必须保持 non-accepted |
| Portfolio index | V2.102 | Portfolio Index Builder | `portfolio_index.json` | planned | accepted/non-accepted counts、project brief refs、project overview refs 或 structured gap、query entrypoints |
| 文档格式 readiness | V2.103 | Document Media Intake Probe | `source_candidate_matrix.json` | planned | real md/html/json/csv/pdf/pptx/docx/yaml rows、extractor status |
| 图片/OCR readiness | V2.103 | Media Probe | `media_readiness.json` | planned | image rows、OCR provider health、ocr_required 或 accepted OCR evidence |
| 扫描件/图片型资料阻断 | V2.103 | Media Probe | `media_readiness.json` | planned | structured unavailable reason，不得 accepted |
| 维护者首页状态面板 | V2.104 | Portfolio Status Header | headless screenshot refs | planned | release gate API result、project summary、visible non-accepted states |
| `/knowledge` portfolio panel | V2.104 | Knowledge Console Portfolio Panel | headless screenshot refs | planned | API read result、screenshot、panel text 与 artifact 一致性 |
| 项目详情体验 | V2.104 | Project Detail Drawer | headless screenshot refs | planned | code asset refs、project brief refs、docs/media readiness、context availability status 或结构化缺口 |
| 媒体 readiness 体验 | V2.104 | Media Readiness Panel | headless screenshot refs | planned | media readiness artifact、OCR/provider status visible |
| HTML portfolio report | V2.104 | Portfolio Report Renderer | `portfolio_report.html` | planned | report refs、path redaction、non-accepted visible |
| Release gate 聚合 | V2.105 | Portfolio Release Gate | `release_gate.json` | planned | phase statuses、`implementation_status`、`portfolio_final_status`、false-green audit、blocker summary |
| False-green audit | V2.105 | Portfolio Release Gate | `false_green_audit.md` | planned | OCR/UI/docs claim/scan-only false-green checks |

## 状态规则

- `planned`：文档规划完成，代码和证据尚未实现。
- `accepted`：真实资料、真实命令/API/MCP/UI 证据、artifact refs、PRD/spec review 和 false-green audit 全部具备。
- `needs_review`：缺人工判断、资料归属或高风险确认。
- `structured_unavailable`：路径、OCR、依赖或权限不可用，不是 accepted。
- `structured_blocker`：实现、依赖或环境阻断，不是 accepted。

任何 row 改为 `accepted` 前必须补齐：

- artifact path。
- focused test command and result。
- real workspace E2E result 或 structured unavailable rationale。
- PRD/spec review。
- false-green audit。
- acceptance audit report path。
