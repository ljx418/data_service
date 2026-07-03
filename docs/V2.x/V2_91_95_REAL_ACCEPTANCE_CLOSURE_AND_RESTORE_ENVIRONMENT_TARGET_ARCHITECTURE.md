# V2.91-V2.95 Target Architecture：真实验收闭环与本机恢复环境加固

## 1. 架构原则

- 只读引用 V2.81-V2.90 persisted artifacts 和审计报告，不静默改写上游证据。
- 每个 accepted 必须绑定真实资料、真实执行、artifact refs、API/CLI/MCP 结果、截图或人工签核。
- `needs_review`、`structured_unavailable`、`structured_blocker` 必须在报告、面板和 release gate 中保留。
- 文档描述不当作 code fact，不扩大为 full call graph、runtime topology、data/control flow、type inference 或完整设计意图恢复。
- 新增实现应优先放在独立 code asset 包或既有 V2.86-V2.90 包内，不触碰 legacy 大文件。

## 2. 当前架构基线

| 实体 | 状态 | 职责 |
| --- | --- | --- |
| `backend/data_service/code_assets/real_document_full_corpus_release/full_corpus.py` | 已实现 | V2.86 Full Corpus E2E Runner，处理 `docs/V2.x` 真实资料并输出 full corpus artifact |
| `backend/data_service/code_assets/real_document_full_corpus_release/route_a_acceptance.py` | 已实现但待真实输入 | Route A 资料包合同、脱敏审查和人工验收记录结构 |
| `backend/data_service/code_assets/real_document_full_corpus_release/quality_review.py` | 已实现但待人工决策 | 人工质量审查记录和纠错决策历史结构 |
| `backend/data_service/code_assets/real_document_full_corpus_release/external_project_closure.py` | 已实现但待外部路径 | 外部项目路径和 E2E 状态记录 |
| `backend/data_service/code_assets/real_document_full_corpus_release/release_gate.py` | 已实现但 final release 未通过 | 聚合 release gate summary 和 readiness report |
| `backend/app/api/v1/code_assets_real_document_full_corpus_release.py` | 已实现 | V2.86-V2.90 HTTP build/read surface |
| `backend/data_service/mcp_code_real_document_full_corpus_release_tools.py` | 已实现 | V2.86-V2.90 MCP build/read tools |
| `backend/data_service/cli_code_real_document_full_corpus_release.py` | 已实现但需恢复 runtime 验证 | CLI command 到 MCP tool payload 映射 |
| `backend/app/static/knowledge_console/*` | 已实现 | Knowledge Console 静态体验入口 |
| `workspace/v2_86_90_manual_experience/*` | 真实运行证据 | 本地人工体验产物，包含 Full Corpus、Route A、Quality、External Project、Release Gate artifacts |

## 3. 目标补强分层

| 层级 | 当前能力 | V2.91-V2.95 目标 |
| --- | --- | --- |
| Runtime | 服务可运行，但 pytest runtime 迁移损坏 | 建立可复跑 pytest/venv/dependency baseline |
| Route A | 合同结构已存在，缺真实资料 | 增加资料包 intake、脱敏审查、人工验收证据 |
| Quality | 人工审查结构已存在，缺真实 decision | 增加 human decision recorder 和 rule effect review closure |
| External Project | data_service 可用，三外部项目缺路径 | 增加路径绑定检查、E2E smoke、unavailable 决议记录 |
| Release Gate | 可聚合阻断项，但 final release 未 accepted | 增加 restore/dependency/human approval gate，形成最终出门判断 |

## 4. 目标架构实体

### 4.1 Acceptance Runtime Restorer

候选落点：

- `backend/data_service/code_assets/real_acceptance_closure/runtime_restore.py`

职责：

- 检查 `backend/.venv` 是否可执行、pytest 是否可用、`python3-venv` 是否可创建临时 runtime。
- 生成 dependency baseline、pytest runtime diagnosis、restore checklist。
- 产出 `runtime_restore/runtime_diagnosis.json`、`runtime_restore/restore_checklist.md`、`runtime_restore/focused_regression_result.json`。

验收边界：

- 若 pytest runtime 不可用，必须输出 `structured_blocker` 或 `structured_unavailable`，不能假写 PASS。
- 不能把服务可运行等同于 focused tests 可复跑。

### 4.2 Route A Material Intake and Review

候选落点：

- 复用并扩展 `backend/data_service/code_assets/real_document_full_corpus_release/route_a_acceptance.py`
- 或新增 `backend/data_service/code_assets/real_acceptance_closure/route_a_material.py`

职责：

- 读取用户代表性真实资料包目录。
- 记录 source type、redaction policy、screenshot/headless evidence、manual reviewer、decision。
- 产出 `route_a_closure/material_manifest.json`、`route_a_closure/redaction_decision.json`、`route_a_closure/manual_acceptance_record.md`。

验收边界：

- 无真实资料、无脱敏审查、无人工验收时保持 `needs_review`。
- mock-only、sample-only、path-only 不能 accepted。

### 4.3 Human Quality Decision Recorder

候选落点：

- 复用并扩展 `backend/data_service/code_assets/real_document_full_corpus_release/quality_review.py`
- 或新增 `backend/data_service/code_assets/real_acceptance_closure/quality_decision.py`

职责：

- 读取 V2.84/V2.88 quality artifacts。
- 记录 reviewer decision：approved、rejected、needs_review、revoked。
- 产出 `quality_decision/human_decisions.jsonl`、`quality_decision/rule_effect_closure.json`、`quality_decision/quality_closure_report.md`。

验收边界：

- 自动建议不能替代人工 decision。
- rule effect 不得改写上游原始 artifact。

### 4.4 External Project Path and E2E Validator

候选落点：

- 复用并扩展 `backend/data_service/code_assets/real_document_full_corpus_release/external_project_closure.py`
- 或新增 `backend/data_service/code_assets/real_acceptance_closure/external_project_validator.py`

职责：

- 绑定 `data_service`、`codexPat`、`HarnessOS`、`Navia` 路径。
- 对可读项目执行 scoped smoke/E2E。
- 对不可用项目记录 unavailable decision、reason、next action。
- 产出 `external_project_closure/path_binding_decision.json`、`external_project_closure/e2e_result_matrix.json`、`external_project_closure/unavailable_decisions.md`。

验收边界：

- 缺路径项目不能 accepted。
- unavailable 只能作为结构化阻断，不计入 accepted count。

### 4.5 Final Release Gate Finalizer

候选落点：

- 复用并扩展 `backend/data_service/code_assets/real_document_full_corpus_release/release_gate.py`
- 或新增 `backend/data_service/code_assets/real_acceptance_closure/release_finalizer.py`

职责：

- 聚合 runtime restore、Route A、Route B、Full Corpus、Quality、External Project、dependency hygiene、human approval。
- 产出 `release_finalizer/final_gate_summary.json`、`release_finalizer/final_release_report.md`、`release_finalizer/false_green_audit.md`。

验收边界：

- 任一高风险项缺失时 final release 不能 accepted。
- human approval 缺失必须保持 `needs_review`。

## 5. Public Surface 规划

如进入实现阶段，新增 public surface 使用独立族，避免混淆 V2.86-V2.90：

- MCP 前缀：`knowledge_code_real_acceptance_closure_*`
- CLI 命令组：`python -m data_service code real-acceptance-closure <command>`
- HTTP route family：`/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/...`

计划命令：

- `runtime-restore-build/read`
- `route-a-closure-build/read`
- `quality-decision-build/read`
- `external-project-closure-build/read`
- `release-finalizer-build/read`

所有 read 接口只读取 persisted artifacts。所有 build 接口返回 artifact refs、warnings、unresolved、next_actions。

## 6. 禁止的架构设计

- 用 Full Corpus accepted 替代 Route A accepted。
- 用自动质量建议替代人工质量审查。
- 用服务启动成功替代 pytest focused regression 通过。
- 把外部项目 path missing 写成 accepted。
- 把 dependency audit 风险隐藏在 release gate 外。
- 默认修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。

