# V2.106-V2.110 Target Architecture：Workspace Portfolio Final Evidence Closure

## 1. 架构原则

- 只读扫描 `/mnt/c/workspace`，不写入被扫描项目目录。
- build/read/report 分离：build 生成 persisted artifacts，read/report 只读取 artifacts。
- 所有 public output 必须包含 `schema_version`、`workspace_id`、`status`、`artifact_refs`、`evidence_refs`、`warnings`、`unresolved`、`next_actions`。
- `accepted` 必须绑定真实命令、artifact refs、PRD/spec review 和 false-green audit。
- `needs_review`、`structured_unavailable`、`structured_blocker` 不得计入 accepted。
- 不声明 full call graph、runtime topology、data/control flow 或 type inference。

## 2. 当前已实现实体

| 实体 | 状态 | 职责 |
| --- | --- | --- |
| `backend/data_service/workspace_portfolio/service.py` | 已实现 | workspace scan、classification、有界 build、media readiness、release gate、report |
| `backend/data_service/workspace_portfolio/persistence.py` | 已实现 | portfolio artifacts 持久化 |
| `backend/data_service/workspace_portfolio/shared.py` | 已实现 | envelope、status、artifact ref、unresolved helper |
| `backend/data_service/cli_portfolio.py` | 已实现 | portfolio scan/build/read/report CLI |
| `backend/data_service/mcp_workspace_portfolio_tools.py` | 已实现 | MCP scan/build/read/report tools |
| `backend/app/api/v1/workspace_portfolio.py` | 已实现 | HTTP scan/build/read/report route |
| `frontend/src/pages/KnowledgePage.vue` | 已修改 | `/knowledge` portfolio panel |
| `docs/V2.x/V2_101_105_*` | 已实现文档与验收 | V2.101-V2.105 文档、验收报告、HTML report、drawio |

## 3. 目标新增/需修改实体

| 目标实体 | 状态 | 职责 |
| --- | --- | --- |
| Coverage Closure Auditor | 待新增 | 回填 coverage matrix、目标架构状态、drawio 状态和证据路径 |
| OCR Evidence Adapter | 待新增 | 检测 OCR/provider 可用性、记录 media row evidence 或 structured unavailable |
| Media Evidence Classifier | 待新增 | 分类图片、扫描 PDF、图片型 PPT、可抽取文本资料和 unsupported rows |
| Full Build Scheduler | 待新增 | 多项目 build queue、cache、timeout、failure isolation、incremental rerun |
| Project Build Diagnosis | 待新增 | 对每个失败/跳过项目输出 category、reason、next action |
| Source Trace Closure Adapter | 待新增 | 将 accepted document ingest 绑定 query result 和 source trace refs |
| UI Evidence Capture Adapter | 待新增 | Headless screenshot 或 structured unavailable 证据，不抢占焦点 |
| Final Portfolio Release Gate | 需增强 | 聚合项目、媒体、文档、UI、MCP/CLI/HTTP、false-green audit |

## 4. 分层关系

| 层级 | 具体实体 | 交互 |
| --- | --- | --- |
| 用户入口层 | `/knowledge`、HTML report、CLI、MCP、HTTP | 发起 closure build/read/report，查看 final gate |
| Adapter 层 | CLI/MCP/HTTP/UI evidence capture | 参数校验、调用 service、返回统一 envelope |
| Closure Service 层 | Coverage Auditor、OCR Adapter、Build Scheduler、Source Trace Adapter、Release Gate | 生成 evidence closure artifacts |
| Existing Capability 层 | workspace_portfolio、code_assets、DataService ingest/query/source trace、extractors、OCR provider | 被编排复用，不改写原有 contract |
| Persistence 层 | `workspace/{workspace_id}/portfolio_final_evidence/*` | 持久化 closure artifacts |
| Audit/Gate 层 | false-green audit、PRD/spec review、final release gate | 决定 `portfolio_final_status` |

## 5. 建议 Artifact Layout

```text
workspace/{workspace_id}/portfolio_final_evidence/
  coverage_state_closure.json
  architecture_state_closure.json
  ocr_provider_health.json
  media_evidence_matrix.json
  full_build_queue.json
  project_build_diagnosis.json
  document_source_trace_closure.json
  ui_evidence_capture.json
  final_release_gate.json
  false_green_recheck.md
  final_evidence_report.html
```

## 6. Public Surface 计划

CLI：

```text
python -m data_service portfolio-final-evidence plan --workspace-id ...
python -m data_service portfolio-final-evidence build --workspace-id ...
python -m data_service portfolio-final-evidence read --workspace-id ...
python -m data_service portfolio-final-evidence report --workspace-id ...
```

MCP：

```text
knowledge_workspace_portfolio_final_evidence_plan
knowledge_workspace_portfolio_final_evidence_build
knowledge_workspace_portfolio_final_evidence_read
knowledge_workspace_portfolio_final_evidence_report
```

HTTP：

```text
POST /api/workspaces/{workspace_id}/portfolio-final-evidence/plan
POST /api/workspaces/{workspace_id}/portfolio-final-evidence/build
GET  /api/workspaces/{workspace_id}/portfolio-final-evidence
GET  /api/workspaces/{workspace_id}/portfolio-final-evidence/report
```

## 7. No-Go 设计

- 不允许 OCR/provider 缺失时把 media row 写成 accepted。
- 不允许未构建项目因为超时或跳过而 accepted。
- 不允许 document readiness 替代 ingest/query/source trace accepted。
- 不允许 UI screenshot 或 HTML report 替代 build evidence。
- 不允许 docs claim 进入 code fact。
- 不允许 final release gate 隐藏 blocker。

## 8. P0 Detailed Architecture Contracts

The logical architecture above is implemented only together with these detailed contracts:

- Artifact schema and stable ID contracts.
- Status algebra and final gate decision table.
- Build execution security and runtime spec.
- Run lineage, persistence and staleness spec.
- Public surface interface contract.
- Prototype UX spec.

Build execution must use read-only external inputs and external output/cache locations. If safe runtime controls cannot be enforced, affected jobs must be `structured_blocker` or `structured_unavailable`.
