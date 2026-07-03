# V2.96-V2.100 Implementation Blueprint and Acceptance Spec

## 1. 实现边界

本文件是实现指导，不是实现完成证据。V2.96-V2.100 进入代码阶段前，必须重新生成 phase-specific plan、acceptance plan 和 pre-implementation audit。

默认不修改：

- `backend/app/api/v1/data_service.py`
- `backend/data_service/service.py`

## 2. 建议代码落点

优先新增独立包：

```text
backend/data_service/code_assets/automated_evidence_closure/
  __init__.py
  shared.py
  persistence.py
  cli_gap.py
  route_a_evidence.py
  quality_workbench.py
  external_path_registry.py
  release_evidence_gate.py
```

Adapter 计划：

```text
backend/data_service/cli_code_automated_evidence_closure.py
backend/data_service/mcp_code_automated_evidence_closure_tools.py
backend/app/api/v1/code_assets_automated_evidence_closure.py
```

若必须复用 `real_acceptance_closure` 包，必须在审计报告中说明原因，并保持 V2.91-V2.95 artifact contract 兼容。

## 3. Artifact Layout

```text
workspace/{workspace_id}/assets/codebase/{codebase_id}/automated_evidence_closure/
  cli_gap_closure/
  route_a_evidence/
  quality_workbench/
  external_path_registry/
  release_evidence_gate/
```

public artifact 不得包含：

- 本地绝对路径。
- secret、token、私有凭据。
- raw traceback。
- 未经证据支持的 accepted claim。

## 4. Public Surface

MCP tools 计划：

- `knowledge_code_automated_evidence_closure_cli_gap_build/read`
- `knowledge_code_automated_evidence_closure_route_a_evidence_build/read`
- `knowledge_code_automated_evidence_closure_quality_workbench_build/read`
- `knowledge_code_automated_evidence_closure_external_path_build/read`
- `knowledge_code_automated_evidence_closure_release_gate_build/read`

CLI 命令组：

```text
python -m data_service code automated-evidence-closure <command>
```

HTTP route family：

```text
/api/workspaces/{workspace_id}/codebases/{codebase_id}/automated-evidence-closure/...
```

## 5. Accepted 条件

| 阶段 | Accepted 条件 | Non-accepted 条件 |
| --- | --- | --- |
| V2.96 | 默认 shell CLI 命令真实可执行，且 MCP/HTTP/parser inventory 一致 | 只验证 parser inventory，默认 shell 入口仍失败 |
| V2.97 | Route A 有真实资料、脱敏检查、截图/headless evidence、人工确认 | 缺真实资料、缺脱敏、缺人工确认 |
| V2.98 | 高风险质量建议有人类 decision，低风险建议有可复核自动预审 | 自动建议替代人工 decision |
| V2.99 | 每个外部项目有 accepted、structured_unavailable 或 structured_blocker 且证据可复核 | 缺路径却 accepted |
| V2.100 | 所有高风险项 accepted，human approval 完成 | 任一高风险项 non-accepted |

## 6. False-green 审计

实现必须拒绝：

- 把 Full Corpus accepted 当作 Route A accepted。
- 把自动质量建议当作 reviewer decision。
- 把 unavailable 外部项目计入 accepted。
- 把服务启动成功当作 restore smoke accepted。
- 把展示图或 HTML 报告当作代码验收证据。
