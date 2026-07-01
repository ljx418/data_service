# V2.86-V2.90 Phase 162-166 Detailed Development and Acceptance Package

## 1. 总则

本包把 V2.86-V2.90 拆成可顺序执行的 Phase 162-166。每个 phase 必须先完成阶段开发计划、验收计划和 pre-implementation audit，再进入实现。本文是实施级计划，不是实现完成证据。

共同约束：

- 新实现默认落点为 `backend/data_service/code_assets/real_document_full_corpus_release/`。
- 公开接口默认新增独立 HTTP/CLI/MCP adapter。
- 不修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`，除非用户明确批准。
- 不把 `needs_review`、`structured_unavailable`、`structured_blocker` 或 `failed` 计入 accepted。
- 不声称 full call graph、runtime topology、data/control flow、type inference 或完整设计意图恢复。

## 2. Phase 162 / V2.86 Full Corpus E2E Hardening

### 开发计划

1. 创建 `full_corpus.py`，实现 build/read。
2. 从 `docs/V2.x` 收集真实文档，默认排除 `.tmp`、资源叉、缓存和明显生成中间件。
3. 对 Markdown、HTML、JSON、drawio 分类处理。
4. 对 HTML extractor `Section` 错误输出 `extractor_bug`，不能输出 raw traceback。
5. 生成 full corpus run、parser failures 和 report。

### 验收计划

- Focused test：`backend/tests/test_v2_86_full_corpus_e2e_hardening.py`。
- E2E：以 `docs/V2.x` 为真实输入执行全量构建或形成 `structured_blocker`。
- PRD/spec review：确认满足维护者“全量真实文档可审计”体验。
- False-green audit：确认小样本 Route B 未被写成全量 accepted。

### 出门条件

- `full_corpus_run.json`、`parser_failures.json`、`full_corpus_report.md` 均存在。
- `Section` 错误已修复或被结构化记录。
- Source trace 缺失时不能 accepted。

## 3. Phase 163 / V2.87 Route A Representative Material Acceptance

### 开发计划

1. 创建 `route_a_acceptance.py`，实现 build/read。
2. 定义 Route A 资料包合同、脱敏审查和人工验收记录。
3. 支持缺资料状态，输出 `needs_review` 和 next action。
4. 支持资料存在时记录 source type、redaction policy、manual review state 和截图/headless evidence refs。

### 验收计划

- Focused test：`backend/tests/test_v2_87_route_a_representative_acceptance.py`。
- E2E：无资料时验证 `needs_review`；有资料时验证人工记录和证据链。
- PRD/spec review：确认 Route A 不被 Route B 替代。
- False-green audit：mock-only、sample-only、path-only 不能 accepted。

### 出门条件

- `sample_pack_contract.json`、`redaction_review.json`、`manual_acceptance_record.md` 均存在。
- 未提供代表性资料时 final release 仍被阻断。

## 4. Phase 164 / V2.88 Quality Governance Human Review Closure

### 开发计划

1. 创建 `quality_review.py`，实现 build/read。
2. 读取 V2.84 quality artifacts。
3. 生成人工质量审查记录和纠错决策历史。
4. 生成 rule effect review，记录上游 artifact hash，只读校验。

### 验收计划

- Focused test：`backend/tests/test_v2_88_quality_governance_human_review.py`。
- E2E：使用 V2.84 artifacts 执行审查记录生成。
- PRD/spec review：确认维护者可看到质量问题、纠错建议、人工 review 状态和下一步动作。
- False-green audit：自动建议无人工 decision 时必须 `needs_review`。

### 出门条件

- `human_quality_review.json`、`correction_decision_history.jsonl`、`rule_effect_review.md` 均存在。
- 无人工确认的 recommendation 不得 accepted。

## 5. Phase 165 / V2.89 External Project E2E Closure

### 开发计划

1. 创建 `external_project_closure.py`，实现 build/read。
2. 读取或生成 project path manifest。
3. 对 `data_service` 执行本仓真实 E2E。
4. 对 `codexPat`、`HarnessOS`、`Navia` 重新确认路径；无路径时输出 `structured_unavailable`。
5. 生成 unavailable diagnosis。

### 验收计划

- Focused test：`backend/tests/test_v2_89_external_project_e2e_closure.py`。
- E2E：`data_service` 必须有真实执行结果；外部项目可用才执行真实 E2E。
- PRD/spec review：确认外部项目状态可审计。
- False-green audit：unavailable 不计 accepted。

### 出门条件

- `path_manifest.json`、`project_e2e_records.json`、`unavailable_diagnosis.md` 均存在。
- 缺路径项目不得 accepted。

## 6. Phase 166 / V2.90 Release Gate and Restore Hygiene

### 开发计划

1. 创建 `release_gate.py`，实现 build/read。
2. 聚合 V2.86-V2.89 artifacts。
3. 接入 restore/smoke、dependency hygiene、worktree hygiene、human approval state。
4. 生成 release gate summary 和 release readiness report。

### 验收计划

- Focused test：`backend/tests/test_v2_90_release_gate_restore_hygiene.py`。
- E2E：构造 accepted、needs_review、structured_unavailable、structured_blocker 混合状态，验证 final release status。
- PRD/spec review：确认维护者能一屏看到出门状态、阻断原因和下一步。
- False-green audit：任何高风险项缺失时 final release 不得 accepted。

### 出门条件

- `release_gate_summary.json`、`release_readiness_report.md` 均存在。
- final release accepted 必须满足 Route A、Route B、全量 docs、quality review、external project、restore/smoke、dependency hygiene、human approval 全部门槛。

## 7. 阶段最终验收命令计划

```text
pytest -q backend/tests/test_v2_86_full_corpus_e2e_hardening.py \
  backend/tests/test_v2_87_route_a_representative_acceptance.py \
  backend/tests/test_v2_88_quality_governance_human_review.py \
  backend/tests/test_v2_89_external_project_e2e_closure.py \
  backend/tests/test_v2_90_release_gate_restore_hygiene.py \
  backend/tests/test_public_surface_guard.py

python -m compileall backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 8. 打回规则

以下任一情况出现时，必须打回到开发计划阶段重新评估：

- 真实 E2E 无法执行且未产生结构化 blocker。
- accepted row 缺 artifact refs 或 evidence refs。
- Route A、外部项目、quality review、human approval 的缺失被隐藏。
- 全量 docs 构建失败被写成 accepted。
- 发现需要修改受保护 legacy 文件但未获得批准。
