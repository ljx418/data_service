# V2.81-V2.85 Target Architecture：真实文档资料验收与发布闭环

## 1. 架构原则

- 只读引用 V2.76-V2.80 persisted artifacts 和审计报告，不静默改写上游证据。
- 真实资料验收必须通过现有 workspace、source、session、query、GraphRAG、Source trace、quality governance 能力完成。
- accepted 必须来自真实资料、真实操作、真实截图、真实 artifact 或真实 API/CLI/MCP 结果。
- `needs_review`、`structured_unavailable`、`structured_blocker` 必须被报告、证据索引和 release gate 保留。
- 不修改 protected legacy 文件，除非用户明确批准。

## 2. 当前架构基线

| 实体 | 状态 | 职责 |
| --- | --- | --- |
| `frontend/src/pages/KnowledgePage.vue` | 已实现 | 知识运营台主交互，承载 workspace、source、query、GraphRAG、quality 等体验 |
| `backend/app/main.py` | 已实现 | FastAPI app，托管 `/knowledge` 控制台和 `/api` 路由 |
| `backend/app/api/v1/data_service.py` | 已实现 / 受保护 | legacy HTTP 边界，当前仅引用，不默认修改 |
| `backend/app/api/v1/code_assets_project_acceptance_hardening.py` | 已实现 | V2.76-V2.80 验收硬化 HTTP surface |
| `backend/data_service/code_assets/project_acceptance_hardening/` | 已实现 | matrix、external binding、warning、console、release readiness |
| `docs/V2.x/V2_76_80_*` | 已实现证据 | 自动化验收、真实 E2E、视觉证据、人工验收 needs_review 状态 |

## 3. 目标补验分层

本阶段文档目标不直接实现新代码。后续如进入实现，候选新增 package 必须独立：

```text
backend/data_service/code_assets/real_document_acceptance/
  shared.py
  sample_contract.py
  real_document_e2e.py
  retrieval_trace.py
  quality_acceptance.py
  release_closure.py
```

候选 adapter 必须独立：

```text
backend/data_service/mcp_code_real_document_acceptance_tools.py
backend/data_service/cli_code_real_document_acceptance.py
backend/app/api/v1/code_assets_real_document_acceptance.py
```

禁止默认修改：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 4. 目标架构实体

### 4.1 Real Document Sample Contract

输入：

- 真实资料类型；
- 脱敏说明；
- 导入方式；
- 期望覆盖能力；
- 人工验收截图标准。

输出：

- `real_document_acceptance/sample_contract.json`
- `real_document_acceptance/manual_scenario_plan.md`

规则：

- 未提供真实资料时为 `needs_review`。
- 真实资料不能含 secret、token、private path 或 raw traceback。
- mock-only sample 不能 accepted。

### 4.2 Real Document E2E Runner

输入：

- workspace；
- source import paths；
- build/session commands；
- Wiki artifact 和 distill artifact。

输出：

- `real_document_acceptance/import_run.json`
- `real_document_acceptance/wiki_artifact_review.json`
- `real_document_acceptance/real_document_e2e_report.md`

规则：

- 导入失败必须保留失败原因。
- 解析弱、空内容或格式不支持必须进入 `needs_review` 或 `structured_blocker`。
- 真实资料导入 accepted 必须有 artifact refs 和截图证据。

### 4.3 Retrieval, GraphRAG and Source Trace Reviewer

输入：

- query text；
- GraphRAG result；
- source trace result；
- evidence spans / units。

输出：

- `real_document_acceptance/query_trace_review.json`
- `real_document_acceptance/graphrag_review.json`
- `real_document_acceptance/source_trace_review.md`

规则：

- 检索结果不能声称完整语义理解。
- GraphRAG 不能写成 full runtime topology。
- Source trace 缺失时不能 accepted。

### 4.4 Quality Governance Acceptance Reviewer

输入：

- low signal audit；
- quality feedback；
- correction plan；
- correction rules / review records。

输出：

- `real_document_acceptance/quality_governance_review.json`
- `real_document_acceptance/correction_acceptance_report.md`

规则：

- 质量问题不能被截图或 HTML 隐藏。
- 自动纠错建议必须有 evidence 或 `needs_review`。
- 人工审批缺失时不能 accepted。

### 4.5 Release Closure Rerun

输入：

- V2.76-V2.80 real E2E evidence；
- 本阶段真实资料补验结果；
- 外部项目路径状态；
- human approval。

输出：

- `real_document_acceptance/release_closure_rerun.json`
- `real_document_acceptance/final_manual_acceptance_report.md`

规则：

- 最终 release accepted 需要真实资料人工验收、外部项目状态、warning gate、restore/smoke 和 human approval。
- 任一高风险项缺失时保持 `needs_review` 或 `structured_unavailable`。

## 5. Public Surface 规划

本阶段是文档开发，不新增 public surface。后续进入实现时，计划 surface 为：

```text
MCP: knowledge_code_real_document_acceptance_*_build/read
CLI: python -m data_service code real-document-acceptance <capability> build/read
HTTP: /api/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/*
```

## 6. 禁止的架构设计

- 用截图替代真实资料导入和 Source trace。
- 用 mock-only document 替代真实资料验收。
- 把思维导图方向 OK 写成真实资料体验 accepted。
- 把 GraphRAG 输出写成 full call graph 或 runtime topology。
- 绕过 human approval 或外部项目路径状态。
- 修改 protected legacy 文件注册本阶段能力。
