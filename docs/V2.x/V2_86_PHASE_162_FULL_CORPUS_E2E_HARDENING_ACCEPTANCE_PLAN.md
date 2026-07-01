# V2.86 / Phase 162 Acceptance Plan：Full Corpus E2E Hardening

## 1. Acceptance Goal

Phase 162 验收目标是确认 `docs/V2.x` 全量真实文档 E2E 路径可被执行、审计和阻断。验收不能把小样本 Route B 结果、mock-only fixture 或未记录失败的全量构建写成 accepted。

## 2. Focused Test Plan

计划测试：

```text
pytest -q backend/tests/test_v2_86_full_corpus_e2e_hardening.py backend/tests/test_public_surface_guard.py
```

测试必须覆盖：

- full corpus build/read parity。
- included/excluded 文件范围。
- HTML parser failure 分类。
- `Section` 错误修复结果或 structured blocker。
- artifact_refs 和 evidence_refs。
- Source trace 缺失不能 accepted。
- `needs_review`、`structured_unavailable`、`structured_blocker`、`failed` 不计 accepted。

## 3. Real E2E Plan

真实 E2E 输入：

```text
docs/V2.x
```

执行结果必须产出：

```text
full_corpus_e2e/full_corpus_run.json
full_corpus_e2e/parser_failures.json
full_corpus_e2e/full_corpus_report.md
```

accepted 需要同时满足：

1. 输入范围明确，包含真实 repo-relative paths。
2. parser failures 全部有 category、status、message、next_action。
3. HTML extractor `Section` 问题已修复，或全量 accepted 被阻断。
4. 查询、GraphRAG、Source trace 有证据或明确 unresolved reason。
5. public artifact 不含本机绝对路径、secret、token、raw traceback 或 private virtualenv path。

## 4. PRD / Spec Review

验收后必须检查：

- 是否满足 PRD 中“维护者能对 `docs/V2.x` 全量真实文档执行导入、解析、构建、查询和失败分类”的体验。
- 是否满足目标架构中 Full Corpus E2E Runner 的职责。
- 是否保留 HTML extractor failure、Source trace 缺失和 low-signal 资料的 unresolved 状态。
- 是否没有把 documentation claim 当作 code fact。

## 5. False-green Audit

必须拒绝：

- 小样本 Route B accepted 推导全量 docs accepted。
- parser failure 被静默过滤。
- raw traceback 被写入 public artifact。
- GraphRAG 结果被写成 full call graph 或 runtime topology。
- Source trace 缺失仍写 accepted。

## 6. Exit Gate

Phase 162 可以 accepted 的条件：

- focused tests 通过。
- real E2E 通过。
- full corpus artifacts 存在且 schema 有效。
- PRD/spec review 通过。
- false-green audit 无 fatal/major。
- protected legacy file diff check 无未批准变更。

Phase 162 必须保持 `structured_blocker` 或 `needs_review` 的条件：

- HTML extractor `Section` 错误未修复且影响全量构建。
- `docs/V2.x` 无法完整处理且没有可审计降级。
- Source trace 缺失且无 unresolved reason。
- artifact_refs 或 evidence_refs 缺失。
