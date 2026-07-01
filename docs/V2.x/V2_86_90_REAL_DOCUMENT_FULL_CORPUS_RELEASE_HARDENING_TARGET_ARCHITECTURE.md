# V2.86-V2.90 Target Architecture：全量真实文档验收与发布闭环加固

## 1. 架构原则

- 只读引用 V2.76-V2.85 persisted artifacts 和审计报告，不静默改写上游证据。
- 全量真实文档验收必须通过真实 workspace、source、session、query、GraphRAG、Source trace、quality governance 或等价公开接口完成。
- accepted 必须绑定真实资料、真实执行结果、真实截图、artifact refs、API/CLI/MCP 结果或人工签核证据。
- `needs_review`、`structured_unavailable`、`structured_blocker` 必须在报告、面板和 release gate 中保留。
- 不把文档描述当作代码事实，不扩大为 full call graph、runtime topology、data/control flow、type inference 或完整设计意图恢复。

## 2. 当前架构基线

| 实体 | 状态 | 职责 |
| --- | --- | --- |
| `backend/data_service/code_assets/real_document_acceptance/service.py` | 已实现 | V2.81-V2.85 真实文档验收 service，生成样本合同、真实 E2E、检索追踪、质量治理、发布闭环 artifact |
| `backend/data_service/code_assets/real_document_acceptance/persistence.py` | 已实现 | 读写 `real_document_acceptance/*` persisted artifacts |
| `backend/data_service/code_assets/real_document_acceptance/shared.py` | 已实现 | schema 基础字段、状态聚合、redaction 检查、unresolved item |
| `backend/app/api/v1/code_assets_real_document_acceptance.py` | 已实现 | V2.81-V2.85 HTTP build/read surface |
| `backend/data_service/cli_code_real_document_acceptance.py` | 已实现 | V2.81-V2.85 CLI command 到 tool 的映射 |
| `backend/data_service/mcp_code_real_document_acceptance_tools.py` | 已实现 | V2.81-V2.85 MCP tool specs 和 handler |
| `backend/app/static/knowledge_console/*` | 已实现但有本地重建变更 | 维护者知识控制台静态前端 |
| `docs/V2.x/V2_81_85_*` | 已实现文档证据 | Route B accepted、V2.84 needs_review、V2.85 structured_unavailable |
| `workspace/*` | 运行时数据 | workspace、source、build、query、graph、artifact 存放位置 |

## 3. 目标补强分层

| 层级 | 当前能力 | V2.86-V2.90 目标 |
| --- | --- | --- |
| 资料入口 | Route B 仓内真实文档小样本可验收 | 增加全量 `docs/V2.x` 验收和 Route A 用户代表性资料合同 |
| 解析构建 | 小样本构建 accepted | 修复或结构化阻断 HTML extractor `Section` 错误，保留失败分类 |
| 体验链路 | Wiki、检索、GraphRAG、Source trace 可验收 | 全量资料和 Route A 资料均有可追溯体验路径 |
| 质量治理 | 自动产物存在但人工审查缺失 | 增加人工质量审查记录、纠错建议确认和 rule effect 证据 |
| 外部项目 | `codexPat`、`HarnessOS`、`Navia` 缺路径 | 路径可用则真实 E2E，不可用则 structured unavailable |
| 出门判断 | Final release 不能 accepted | release gate 聚合真实资料、外部项目、approval、restore、dependency hygiene |

## 4. 目标架构实体

### 4.1 Full Corpus E2E Runner

候选落点：

- `backend/data_service/code_assets/real_document_full_corpus_release/full_corpus.py`
- 复用 `RealDocumentAcceptanceService`、workspace runtime、source import、query/graph/source trace 能力。

职责：

- 以 `docs/V2.x` 为真实资料源执行全量导入和构建。
- 识别 Markdown、HTML、JSON、drawio 等资料类型。
- 对 HTML extractor 失败输出 failure category，不隐藏异常。
- 产出 `full_corpus_e2e/full_corpus_run.json`、`full_corpus_e2e/parser_failures.json`、`full_corpus_e2e/full_corpus_report.md`。

验收边界：

- 全量构建未完成时不能 accepted。
- HTML extractor `Section` 错误未修复时必须是 `structured_blocker` 或 `needs_review`。

### 4.2 Route A Acceptance Pack

候选落点：

- `backend/data_service/code_assets/real_document_full_corpus_release/route_a_acceptance.py`

职责：

- 记录用户代表性真实资料来源类型、脱敏说明、用途边界和人工验收步骤。
- 产出 `route_a_acceptance/sample_pack_contract.json`、`route_a_acceptance/redaction_review.json`、`route_a_acceptance/manual_acceptance_record.md`。

验收边界：

- 用户未提供代表性真实资料时保持 `needs_review`。
- mock-only 或 sample-only 不能作为 Route A accepted evidence。

### 4.3 Quality Review Recorder

候选落点：

- `backend/data_service/code_assets/real_document_full_corpus_release/quality_review.py`

职责：

- 汇总 low-signal audit、quality feedback、correction plan、rule review。
- 记录人工审查结论、证据引用、拒绝原因和下一步动作。
- 产出 `quality_review/human_quality_review.json`、`quality_review/correction_decision_history.jsonl`、`quality_review/rule_effect_review.md`。

验收边界：

- 自动建议无人工审查时保持 `needs_review`。
- rule effect 不得改写上游原始 artifact。

### 4.4 External Project Closure

候选落点：

- `backend/data_service/code_assets/real_document_full_corpus_release/external_project_closure.py`

职责：

- 检查 `data_service`、`codexPat`、`HarnessOS`、`Navia` 的真实可读路径。
- 可用时执行真实 E2E 或验收烟测。
- 不可用时记录 structured unavailable 和 next action。

验收边界：

- 外部路径缺失不能 accepted。
- structured unavailable 不能计入 accepted 数量。

### 4.5 Release Gate Aggregator

候选落点：

- `backend/data_service/code_assets/real_document_full_corpus_release/release_gate.py`

职责：

- 聚合 Route A、Route B、全量 docs、质量审查、外部项目、restore/smoke、dependency hygiene、human approval。
- 产出 `release_gate/release_gate_summary.json`、`release_gate/release_readiness_report.md`。

验收边界：

- 任一高风险项缺失时 final release 不能 accepted。
- human approval 缺失必须保持 `needs_review`。

## 5. Public Surface 规划

后续实现如新增 public surface，应保持 build/read parity：

- MCP tool 前缀：`knowledge_code_real_document_full_corpus_release_*`
- CLI 命令组：`python -m data_service code real-document-full-corpus-release <command>`
- HTTP 路由家族：`/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/...`

所有 read 接口只读取 persisted artifacts，不能重新制造事实。所有 build 接口返回 repo-relative artifact refs、warnings、unresolved 和 next_actions。

## 6. 禁止的架构设计

- 用 Route B 小样本替代 Route A 用户代表性验收。
- 用 mock-only document 替代真实资料验收。
- 把 HTML extractor 失败静默过滤成 accepted。
- 把 impact candidate、GraphRAG evidence 或 Source trace 写成 runtime call claim。
- 绕过 human approval、外部项目路径状态或质量人工审查。
- 默认修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。
