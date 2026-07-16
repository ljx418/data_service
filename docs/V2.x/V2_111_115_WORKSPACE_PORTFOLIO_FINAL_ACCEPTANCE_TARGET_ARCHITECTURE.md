# V2.111-V2.115 Target Architecture：Workspace Portfolio Final Acceptance Closure

## 1. 架构原则

- 复用 V2.106-V2.110 persisted artifacts，不重写上游事实。
- build/read/report 分离：build 生成 artifacts，read/report 只读取 artifacts。
- 外部 workspace 输入只读；所有输出写入 managed workspace。
- `accepted` 必须绑定真实命令、artifact refs、source refs、PRD/spec review 和 false-green audit。
- `needs_review`、`structured_unavailable`、`structured_blocker` 不得计入 accepted。
- 不声明 full call graph、runtime topology、data/control flow 或 type inference。

## 2. 当前已实现实体

| 实体 | 状态 | 职责 |
| --- | --- | --- |
| `backend/data_service/workspace_portfolio/service.py` | 已实现 | workspace scan、classification、有界 build、media readiness、release gate |
| `backend/data_service/workspace_portfolio_final_evidence/service.py` | 已实现 | V2.106-V2.110 baseline、coverage、architecture、media、queue、source trace、UI、final gate |
| `backend/data_service/workspace_portfolio_final_evidence/shared.py` | 已实现 | status algebra、run id、artifact refs、base artifact |
| `backend/data_service/workspace_portfolio_final_evidence/persistence.py` | 已实现 | `portfolio_final_evidence/*` 持久化 |
| `backend/data_service/cli_portfolio_final_evidence.py` | 已实现 | `portfolio-final-evidence plan/build/read/report` |
| `backend/data_service/mcp_workspace_portfolio_final_evidence_tools.py` | 已实现 | MCP plan/build/read/report |
| `backend/app/api/v1/workspace_portfolio_final_evidence.py` | 已实现 | HTTP plan/build/read/report |
| `frontend/src/pages/KnowledgePage.vue` | 已修改 | `/knowledge` final evidence panel |
| `v2_106_110_real/portfolio_final_evidence/*` | 真实证据 | 当前 final gate：`structured_unavailable` |

## 3. 目标新增实体

| 目标实体 | 状态 | 建议落点 | 职责 |
| --- | --- | --- | --- |
| Media Execution Provider | 待新增 | `workspace_portfolio_final_acceptance/media_execution.py` | 先确认 OCR 真实样本资格，再执行 OCR、PDF/PPT/text conversion，记录 provider、命令、输出 hash、失败分类 |
| Source Trace Closure Runner | 待新增 | `workspace_portfolio_final_acceptance/source_trace.py` | 对 accepted 文档执行 source import、query、source trace 验证 |
| Headless UI Evidence Runner | 待新增 | `workspace_portfolio_final_acceptance/ui_evidence.py` | 无焦点抢占截图 `/knowledge` panel，失败时输出浏览器依赖诊断 |
| Safe Project Build Runtime | 待新增 | `workspace_portfolio_final_acceptance/build_runtime.py` | allowlist、timeout、cache、独立 output/cache、日志截断、retry/resume |
| Final Acceptance Rerun Gate | 待新增 | `workspace_portfolio_final_acceptance/release_gate.py` | 聚合 V2.111-V2.114 artifacts，输出 final accepted 或 non-accepted reason |
| Final Acceptance Public Adapter | 待新增 | CLI/MCP/HTTP/UI adapters | 暴露 plan/build/read/report，不修改 legacy 大文件 |

## 4. 分层关系

| 层级 | 具体实体 | 交互 |
| --- | --- | --- |
| 用户入口层 | `/knowledge`、HTML report、CLI、MCP、HTTP | 发起 final acceptance build/read/report，查看出门状态 |
| Adapter 层 | CLI/MCP/HTTP/UI evidence runner | 参数校验、调用 service、返回统一 envelope |
| Orchestration 层 | Final Acceptance Service | 编排 OCR、source trace、UI、safe build runtime 和 release gate |
| Execution Adapter 层 | Media Execution、Source Trace、Headless UI、Safe Build Runtime | 执行真实验收动作或结构化阻断 |
| Existing Capability 层 | workspace_portfolio、workspace_portfolio_final_evidence、source registry、query/source trace、code assets | 只读复用，不静默改写 |
| Persistence 层 | `workspace/{workspace_id}/portfolio_final_acceptance/*` | 持久化 final acceptance artifacts |
| Audit/Gate 层 | PRD/spec review、false-green audit、final acceptance gate | 判定 `portfolio_final_status` |

## 5. Artifact Layout

```text
workspace/{workspace_id}/portfolio_final_acceptance/
  media_execution_results.json
  ocr_sample_qualification.json
  media_artifact_manifest.json
  source_trace_execution.json
  source_trace_audit.json
  ui_evidence_capture.json
  ui_screenshot_manifest.json
  safe_build_queue.json
  safe_build_execution.json
  build_runtime_diagnosis.json
  final_acceptance_gate.json
  final_acceptance_false_green_audit.md
  final_acceptance_report.html
```

## 6. Public Surface 计划

CLI：

```text
python -m data_service portfolio-final-acceptance plan --workspace-id ...
python -m data_service portfolio-final-acceptance build --workspace-id ...
python -m data_service portfolio-final-acceptance read --workspace-id ...
python -m data_service portfolio-final-acceptance report --workspace-id ...
```

MCP：

```text
knowledge_workspace_portfolio_final_acceptance_plan
knowledge_workspace_portfolio_final_acceptance_build
knowledge_workspace_portfolio_final_acceptance_read
knowledge_workspace_portfolio_final_acceptance_report
```

HTTP：

```text
POST /api/workspaces/{workspace_id}/portfolio-final-acceptance/plan
POST /api/workspaces/{workspace_id}/portfolio-final-acceptance/build
GET  /api/workspaces/{workspace_id}/portfolio-final-acceptance
GET  /api/workspaces/{workspace_id}/portfolio-final-acceptance/report
```

## 7. ADR：继续采用模块化单体扩展

Status: Accepted for planning.

Context:

Final acceptance 需要同时读取 managed workspace、portfolio artifacts、source registry、query/source trace、code assets 和 UI artifacts。拆成独立服务会增加部署、权限、artifact lineage 和回放复杂度。

Decision:

在 data_service modular monolith 内新增独立 `workspace_portfolio_final_acceptance` 包，并通过现有 CLI/MCP/HTTP/UI adapter 模式暴露能力。

Consequences:

- 更容易复用现有 artifact 与 workspace runtime。
- 需要继续维护清晰包边界，避免逻辑堆回 legacy 大文件。
- 如果未来需要独立 sandbox worker，可只迁移 `build_runtime.py` 执行层。

## 8. No-Go 设计

- OCR/provider 缺失时 media row 不得 accepted。
- OCR accepted 必须引用真实可 OCR 样本资格和 OCR 输出证据；PPT/PDF 直接文本抽取不得替代 OCR accepted。
- source import/query/source trace 任一缺失时 document row 不得 accepted。
- UI HTML report 不得替代真实 screenshot 或 structured browser blocker。
- 有界 build 不得冒充全量 build accepted。
- 未批准命令不得执行；外部项目 build script 不得默认运行。
- final gate 不得隐藏 blocker 或把 unavailable 计入 accepted。
