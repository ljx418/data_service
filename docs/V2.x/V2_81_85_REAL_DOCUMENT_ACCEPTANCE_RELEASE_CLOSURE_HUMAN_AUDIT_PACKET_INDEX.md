# V2.81-V2.85 人类审计包索引

## 1. 用途

本文档是人类审计者的固定入口。审计者只依赖 git 仓库内已提交文件，即可复核 V2.81-V2.85 自动化开发工作，不需要依赖聊天记录或未提交的 `workspace/` 运行状态。

## 2. 最短审计结论

- 业务实现提交：`c89ad3f feat: add V2.81-V2.85 real document acceptance audit`
- 审计证据补强提交：`1d90d47`、`601605f`
- 当前可审计通过范围：V2.81-V2.83 Route B 自动化工程验收。
- 当前不可放行范围：V2.84 保持 `needs_review`；V2.85 保持 `structured_unavailable`；最终 release 不能 accepted。
- 关键边界：Route B 使用仓库 `docs/` 真实项目文档，但不能替代用户代表性真实资料 Route A、人工质量 review、外部项目路径和 human approval。

## 3. 审计顺序

1. 阅读 PRD 和目标架构：
   - `docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_PRD.md`
   - `docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_TARGET_ARCHITECTURE.md`

2. 阅读开发与验收基线：
   - `docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md`
   - `docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_TEST_AND_E2E_MAPPING.md`
   - `docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_FULL_COVERAGE_MATRIX.md`

3. 阅读阶段最终验收状态：
   - `docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_FINAL_ACCEPTANCE_AUDIT_REPORT.md`
   - `docs/V2.x/V2_81_PHASE_157_REAL_DOCUMENT_SAMPLE_CONTRACT_ACCEPTANCE_AUDIT_REPORT.md`
   - `docs/V2.x/V2_82_PHASE_158_REAL_DOCUMENT_IMPORT_WIKI_ACCEPTANCE_AUDIT_REPORT.md`
   - `docs/V2.x/V2_83_PHASE_159_RETRIEVAL_GRAPHRAG_SOURCE_TRACE_ACCEPTANCE_AUDIT_REPORT.md`
   - `docs/V2.x/V2_84_PHASE_160_QUALITY_GOVERNANCE_ACCEPTANCE_AUDIT_REPORT.md`
   - `docs/V2.x/V2_85_PHASE_161_RELEASE_CLOSURE_RERUN_ACCEPTANCE_AUDIT_REPORT.md`

4. 阅读可视化报告与命令证据：
   - `docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_VISUAL_ACCEPTANCE_REPORT.html`
   - `docs/V2.x/visual_acceptance_assets/v2_81_85/visual_evidence_manifest.json`
   - `docs/V2.x/visual_acceptance_assets/v2_81_85/verification_evidence_20260701.md`

5. 阅读已提交的 Route B 产物快照：
   - `docs/V2.x/visual_acceptance_assets/v2_81_85/route_b_artifact_snapshot_manifest.json`
   - `docs/V2.x/visual_acceptance_assets/v2_81_85/route_b_artifacts/sample_contract/sample_contract.json`
   - `docs/V2.x/visual_acceptance_assets/v2_81_85/route_b_artifacts/real_e2e/import_run.json`
   - `docs/V2.x/visual_acceptance_assets/v2_81_85/route_b_artifacts/real_e2e/wiki_artifact_review.json`
   - `docs/V2.x/visual_acceptance_assets/v2_81_85/route_b_artifacts/retrieval_trace/query_trace_review.json`
   - `docs/V2.x/visual_acceptance_assets/v2_81_85/route_b_artifacts/retrieval_trace/graphrag_review.json`
   - `docs/V2.x/visual_acceptance_assets/v2_81_85/route_b_artifacts/release_closure/release_closure_rerun.json`

6. 对照代码和测试文件：
   - `backend/data_service/code_assets/real_document_acceptance/`
   - `backend/data_service/mcp_code_real_document_acceptance_tools.py`
   - `backend/data_service/cli_code_real_document_acceptance.py`
   - `backend/app/api/v1/code_assets_real_document_acceptance.py`
   - `backend/tests/test_v2_81_real_document_sample_contract.py`
   - `backend/tests/test_v2_82_real_document_import_wiki.py`
   - `backend/tests/test_v2_83_retrieval_graphrag_source_trace.py`
   - `backend/tests/test_v2_84_quality_governance_real_document.py`
   - `backend/tests/test_v2_85_release_closure_rerun.py`
   - `backend/tests/test_public_surface_guard.py`

## 4. 必查项

- 确认 V2.81-V2.83 只是 Route B 自动化工程验收 accepted。
- 确认 V2.84 仍为 `needs_review`。
- 确认 V2.85 仍为 `structured_unavailable`。
- 确认报告没有声明最终 release accepted。
- 确认 Route B 产物快照已经提交到 `docs/`，不是只引用被忽略的 `workspace/` 路径。
- 确认受保护 legacy 文件没有被修改：
  - `backend/app/api/v1/data_service.py`
  - `backend/data_service/service.py`

## 5. 证据时序说明

`verification_evidence_20260701.md` 是在被加入 git 前生成的，因此其中 `git status --short` 会显示该证据日志自身为 untracked。这是证据生成时序造成的，不代表业务实现提交存在未提交代码。

如果审计者需要在当前仓库重新确认清洁状态，应运行：

```bash
git status --short
git rev-list --left-right --count HEAD...origin/main
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 6. 最终边界

本审计包只支持对本阶段自动化开发工作做阶段级审计。它不会把用户代表性 Route A、人工质量 review、外部项目路径或 human release approval 转成 accepted。
