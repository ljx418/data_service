# V2.86-V2.90 Implementation Blueprint and Acceptance Spec

## 1. 目的

本文把 V2.86-V2.90 PRD 目标、目标架构、artifact contract、public surface、focused tests 和出门验收门槛连接成实现级基线。本文不证明 V2.86-V2.90 已实现。

## 2. 代码落点规划

所有新增实现优先落在独立包内，避免修改 legacy 大文件：

```text
backend/data_service/code_assets/real_document_full_corpus_release/
  __init__.py
  shared.py
  persistence.py
  full_corpus.py
  route_a_acceptance.py
  quality_review.py
  external_project_closure.py
  release_gate.py
```

公开 adapter 规划：

```text
backend/data_service/cli_code_real_document_full_corpus_release.py
backend/data_service/mcp_code_real_document_full_corpus_release_tools.py
backend/app/api/v1/code_assets_real_document_full_corpus_release.py
```

默认不得修改：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

如后续发现必须注册新 router 或 CLI command，优先使用现有插件式注册点；若必须触碰受保护文件，需要先获得明确批准。

## 3. Artifact Layout

所有新 artifact 写入：

```text
workspace/assets/codebase/{codebase_id}/real_document_full_corpus_release/
```

子目录：

```text
full_corpus_e2e/
route_a_acceptance/
quality_review/
external_project_closure/
release_gate/
```

公共 artifact 只能包含 repo-relative path、artifact id、状态、证据引用、warnings、unresolved 和 next_actions。禁止包含本机绝对路径、secret、token、raw traceback、private virtualenv path。

## 4. Public Surface 规划

### 4.1 MCP tools

```text
knowledge_code_real_document_full_corpus_release_full_corpus_build
knowledge_code_real_document_full_corpus_release_full_corpus_read
knowledge_code_real_document_full_corpus_release_route_a_build
knowledge_code_real_document_full_corpus_release_route_a_read
knowledge_code_real_document_full_corpus_release_quality_review_build
knowledge_code_real_document_full_corpus_release_quality_review_read
knowledge_code_real_document_full_corpus_release_external_project_build
knowledge_code_real_document_full_corpus_release_external_project_read
knowledge_code_real_document_full_corpus_release_release_gate_build
knowledge_code_real_document_full_corpus_release_release_gate_read
```

### 4.2 CLI commands

命令组：

```text
python -m data_service code real-document-full-corpus-release <command>
```

子命令：

```text
full-corpus-build
full-corpus-read
route-a-build
route-a-read
quality-review-build
quality-review-read
external-project-build
external-project-read
release-gate-build
release-gate-read
```

### 4.3 HTTP routes

路由族：

```text
/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/full-corpus/build
/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/full-corpus
/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/route-a/build
/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/route-a
/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/quality-review/build
/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/quality-review
/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/external-project/build
/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/external-project
/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/release-gate/build
/workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/release-gate
```

Build 接口生成 artifact 并返回 refs。Read 接口只读取 persisted artifact，不重新制造事实。

## 5. 子阶段实现蓝图

### V2.86 Full Corpus E2E Hardening

实现入口：

- `full_corpus.build_full_corpus_e2e(...)`
- `full_corpus.read_full_corpus_e2e(...)`

输入：

- `workspace_id`
- `codebase_id`
- `source_root`，默认 repo-relative `docs/V2.x`
- `include_globs`
- `exclude_globs`

输出：

- `full_corpus_e2e/full_corpus_run.json`
- `full_corpus_e2e/parser_failures.json`
- `full_corpus_e2e/full_corpus_report.md`

验收：

- `docs/V2.x` 全量资料处理成功，或失败进入 `structured_blocker`。
- HTML extractor `Section` 错误有复现记录、修复结果或 blocker。
- GraphRAG 和 Source trace 只声明文档证据关系，不声明 full call graph 或 runtime topology。

### V2.87 Route A Representative Material Acceptance

实现入口：

- `route_a_acceptance.build_route_a_acceptance(...)`
- `route_a_acceptance.read_route_a_acceptance(...)`

输入：

- `workspace_id`
- `codebase_id`
- `sample_pack_ref`
- `redaction_policy`
- `manual_review_state`

输出：

- `route_a_acceptance/sample_pack_contract.json`
- `route_a_acceptance/redaction_review.json`
- `route_a_acceptance/manual_acceptance_record.md`

验收：

- 无用户代表性资料时状态为 `needs_review`。
- 有资料时 accepted 必须有来源说明、脱敏说明、人工体验步骤、截图或 headless evidence、reviewer decision。

### V2.88 Quality Governance Human Review Closure

实现入口：

- `quality_review.build_quality_review(...)`
- `quality_review.read_quality_review(...)`

输入：

- V2.84 quality artifacts。
- reviewer decision payload。

输出：

- `quality_review/human_quality_review.json`
- `quality_review/correction_decision_history.jsonl`
- `quality_review/rule_effect_review.md`

验收：

- 每条 quality/correction recommendation 必须有 evidence_refs 或 unresolved reason。
- 缺人工 decision 的 recommendation 保持 `needs_review`。
- rule effect review 不改写上游 artifact。

### V2.89 External Project E2E Closure

实现入口：

- `external_project_closure.build_external_project_closure(...)`
- `external_project_closure.read_external_project_closure(...)`

输入：

- project path manifest。
- allowed roots。

输出：

- `external_project_closure/path_manifest.json`
- `external_project_closure/project_e2e_records.json`
- `external_project_closure/unavailable_diagnosis.md`

验收：

- `data_service` 必须有真实本仓 E2E。
- `codexPat`、`HarnessOS`、`Navia` 无真实路径时为 `structured_unavailable`，不能 accepted。
- path-only 不能作为 E2E accepted。

### V2.90 Release Gate and Restore Hygiene

实现入口：

- `release_gate.build_release_gate(...)`
- `release_gate.read_release_gate(...)`

输入：

- V2.86-V2.89 artifacts。
- restore/smoke result。
- dependency hygiene result。
- human approval state。

输出：

- `release_gate/release_gate_summary.json`
- `release_gate/release_readiness_report.md`

验收：

- Route A、全量 docs、quality review、external projects、human approval 任一缺失时 final release 不能 accepted。
- Release report 必须列出阻断项、证据、next action 和 false-green audit。

## 6. Focused Test 目标

```text
backend/tests/test_v2_86_full_corpus_e2e_hardening.py
backend/tests/test_v2_87_route_a_representative_acceptance.py
backend/tests/test_v2_88_quality_governance_human_review.py
backend/tests/test_v2_89_external_project_e2e_closure.py
backend/tests/test_v2_90_release_gate_restore_hygiene.py
backend/tests/test_public_surface_guard.py
```

每个 focused test 必须覆盖 build/read parity、artifact refs、status preservation、false-green rejection。

## 7. 出门验收

阶段结束必须生成：

- focused test result。
- 真实 E2E result。
- PRD/spec review。
- false-green audit。
- protected legacy diff check。
- visual or headless acceptance evidence。
- final acceptance audit report。

任一高风险项无法消减时，不得继续写 final accepted，应输出风险点和备选技术路线供人类确认。
