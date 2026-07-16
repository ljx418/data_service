# V2.101-V2.105 Full Coverage Matrix

## 1. Implementation Closure Status

本矩阵已按 `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_ACCEPTANCE_AUDIT_REPORT.md` 回填实现后状态。

可以声明：

- `implementation_status=accepted`
- V2.101-V2.105 文档完整支撑范围内的 workspace scan、project classification、有界 project build、document/media readiness、`/knowledge` portfolio panel、release gate 与 false-green audit 已实现。

不可以声明：

- `portfolio_final_status=accepted`
- workspace 内全部项目已经完成深度理解。
- OCR 缺失的图片、扫描 PDF、图片型 PPT 已被理解。
- 全量 document ingest/query/source trace 已覆盖所有 source candidates。
- headless screenshot evidence 已 accepted。

## 2. Coverage Rows

| 能力 | 阶段 | 目标实体 | Planned artifact | 当前状态 | Required evidence / 当前证据 |
| --- | --- | --- | --- | --- | --- |
| Workspace 一级目录发现 | V2.101 | Workspace Portfolio Scanner | `project_registry.json` | accepted | 真实 `/mnt/c/workspace` scan；18 个项目/目录、9 个 ignored；见 acceptance audit 与 `cli_e2e_summary.json` |
| 项目分类证据 | V2.101 | Project Classifier | `project_registry.json` | accepted | 分类统计：media_corpus 4、code_project 11、needs_review 2、doc_project 1；分类证据来自真实目录信号 |
| 忽略/不可用记录 | V2.101 | Discovery Auditor | `project_registry.json` / release unresolved | accepted | ignored reason、needs_review reason、next action 已保留；未静默忽略 |
| 代码项目 build 编排 | V2.102 | Project Build Orchestrator | `project_build_runs.json` | accepted for bounded implementation | 1 个真实代码项目 accepted；17 个项目保留 `needs_review`；不得声明全量深度建库 |
| 项目 docs ingest/readiness | V2.102 | Document Build Adapter | `project_build_runs.json` | needs_review | readiness 已实现；全量 ingest/query/source trace 未完成，不可 accepted |
| Portfolio index | V2.102 | Portfolio Index Builder | `portfolio_index.json` | accepted for bounded implementation | accepted/non-accepted counts、project brief refs、structured gaps 已输出；final portfolio 非 accepted |
| 文档格式 readiness | V2.103 | Document Media Intake Probe | `source_candidate_matrix.json` | accepted for readiness | 真实 source candidates 被枚举；仅 readiness accepted，不代表全部 ingest accepted |
| 图片/OCR readiness | V2.103 | Media Probe | `media_readiness.json` | structured_unavailable | `ocr_required_count=86`；OCR provider 缺失；不得 accepted |
| 扫描件/图片型资料阻断 | V2.103 | Media Probe | `media_readiness.json` | structured_unavailable | 图片/扫描件保留 structured unavailable reason 与 next action |
| 维护者首页状态面板 | V2.104 | Portfolio Status Header | API/HTML evidence | accepted for implementation | `/knowledge?view=portfolio` HTTP 200；状态来自 read model；headless screenshot 不可用 |
| `/knowledge` portfolio panel | V2.104 | Knowledge Console Portfolio Panel | API/HTML evidence | accepted for implementation | API read result 与 panel 绑定；截图因 `libnspr4.so` 缺失为 `structured_unavailable` |
| 项目详情体验 | V2.104 | Project Detail Drawer | read model | accepted for implementation | 展示 code asset refs、project brief refs、docs/media readiness 与结构化缺口；截图未 accepted |
| 媒体 readiness 体验 | V2.104 | Media Readiness Panel | read model | accepted for implementation | OCR/provider status 可见；OCR 内容级解析仍 `structured_unavailable` |
| HTML portfolio report | V2.104 | Portfolio Report Renderer | `portfolio_report.html` / visual acceptance HTML | accepted | 中文报告可读、non-accepted 状态可见、路径脱敏检查通过 |
| Release gate 聚合 | V2.105 | Portfolio Release Gate | `release_gate.json` | accepted for implementation | 输出 `implementation_status=accepted` 与 `portfolio_final_status=structured_unavailable` |
| False-green audit | V2.105 | Portfolio Release Gate | `false_green_audit.md` / acceptance audit | accepted | scan-only、UI-only、OCR、docs claim、silent skip 风险均被拒绝 |

## 3. 状态规则

- `planned`：文档规划完成，代码和证据尚未实现。
- `accepted`：真实资料、真实命令/API/MCP/UI 证据、artifact refs、PRD/spec review 和 false-green audit 全部具备。
- `accepted for bounded implementation`：实现路径、focused tests 和真实 E2E 通过，但不能声明全量内容级完成。
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

## 4. Handoff to V2.106-V2.110

下一阶段必须优先处理：

1. 文档状态与目标架构状态持续回填，避免已实现实体仍显示为 planned。
2. OCR/provider 和多媒体 evidence closure。
3. 多项目 full build governance，避免 silent skip。
4. 全量 document ingest/query/source trace closure。
5. Portfolio final release gate，只有所有高风险项 accepted 或被明确结构化阻断时才允许 final accepted。
