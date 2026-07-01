# V2.86 / Phase 162 Development Plan：Full Corpus E2E Hardening

## 1. Phase Goal

Phase 162 的目标是把 V2.81-V2.85 已验证的小样本 Route B 真实文档链路，推进到 `docs/V2.x` 全量真实文档 E2E 验收路径。本文是阶段级开发计划，不是实现完成证据。

本阶段不得声明：

- V2.86 已实现或已验收。
- 全量 `docs/V2.x` 已 accepted。
- Route B 等同 Route A。
- full call graph、runtime topology、data/control flow、type inference 或完整设计意图恢复。

## 2. Implementation Boundary

默认新增代码落点：

```text
backend/data_service/code_assets/real_document_full_corpus_release/
  __init__.py
  shared.py
  persistence.py
  full_corpus.py
```

默认新增 public adapter：

```text
backend/data_service/cli_code_real_document_full_corpus_release.py
backend/data_service/mcp_code_real_document_full_corpus_release_tools.py
backend/app/api/v1/code_assets_real_document_full_corpus_release.py
```

不得默认修改：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

如后续发现必须触碰受保护文件，必须先停止并取得明确批准。

## 3. Development Steps

1. 创建 full corpus artifact layout。
2. 读取 `docs/V2.x` 全量真实文档输入范围。
3. 默认排除 `.tmp/`、`backend/.tmp/`、资源叉文件、缓存文件和明显构建中间产物。
4. 对 Markdown、HTML、JSON、drawio 做分类处理。
5. 复现或识别 HTML extractor `Section` 错误。
6. 将 parser failure 转成结构化 `parser_failures.json`，不得输出 raw traceback。
7. 生成 `full_corpus_run.json`，记录 included、excluded、processed、accepted、failed、unresolved。
8. 生成 `full_corpus_report.md`，记录真实 E2E 状态、Source trace 状态、GraphRAG 边界和 next actions。
9. 实现 read 接口只读取 persisted artifacts，不重新制造事实。

## 4. Planned Artifacts

```text
workspace/assets/codebase/{codebase_id}/real_document_full_corpus_release/full_corpus_e2e/full_corpus_run.json
workspace/assets/codebase/{codebase_id}/real_document_full_corpus_release/full_corpus_e2e/parser_failures.json
workspace/assets/codebase/{codebase_id}/real_document_full_corpus_release/full_corpus_e2e/full_corpus_report.md
```

## 5. Planned Public Surface

MCP：

```text
knowledge_code_real_document_full_corpus_release_full_corpus_build
knowledge_code_real_document_full_corpus_release_full_corpus_read
```

CLI：

```text
python -m data_service code real-document-full-corpus-release full-corpus-build
python -m data_service code real-document-full-corpus-release full-corpus-read
```

HTTP：

```text
POST /workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/full-corpus/build
GET  /workspaces/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/full-corpus
```

## 6. Risk Controls

- 小样本 Route B accepted 不能推导全量 docs accepted。
- HTML extractor failure 必须记录为 `extractor_bug`、`needs_review`、`structured_blocker` 或 `failed`。
- Source trace 缺失时不能 accepted。
- GraphRAG 只能声明文档证据关系，不声明完整调用图或运行时拓扑。
- full corpus accepted 必须有真实输入范围、artifact refs、evidence refs、命令/API 结果和 false-green audit。

## 7. Handoff Criteria

Phase 162 实现完成后才能进入验收阶段。实现完成前，本文只能作为 `pass for implementation guidance` 的开发基线。
