# V2.116-V2.120 Target Architecture：Real Evidence Acceptance Closure

## 1. 架构原则

- 复用 V2.111-V2.115 persisted artifacts，不静默改写上游事实。
- build/read/report 分离：build 生成 artifacts，read/report 只读取 artifacts。
- 外部 workspace 输入只读；所有输出写入 managed workspace。
- `accepted` 必须绑定真实命令、artifact refs、source refs、hash、focused tests、PRD/spec review 和 false-green audit。
- `needs_review`、`structured_unavailable`、`structured_blocker`、`failed` 不得计入 accepted。
- 不声明 full call graph、runtime topology、data/control flow 或 type inference。

## 2. 当前已实现实体

| 实体 | 状态 | 职责 |
| --- | --- | --- |
| `backend/data_service/workspace_portfolio/service.py` | 已实现 | workspace scan、classification、有界 build、media readiness、release gate |
| `backend/data_service/workspace_portfolio_final_evidence/service.py` | 已实现 | V2.106-V2.110 final evidence closure |
| `backend/data_service/workspace_portfolio_final_acceptance/service.py` | 已实现 | V2.111-V2.115 OCR/source/UI/build/final gate orchestration |
| `backend/data_service/cli_portfolio_final_acceptance.py` | 已实现 | `portfolio-final-acceptance plan/build/read/report` |
| `backend/data_service/mcp_workspace_portfolio_final_acceptance_tools.py` | 已实现 | MCP final acceptance tools |
| `backend/app/api/v1/workspace_portfolio_final_acceptance.py` | 已实现 | HTTP final acceptance routes |
| `frontend/src/pages/KnowledgePage.vue` | 已修改 | `/knowledge` final evidence panel |
| `v2_111_115_real/portfolio_final_acceptance/*` | 真实证据 | final gate 仍为 `structured_unavailable` |

## 3. 目标新增实体

| 目标实体 | 状态 | 建议落点 | 职责 |
| --- | --- | --- | --- |
| Real Evidence Acceptance Service | 待新增 | `workspace_portfolio_real_evidence_acceptance/service.py` | 编排 OCR、source trace、UI、safe build 和 final gate rerun |
| OCR Anchor Registry | 待新增 | `ocr_anchor.py` | 管理 OCR 候选文件、source ref、hash、anchor、人工说明和样本资格 |
| OCR Provider Runner | 待新增 | `ocr_provider.py` | 本地优先运行 OCR provider，记录依赖健康、命令、输出 hash、文本命中、失败分类 |
| Source Trace Batch Runner | 待新增 | `source_trace_batch.py` | 批量执行 import/query/source trace 验证，不把文件存在当 source trace |
| Headless UI Capture Runner | 待新增 | `ui_capture.py` | 捕获 `/knowledge` 或 HTML report 截图，失败时输出浏览器 blocker |
| Safe Build Allowlist Runner | 待新增 | `safe_build.py` | 生成 allowlist proposal；只有可信 approval 与 managed sandbox 同时存在时才执行命令 |
| Evidence Decision Registry | 待新增 | `decisions.py` | 读取 append-only decision set，记录 approved out_of_scope、anchor confirmation、build approval、revoke 和 reason |
| Final Portfolio Acceptance Gate | 待新增 | `release_gate.py` | 聚合所有证据，输出 accepted 或可信 non-accepted |
| Public Adapters | 待新增 | CLI/MCP/HTTP/UI adapters | 暴露 plan/build/read/report，不修改 legacy 大文件 |

## 4. 分层关系

| 层级 | 具体实体 | 交互 |
| --- | --- | --- |
| 用户入口层 | `/knowledge`、HTML report、CLI、MCP、HTTP | 发起真实证据闭环 plan/build/read/report，查看出门状态；本阶段 UI/HTML 只读 |
| Adapter 层 | CLI/MCP/HTTP/UI adapters | 参数校验、调用 service、返回统一 envelope |
| Orchestration 层 | Real Evidence Acceptance Service | 串联 OCR、source trace、UI、safe build 和 final gate |
| Execution 层 | OCR Provider、Source Trace Batch、Headless UI、Safe Build | 执行真实验收动作或结构化阻断 |
| Decision 层 | Evidence Decision Registry、Out-of-scope Approval | 读取独立 `decisions/{decision_set_id}.json`，校验有效期、撤销、scope 和 digest |
| Existing Capability 层 | workspace_portfolio、final_acceptance、source registry、query/source trace、code assets | 只读复用，不静默改写 |
| Persistence 层 | `workspace/{workspace_id}/portfolio_real_evidence_acceptance/*` | 持久化 artifacts、hash、refs、截图和报告 |
| Audit/Gate 层 | PRD/spec review、false-green audit、final gate | 判定 `portfolio_final_status` |

## 5. Artifact Layout

```text
workspace/{workspace_id}/portfolio_real_evidence_acceptance/
  latest.json
  decisions/{decision_set_id}.json
  runs/{run_id}/
    input_manifest.json
    ocr_anchor_registry.json
    ocr_provider_execution.json
    ocr_closure_report.md
    source_trace_batch_results.json
    source_trace_evidence_index.json
    source_trace_closure_report.md
    ui_capture_results.json
    ui_screenshot_manifest.json
    safe_build_allowlist.json
    safe_build_execution_results.json
    safe_build_governance_report.md
    evidence_decision_snapshot.json
    final_portfolio_acceptance_gate.json
    final_portfolio_false_green_audit.md
    final_portfolio_acceptance_report.html
    run_sandbox/{project_id}/
      readonly_input/
      working_copy_or_overlay/
      home/
      cache/
      tmp/
      output/
      logs/
```

Run lineage、staleness、atomic write、lineage-bound cross-run validation、decision lifecycle 和 sandbox 以 schema、status 和 safe-build spec 为准。

## 6. Public Surface 计划

CLI：

```text
python -m data_service portfolio-real-evidence plan --workspace-id ...
python -m data_service portfolio-real-evidence build --workspace-id ...
python -m data_service portfolio-real-evidence read --workspace-id ...
python -m data_service portfolio-real-evidence report --workspace-id ...
```

MCP：

```text
knowledge_workspace_portfolio_real_evidence_plan
knowledge_workspace_portfolio_real_evidence_build
knowledge_workspace_portfolio_real_evidence_read
knowledge_workspace_portfolio_real_evidence_report
```

HTTP：

```text
POST /api/workspaces/{workspace_id}/portfolio-real-evidence/plan
POST /api/workspaces/{workspace_id}/portfolio-real-evidence/build
GET  /api/workspaces/{workspace_id}/portfolio-real-evidence
GET  /api/workspaces/{workspace_id}/portfolio-real-evidence/report
```

CLI/MCP/HTTP/UI 的精确注册点以 `V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_PUBLIC_SURFACE_REGISTRATION_AND_UPSTREAM_COMPATIBILITY_SPEC.md` 为准。

本阶段不提供 UI/HTTP/MCP 的 anchor 或 decision 写接口；`/knowledge` 和 HTML report 只读展示证据、阻断、next action 和 decision state。

## 7. ADR：继续采用模块化单体扩展

Status: Accepted for planning.

Context:

本阶段需要强一致读取 managed workspace、V2.111-V2.115 artifacts、source registry、query/source trace、UI report 和 build queue。拆成独立服务会增加部署、权限、artifact lineage 和回放复杂度。

Decision:

在 data_service modular monolith 内新增独立 `workspace_portfolio_real_evidence_acceptance` 包，并沿用现有 CLI/MCP/HTTP/UI adapter 模式。

Consequences:

- 更容易复用现有 artifact、workspace runtime 和 public surface guard。
- 需要保持清晰包边界，避免逻辑堆回 legacy 大文件。
- Safe build 真执行前必须先实现 managed sandbox；否则只能输出 proposal 和 `structured_blocker`。

## 8. No-Go 设计

- OCR provider readiness 不得替代 OCR anchor 和 OCR output。
- PPT/PDF 直接文本抽取不得替代 OCR accepted。
- Source file existence 不得替代 import/query/source trace chain。
- HTML report 不得替代 UI screenshot 或 structured browser blocker。
- 未批准 build 命令不得执行。
- 有界 build 不得冒充全量 build accepted。
- Final gate 不得隐藏 blocker 或把 unavailable 计入 accepted。
- Final gate 不得使用未在 `source_run_refs[]` 声明、lineage/hash 不匹配或 stale 的跨 run 输入。
- 程序不得自行生成 build approval、human confirmation 或 approved out_of_scope。
- Safe build 在缺可信 approval 前不得执行真实外部项目命令。
- Safe build 在缺 managed sandbox 前不得执行真实外部项目命令。
- UI 不得直接修改 persisted artifacts 或生成 approved decision。

## 9. OCR Provider 技术路线

默认路线采用本地 provider，不使用云 OCR 作为首发默认路径。

| 输入类型 | 默认处理 | 依赖 | accepted 前置条件 |
| --- | --- | --- | --- |
| 图片：png/jpg/jpeg/webp/bmp/tif/tiff | 直接调用 Tesseract OCR | `tesseract`、语言包 `chi_sim`/`eng` | source ref、sha256、anchor、OCR text、output hash、anchor hit |
| 扫描 PDF | `pdftoppm` 或等价 Poppler 工具转图片，再 OCR | `poppler-utils`、`tesseract` | PDF source hash、页图 hash、anchor、OCR output |
| 图片型 PPTX | `soffice`/LibreOffice 转 PDF 或图片，再进入 OCR | `libreoffice`/`soffice`、Poppler、Tesseract | 转换 artifact、source hash、anchor、OCR output |
| 直接文本 PDF/PPTX/DOCX | 文本抽取只能作为 source candidate evidence | `pypdf` 或 office parser | 不得替代 OCR accepted |

首发不默认使用：

- PaddleOCR / EasyOCR：依赖重，作为后续 provider adapter。
- 云 OCR：涉及网络、费用、密钥和资料外发，默认不启用。
- 自动安装依赖：本阶段只检测依赖和结构化阻断，不自动安装系统包。

OCR accepted 必须同时满足：

1. 真实文件存在且有 `sha256`。
2. 有人类提供或确认的 `ocr_anchor`，例如 `scan.png.ocr-anchor.txt`。
3. Provider health 为可用。
4. Provider execution 真实运行并产生 `output_ref` 和 `output_hash`。
5. OCR 输出命中 anchor，或记录明确人工确认。
6. Public artifact 不暴露本机绝对私有路径、secret、token、raw traceback。

缺任一项时，状态只能是 `needs_review`、`structured_unavailable` 或 `structured_blocker`。
