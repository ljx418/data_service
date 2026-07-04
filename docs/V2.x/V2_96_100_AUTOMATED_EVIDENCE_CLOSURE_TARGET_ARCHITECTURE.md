# V2.96-V2.100 Target Architecture：少人工真实验收与出门证据闭环

## 1. 架构原则

- 保留 V2.91-V2.95 的状态事实，不把未闭环项改写为 accepted。
- 新增实现应优先放在独立 code asset 包或既有 `real_acceptance_closure` 包内。
- public surface 必须保持 MCP、HTTP、CLI 三类入口的 build/read 语义一致。
- read 接口只读取 persisted artifacts；build 接口生成 artifact refs、warnings、unresolved、next_actions。
- 任何 accepted 必须绑定真实命令、真实资料、API/CLI/MCP 结果、截图/headless evidence 或人工签核。

## 2. 当前架构实体

| 实体 | 状态 | 职责 |
| --- | --- | --- |
| `backend/data_service/code_assets/real_acceptance_closure/runtime_restore.py` | 已开发，需环境修复 | 生成 runtime diagnosis、restore checklist、focused regression result |
| `backend/data_service/code_assets/real_acceptance_closure/route_a_material.py` | 已开发，缺真实资料 | 生成 Route A material manifest、redaction decision、manual acceptance record |
| `backend/data_service/code_assets/real_acceptance_closure/quality_decision.py` | 已开发，缺人工决策 | 记录 quality human decisions、rule effect closure |
| `backend/data_service/code_assets/real_acceptance_closure/external_project_validator.py` | 已开发，缺外部路径 | 记录路径绑定、E2E matrix、unavailable decisions |
| `backend/data_service/code_assets/real_acceptance_closure/release_finalizer.py` | 已开发，final release 阻断 | 聚合 final gate summary、release report、false-green audit |
| `backend/data_service/mcp_code_real_acceptance_closure_tools.py` | 已开发 | 暴露 `knowledge_code_real_acceptance_closure_*` tools |
| `backend/app/api/v1/code_assets_real_acceptance_closure.py` | 已开发 | 暴露 real-acceptance-closure HTTP route family |
| `backend/data_service/cli_code_real_acceptance_closure.py` | 已开发但默认入口有 gap | 为 code parser 注册 real-acceptance-closure command group |
| `backend/app/static/knowledge_console/*` | 已开发 | 静态控制台入口 |
| `workspace/v2_91_95_real_acceptance_e2e/*` | 真实证据 | V2.91-V2.95 artifacts，final gate 为 `structured_blocker` |
| `docs/present/*` | 辅助展示 | 帮助 Agent/人类理解，不作为代码验收证据 |

## 3. 目标补强实体

| 目标实体 | 状态 | 计划职责 |
| --- | --- | --- |
| Default CLI Entrypoint Adapter | 待新增或修改 | 让 `python -m data_service code real-acceptance-closure ...` 使用 code parser |
| Route A Evidence Automator | 待新增或扩展 | 扫描真实资料、生成脱敏检查、截图/headless evidence、人工确认草稿 |
| Quality Decision Workbench | 待新增或扩展 | 生成风险分级、人类最小决策队列、decision history |
| External Project Path Registry | 待新增或扩展 | 管理项目路径配置、可读性检查、E2E command refs、unavailable 决议 |
| Release Evidence Aggregator | 待新增或扩展 | 聚合 dependency hygiene、restore smoke、human approval 和上游 accepted artifacts |

## 4. 分层关系

| 层级 | 具体实体 | 交互 |
| --- | --- | --- |
| 用户入口层 | Knowledge Console、HTML 报告、CLI、MCP、HTTP | 发起 build/read，查看 release 状态和 next actions |
| Adapter 层 | CLI adapter、MCP tool handler、HTTP router | 转换请求为统一 payload，不制造新事实 |
| Evidence Service 层 | runtime、Route A、Quality、External、Release 服务 | 生成结构化 artifacts 和 unresolved |
| Persistence 层 | workspace assets、docs/V2.x、docs/present | 持久化 artifact refs、报告和展示材料 |
| Gate 层 | false-green audit、release finalizer | 根据最差高风险状态决定 final status |

## 5. Public Surface 目标

- MCP tools：继续使用 `knowledge_code_real_acceptance_closure_*`，新增或扩展 V2.96-V2.100 build/read 能力。
- CLI：默认 shell 入口必须能执行 `python -m data_service code real-acceptance-closure <command>`，或文档改为唯一真实可用命令并记录旧命令 gap。
- HTTP：继续使用 `/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/...` route family。
- Artifact schema：必须包含 `status`、`artifact_refs`、`evidence_refs`、`warnings`、`unresolved`、`next_actions`。

## 6. 禁止的架构设计

- 不允许用展示材料替代验收证据。
- 不允许用 Full Corpus accepted 替代 Route A accepted。
- 不允许用自动质量建议替代 reviewer decision。
- 不允许把外部项目 path missing 计入 accepted。
- 不允许把服务启动成功等同于 restore smoke accepted。

## 7. Post-implementation architecture reconciliation

本节记录实现后的架构事实，用于避免把早期 planning baseline 误读为当前代码事实。

### 7.1 当前已落地实体

| 实体 | 当前状态 | 代码事实 |
| --- | --- | --- |
| Default CLI Entrypoint Adapter | 已实现并测试 | `backend/data_service/__main__.py`、`backend/data_service/cli_code.py` 已能通过默认 shell CLI 访问 `code automated-evidence-closure` 命令族 |
| Automated Evidence Closure package | 已实现并测试 | `backend/data_service/code_assets/automated_evidence_closure/` |
| Route A Evidence Automator | 已实现，最终验收仍需人工确认 | `backend/data_service/code_assets/automated_evidence_closure/route_a_evidence.py` |
| Quality Decision Workbench | 已实现，最终验收仍需 reviewer decision | `backend/data_service/code_assets/automated_evidence_closure/quality_workbench.py` |
| External Project Path Registry | 已实现，外部项目缺路径时保持 `structured_unavailable` | `backend/data_service/code_assets/automated_evidence_closure/external_path_registry.py` |
| Automated Release Evidence Gate | 已实现，final release 仍非全绿 | `backend/data_service/code_assets/automated_evidence_closure/release_evidence_gate.py` |
| CLI adapter | 已实现并测试 | `backend/data_service/cli_code_automated_evidence_closure.py` |
| MCP adapter | 已实现并测试 | `backend/data_service/mcp_code_automated_evidence_closure_tools.py` |
| HTTP adapter | 已实现并测试 | `backend/app/api/v1/code_assets_automated_evidence_closure.py` |

### 7.2 当前 public surface

- CLI：`python -m data_service code automated-evidence-closure <command>`。
- MCP：`knowledge_code_automated_evidence_closure_*_build/read`。
- HTTP：`/api/workspaces/{workspace_id}/codebases/{codebase_id}/automated-evidence-closure/...`。

V2.91-V2.95 的 `real-acceptance-closure` surface 仍作为上游历史阶段能力保留；V2.96-V2.100 的新增实现不再声明为“待新增”，而是以 `automated_evidence_closure` 独立包承载。

### 7.3 验收声明边界

- 可以声明：V2.96-V2.100 文档完整支撑范围内的代码实体、CLI/MCP/HTTP surface、artifact persistence、focused tests 和命令级 E2E 证据已实现。
- 不可以声明：本阶段 final release 全绿 accepted。
- 不可以声明：本阶段自动化开发阶段已全部完成到出门验收全绿状态。

拒绝全绿的原因不是 focused tests 失败，而是 PRD 明确要求保留的高风险真实输入缺口仍存在：Route A 人工确认、quality reviewer decision、codexPat/HarnessOS/Navia 外部路径、dependency hygiene、restore smoke 和 human approval。
