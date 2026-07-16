# V2.116-V2.120 Public Surface Registration and Upstream Compatibility Spec

## 1. 目的

冻结 CLI、MCP、HTTP、UI 注册点，避免实现阶段临场猜测，也避免默认修改 protected legacy files。

## 2. CLI Registration Contract

现有模式：

- Parser 构建：`backend/data_service/__main__.py::_build_parser`
- 子命令注册：`add_portfolio_parser`、`add_portfolio_final_evidence_parser`、`add_portfolio_final_acceptance_parser`
- 命令分发：`_run_parsed_args`

V2.116-V2.120 计划：

```text
backend/data_service/cli_portfolio_real_evidence.py
  add_portfolio_real_evidence_parser(subparsers)
  run_portfolio_real_evidence_command(args)
```

需要注册到：

```text
backend/data_service/__main__.py
  import add_portfolio_real_evidence_parser, run_portfolio_real_evidence_command
  _build_parser(): add_portfolio_real_evidence_parser(subparsers)
  _run_parsed_args(): if args.command == "portfolio-real-evidence": ...
```

风险：

- 该文件不是 protected legacy file，但属于 central CLI parser。实现必须由 public surface guard 覆盖。

## 3. MCP Registration Contract

现有模式：

- Tool specs 聚合：`backend/data_service/mcp_tool_registry.py::all_tool_specs`
- Dispatcher 分发：`backend/data_service/mcp_dispatcher.py::MCPToolDispatcher.call_tool`
- 专用 handler 文件：`mcp_workspace_portfolio_final_acceptance_tools.py`

V2.116-V2.120 计划：

```text
backend/data_service/mcp_workspace_portfolio_real_evidence_tools.py
  WORKSPACE_PORTFOLIO_REAL_EVIDENCE_TOOL_NAMES
  WORKSPACE_PORTFOLIO_REAL_EVIDENCE_TOOL_SPECS
  handle_workspace_portfolio_real_evidence_tool(...)
```

需要注册到：

```text
mcp_tool_registry.py
  import WORKSPACE_PORTFOLIO_REAL_EVIDENCE_TOOL_SPECS
  all_tool_specs(): include specs

mcp_dispatcher.py
  import WORKSPACE_PORTFOLIO_REAL_EVIDENCE_TOOL_NAMES
  import handle_workspace_portfolio_real_evidence_tool
  call_tool(): route matching tool names
```

Planned tools：

```text
knowledge_workspace_portfolio_real_evidence_plan
knowledge_workspace_portfolio_real_evidence_build
knowledge_workspace_portfolio_real_evidence_read
knowledge_workspace_portfolio_real_evidence_report
```

本阶段 MCP 不提供 anchor/decision 写工具。高风险审批、revoke 和 approved out-of-scope 通过独立 decision bundle 或未来阶段专用 write surface 处理。

## 4. HTTP Registration Contract

现有模式：

- Router include 点：`backend/app/api/__init__.py`
- V1 route 文件：`backend/app/api/v1/workspace_portfolio_final_acceptance.py`

V2.116-V2.120 计划：

```text
backend/app/api/v1/workspace_portfolio_real_evidence.py
  router = APIRouter(prefix="/workspaces", ...)
```

需要注册到：

```text
backend/app/api/__init__.py
  from .v1.workspace_portfolio_real_evidence import router as workspace_portfolio_real_evidence_target_router
  api_router.include_router(workspace_portfolio_real_evidence_target_router)
```

Routes：

```text
POST /api/workspaces/{workspace_id}/portfolio-real-evidence/plan
POST /api/workspaces/{workspace_id}/portfolio-real-evidence/build
GET  /api/workspaces/{workspace_id}/portfolio-real-evidence
GET  /api/workspaces/{workspace_id}/portfolio-real-evidence/report
```

本阶段 HTTP 不提供以下写接口：

```text
POST /portfolio-real-evidence/anchors
POST /portfolio-real-evidence/decisions
POST /portfolio-real-evidence/decisions/{decision_id}/revoke
```

如果后续选择交互式 UI，必须先补充 PRD、身份来源、权限、CSRF/审计、MCP/CLI parity 和 false-green 规则。

## 5. UI Registration Contract

现有风险：

- `frontend/src/pages/KnowledgePage.vue` 已较大，继续堆叠会提高维护风险。

计划：

- API client：`frontend/src/api/dataService.ts`
- UI component 目录建议：

```text
frontend/src/components/portfolioRealEvidence/
  PortfolioRealEvidencePanel.vue
  OcrEvidenceTable.vue
  SourceTraceEvidenceTable.vue
  UiCaptureEvidencePanel.vue
  SafeBuildApprovalTable.vue
  FinalGateSummary.vue
  DecisionRegistryPanel.vue
  FalseGreenAuditPanel.vue
  ArtifactLinksPanel.vue
```

`KnowledgePage.vue` 只负责挂载新 panel，不直接承载全部表格和交互逻辑。`PortfolioRealEvidencePanel` 只读展示 persisted artifacts，不直接写 artifact、不创建 approval、不执行 revoke。

## 6. Upstream Artifact Compatibility

V2.116-V2.120 输入必须兼容：

```text
v2_111_115_real/portfolio_final_acceptance/
  final_acceptance_gate.json
  ocr_sample_qualification.json
  media_execution_results.json
  source_trace_execution.json
  ui_evidence_capture.json
  safe_build_execution.json
```

实现必须：

- 读取上游 artifact hash 写入 `input_manifest.json`。
- 缺字段时输出 `structured_unavailable`，不得静默补造 accepted。
- 不修改 V2.111-V2.115 artifact。
