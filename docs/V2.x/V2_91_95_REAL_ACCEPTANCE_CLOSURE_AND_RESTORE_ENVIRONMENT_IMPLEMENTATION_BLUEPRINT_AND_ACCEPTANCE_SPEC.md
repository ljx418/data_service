# V2.91-V2.95 Implementation Blueprint and Acceptance Spec

## 1. 状态边界

本文件是 implementation guidance，不是 implementation acceptance。它把 PRD 体验目标连接到具体代码落点、artifact contract、public surface、focused tests 和验收门槛。

不得声明：

- V2.91-V2.95 已实现。
- Final release accepted。
- full call graph、runtime topology、data/control flow、type inference。
- 完整恢复复杂项目设计意图。

## 2. 推荐代码落点

新增实现优先使用独立包：

```text
backend/data_service/code_assets/real_acceptance_closure/
  __init__.py
  shared.py
  persistence.py
  runtime_restore.py
  route_a_material.py
  quality_decision.py
  external_project_validator.py
  release_finalizer.py
```

可选 public adapters：

```text
backend/data_service/cli_code_real_acceptance_closure.py
backend/data_service/mcp_code_real_acceptance_closure_tools.py
backend/app/api/v1/code_assets_real_acceptance_closure.py
```

受保护文件：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

除非用户明确批准，不修改上述 legacy 大文件。

## 3. Public Surface

MCP tools：

```text
knowledge_code_real_acceptance_closure_runtime_restore_build
knowledge_code_real_acceptance_closure_runtime_restore_read
knowledge_code_real_acceptance_closure_route_a_closure_build
knowledge_code_real_acceptance_closure_route_a_closure_read
knowledge_code_real_acceptance_closure_quality_decision_build
knowledge_code_real_acceptance_closure_quality_decision_read
knowledge_code_real_acceptance_closure_external_project_closure_build
knowledge_code_real_acceptance_closure_external_project_closure_read
knowledge_code_real_acceptance_closure_release_finalizer_build
knowledge_code_real_acceptance_closure_release_finalizer_read
```

CLI command group：

```text
python -m data_service code real-acceptance-closure <command>
```

Commands：

```text
runtime-restore-build
runtime-restore-read
route-a-closure-build
route-a-closure-read
quality-decision-build
quality-decision-read
external-project-closure-build
external-project-closure-read
release-finalizer-build
release-finalizer-read
```

HTTP route family：

```text
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/runtime-restore/build
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/runtime-restore
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/route-a-closure/build
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/route-a-closure
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/quality-decision/build
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/quality-decision
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/external-project-closure/build
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/external-project-closure
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/release-finalizer/build
/api/workspaces/{workspace_id}/codebases/{codebase_id}/real-acceptance-closure/release-finalizer
```

Read 接口只读取 persisted artifacts，不重新制造事实。Build 接口必须返回 artifact refs、evidence refs、warnings、unresolved、next actions。

## 4. Artifact Layout

所有新增 artifact 写入：

```text
workspace/assets/codebase/{codebase_id}/real_acceptance_closure/
```

Planned outputs：

```text
runtime_restore/runtime_diagnosis.json
runtime_restore/restore_checklist.md
runtime_restore/focused_regression_result.json

route_a_closure/material_manifest.json
route_a_closure/redaction_decision.json
route_a_closure/manual_acceptance_record.md

quality_decision/human_decisions.jsonl
quality_decision/rule_effect_closure.json
quality_decision/quality_closure_report.md

external_project_closure/path_binding_decision.json
external_project_closure/e2e_result_matrix.json
external_project_closure/unavailable_decisions.md

release_finalizer/final_gate_summary.json
release_finalizer/final_release_report.md
release_finalizer/false_green_audit.md
```

## 5. Phase Acceptance Signals

| Phase | Accepted 条件 | Non-accepted 条件 |
| --- | --- | --- |
| V2.91 | pytest runtime 可复跑，focused regression 有真实命令结果 | runtime 缺依赖、venv 不可创建、pytest 不可用 |
| V2.92 | Route A 有真实资料、脱敏、截图/headless evidence、人工验收 | 缺资料、缺脱敏、缺截图、缺人工签核 |
| V2.93 | 每条质量建议有 human decision 或明确 out-of-scope | 自动建议无人工决策 |
| V2.94 | 每个外部项目有 accepted 或 structured_unavailable/blocker | 缺路径却 accepted |
| V2.95 | 所有高风险项 accepted 且 human approval 完成 | 任一高风险项 non-accepted |

## 6. Required Tests

```text
backend/tests/test_v2_91_restoreable_acceptance_runtime.py
backend/tests/test_v2_92_route_a_material_closure.py
backend/tests/test_v2_93_human_quality_decision_closure.py
backend/tests/test_v2_94_external_project_path_e2e_closure.py
backend/tests/test_v2_95_final_release_gate_closure.py
backend/tests/test_public_surface_guard.py
```

## 7. False-green Rejection Rules

- 服务启动成功不能替代 pytest focused regression。
- Full Corpus accepted 不能替代 Route A accepted。
- 自动质量建议不能替代人工 quality decision。
- 外部项目缺路径不能 accepted。
- human approval 缺失时 final release 不能 accepted。
- `needs_review`、`structured_unavailable`、`structured_blocker` 不计入 accepted。

