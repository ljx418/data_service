# V2.81-V2.85 Verification Evidence Log

Generated at: 2026-07-01T13:10:00+08:00
Workspace: /mnt/c/workspace/data_service

## Command
```bash
git log -1 --oneline --decorate
```
## Output
```text
c89ad3f (HEAD -> main, origin/main) feat: add V2.81-V2.85 real document acceptance audit
```
Exit code: 0

## Command
```bash
git rev-list --left-right --count HEAD...origin/main
```
## Output
```text
0	0
```
Exit code: 0

## Command
```bash
git status --short
```
## Output
```text
?? docs/V2.x/visual_acceptance_assets/v2_81_85/verification_evidence_20260701.md
```
Exit code: 0

## Command
```bash
git diff --name-only HEAD^ HEAD
```
## Output
```text
backend/app/api/__init__.py
backend/app/api/v1/code_assets_real_document_acceptance.py
backend/data_service/cli_code.py
backend/data_service/cli_code_real_document_acceptance.py
backend/data_service/code_assets/real_document_acceptance/__init__.py
backend/data_service/code_assets/real_document_acceptance/persistence.py
backend/data_service/code_assets/real_document_acceptance/service.py
backend/data_service/code_assets/real_document_acceptance/shared.py
backend/data_service/mcp_code_real_document_acceptance_tools.py
backend/data_service/mcp_code_tools.py
backend/tests/test_public_surface_guard.py
backend/tests/test_v2_81_real_document_sample_contract.py
backend/tests/test_v2_82_real_document_import_wiki.py
backend/tests/test_v2_83_retrieval_graphrag_source_trace.py
backend/tests/test_v2_84_quality_governance_real_document.py
backend/tests/test_v2_85_release_closure_rerun.py
docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md
docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_FINAL_ACCEPTANCE_AUDIT_REPORT.md
docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_HUMAN_AUDIT_EVIDENCE_INDEX.json
docs/V2.x/V2_76_80_PROJECT_ACCEPTANCE_HARDENING_VISUAL_ACCEPTANCE_REPORT.html
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_DOCUMENT_AUDIT_REPORT.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_FINAL_ACCEPTANCE_AUDIT_REPORT.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_FULL_COVERAGE_MATRIX.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_GAP_ANALYSIS.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_IMPLEMENTATION_BLUEPRINT_AND_ACCEPTANCE_SPEC.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_MILESTONES_AND_EXIT_GATES.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_PHASE_157_161_DETAILED_IMPLEMENTATION_PACKAGE.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_PHASE_READINESS_AND_SCHEMA_CONTRACTS.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_PRD.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_PRE_IMPLEMENTATION_AUDIT_REPORT.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_RISK_REDUCTION_AND_TECHNICAL_ROUTE_REVIEW.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_SELF_AUDIT_REVIEW_PACKAGE.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_TARGET_ARCHITECTURE.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_TARGET_STATE.drawio
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_TEST_AND_E2E_MAPPING.md
docs/V2.x/V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_VISUAL_ACCEPTANCE_REPORT.html
docs/V2.x/V2_81_PHASE_157_REAL_DOCUMENT_SAMPLE_CONTRACT_ACCEPTANCE_AUDIT_REPORT.md
docs/V2.x/V2_82_PHASE_158_REAL_DOCUMENT_IMPORT_WIKI_ACCEPTANCE_AUDIT_REPORT.md
docs/V2.x/V2_83_PHASE_159_RETRIEVAL_GRAPHRAG_SOURCE_TRACE_ACCEPTANCE_AUDIT_REPORT.md
docs/V2.x/V2_84_PHASE_160_QUALITY_GOVERNANCE_ACCEPTANCE_AUDIT_REPORT.md
docs/V2.x/V2_85_PHASE_161_RELEASE_CLOSURE_RERUN_ACCEPTANCE_AUDIT_REPORT.md
docs/V2.x/visual_acceptance_assets/v2_81_85/architecture.png
docs/V2.x/visual_acceptance_assets/v2_81_85/overview.png
docs/V2.x/visual_acceptance_assets/v2_81_85/quality_governance.png
docs/V2.x/visual_acceptance_assets/v2_81_85/real_e2e.png
docs/V2.x/visual_acceptance_assets/v2_81_85/release_closure.png
docs/V2.x/visual_acceptance_assets/v2_81_85/retrieval_trace.png
docs/V2.x/visual_acceptance_assets/v2_81_85/sample_contract.png
docs/V2.x/visual_acceptance_assets/v2_81_85/scenario_capture.html
docs/V2.x/visual_acceptance_assets/v2_81_85/user_path.png
docs/V2.x/visual_acceptance_assets/v2_81_85/visual_evidence_manifest.json
```
Exit code: 0

## Command
```bash
git diff --name-only HEAD^ HEAD -- backend/app/api/v1/data_service.py backend/data_service/service.py
```
## Output
```text
```
Exit code: 0

## Command
```bash
backend/.venv/bin/python -m pytest -q backend/tests/test_v2_81_real_document_sample_contract.py backend/tests/test_v2_82_real_document_import_wiki.py backend/tests/test_v2_83_retrieval_graphrag_source_trace.py backend/tests/test_v2_84_quality_governance_real_document.py backend/tests/test_v2_85_release_closure_rerun.py backend/tests/test_public_surface_guard.py
```
## Output
```text
```
Exit code: 0

## Command
```bash
backend/.venv/bin/python -m compileall backend/data_service backend/app/api backend/tests
```
## Output
```text
```
Exit code: 0

## Command
```bash
git diff --check
```
## Output
```text
```
Exit code: 0

## Command
```bash
python3 -m json.tool docs/V2.x/visual_acceptance_assets/v2_81_85/visual_evidence_manifest.json
```
## Output
```text
{
    "schema_version": "v2.81-85-visual-evidence",
    "generated_at": "2026-07-01T12:45:00+08:00",
    "stage": "V2.81-V2.85 Real Document Acceptance Release Closure",
    "capture_mode": "headless_chrome",
    "source_page": "docs/V2.x/visual_acceptance_assets/v2_81_85/scenario_capture.html",
    "fallback_note": "Linux Playwright Chromium could not launch because libnspr4.so was unavailable. Screenshots were captured with Windows Chrome in headless mode, so no visible browser focus was required for capture.",
    "overall_result": "partial_accepted",
    "release_result": "not_accepted",
    "screenshots": [
        {
            "id": "overview",
            "path": "docs/V2.x/visual_acceptance_assets/v2_81_85/overview.png",
            "size": "1280x720",
            "purpose": "\u9636\u6bb5\u603b\u89c8\u4e0e\u975e\u6700\u7ec8\u653e\u884c\u7ed3\u8bba"
        },
        {
            "id": "architecture",
            "path": "docs/V2.x/visual_acceptance_assets/v2_81_85/architecture.png",
            "size": "1280x720",
            "purpose": "\u76ee\u6807\u67b6\u6784\u4e0e\u5f53\u524d\u5b9e\u73b0\u5b9e\u4f53"
        },
        {
            "id": "sample_contract",
            "path": "docs/V2.x/visual_acceptance_assets/v2_81_85/sample_contract.png",
            "size": "1280x720",
            "purpose": "V2.81 \u771f\u5b9e\u8d44\u6599\u6837\u672c\u5951\u7ea6\u9a8c\u6536"
        },
        {
            "id": "real_e2e",
            "path": "docs/V2.x/visual_acceptance_assets/v2_81_85/real_e2e.png",
            "size": "1280x720",
            "purpose": "V2.82 \u771f\u5b9e\u8d44\u6599\u5bfc\u5165\u4e0e Wiki artifact \u9a8c\u6536"
        },
        {
            "id": "retrieval_trace",
            "path": "docs/V2.x/visual_acceptance_assets/v2_81_85/retrieval_trace.png",
            "size": "1280x720",
            "purpose": "V2.83 \u68c0\u7d22\u3001GraphRAG \u4e0e Source trace \u9a8c\u6536"
        },
        {
            "id": "quality_governance",
            "path": "docs/V2.x/visual_acceptance_assets/v2_81_85/quality_governance.png",
            "size": "1280x720",
            "purpose": "V2.84 \u8d28\u91cf\u6cbb\u7406 needs_review \u8bc1\u636e"
        },
        {
            "id": "release_closure",
            "path": "docs/V2.x/visual_acceptance_assets/v2_81_85/release_closure.png",
            "size": "1280x720",
            "purpose": "V2.85 \u53d1\u5e03\u95ed\u73af structured_unavailable \u8bc1\u636e"
        },
        {
            "id": "user_path",
            "path": "docs/V2.x/visual_acceptance_assets/v2_81_85/user_path.png",
            "size": "1280x720",
            "purpose": "\u7ef4\u62a4\u8005\u6700\u5c0f\u4f53\u9a8c\u8def\u5f84"
        }
    ],
    "real_route_b_artifacts": [
        "workspace/v28185-real-docs/assets/codebase/data-service-v28185-real-docs/real_document_acceptance/sample_contract/sample_contract.json",
        "workspace/v28185-real-docs/assets/codebase/data-service-v28185-real-docs/real_document_acceptance/sample_contract/manual_scenario_plan.md",
        "workspace/v28185-real-docs/assets/codebase/data-service-v28185-real-docs/real_document_acceptance/real_e2e/import_run.json",
        "workspace/v28185-real-docs/assets/codebase/data-service-v28185-real-docs/real_document_acceptance/real_e2e/wiki_artifact_review.json",
        "workspace/v28185-real-docs/assets/codebase/data-service-v28185-real-docs/real_document_acceptance/real_e2e/real_document_e2e_report.md",
        "workspace/v28185-real-docs/assets/codebase/data-service-v28185-real-docs/real_document_acceptance/retrieval_trace/query_trace_review.json",
        "workspace/v28185-real-docs/assets/codebase/data-service-v28185-real-docs/real_document_acceptance/retrieval_trace/graphrag_review.json",
        "workspace/v28185-real-docs/assets/codebase/data-service-v28185-real-docs/real_document_acceptance/retrieval_trace/source_trace_review.md",
        "workspace/v28185-real-docs/assets/codebase/data-service-v28185-real-docs/real_document_acceptance/quality/quality_governance_review.json",
        "workspace/v28185-real-docs/assets/codebase/data-service-v28185-real-docs/real_document_acceptance/quality/correction_acceptance_report.md",
        "workspace/v28185-real-docs/assets/codebase/data-service-v28185-real-docs/real_document_acceptance/release_closure/release_closure_rerun.json",
        "workspace/v28185-real-docs/assets/codebase/data-service-v28185-real-docs/real_document_acceptance/release_closure/final_manual_acceptance_report.md"
    ],
    "phase_results": [
        {
            "phase": "V2.81",
            "status": "accepted_for_route_b",
            "reason": "\u4ed3\u5e93 docs/ \u771f\u5b9e\u9879\u76ee\u6587\u6863\u6837\u672c\u5951\u7ea6\u5df2\u751f\u6210\uff0c\u7528\u6237\u4ee3\u8868\u6027 Route A \u4ecd\u4e3a needs_review\u3002"
        },
        {
            "phase": "V2.82",
            "status": "accepted_for_route_b",
            "reason": "\u771f\u5b9e\u4ed3\u5e93\u6587\u6863\u5bfc\u5165\u3001Wiki artifact review \u548c E2E report \u5df2\u751f\u6210\u3002"
        },
        {
            "phase": "V2.83",
            "status": "accepted_for_route_b",
            "reason": "\u68c0\u7d22\u3001GraphRAG \u548c Source trace \u5747\u4fdd\u7559 evidence/source refs\uff0c\u672a\u58f0\u660e\u5b8c\u6574\u8c03\u7528\u56fe\u6216\u8fd0\u884c\u62d3\u6251\u3002"
        },
        {
            "phase": "V2.84",
            "status": "needs_review",
            "reason": "\u7f3a\u5c11\u4eba\u5de5\u8d28\u91cf review\uff0c\u4e0d\u80fd accepted\u3002"
        },
        {
            "phase": "V2.85",
            "status": "structured_unavailable",
            "reason": "\u5916\u90e8\u9879\u76ee\u8def\u5f84\u4e0e human approval \u7f3a\u5931\uff0c\u6700\u7ec8 release \u4e0d\u80fd accepted\u3002"
        }
    ]
}
```
Exit code: 0

## Command
```bash
file docs/V2.x/visual_acceptance_assets/v2_81_85/overview.png docs/V2.x/visual_acceptance_assets/v2_81_85/architecture.png docs/V2.x/visual_acceptance_assets/v2_81_85/sample_contract.png docs/V2.x/visual_acceptance_assets/v2_81_85/real_e2e.png docs/V2.x/visual_acceptance_assets/v2_81_85/retrieval_trace.png docs/V2.x/visual_acceptance_assets/v2_81_85/quality_governance.png docs/V2.x/visual_acceptance_assets/v2_81_85/release_closure.png docs/V2.x/visual_acceptance_assets/v2_81_85/user_path.png
```
## Output
```text
docs/V2.x/visual_acceptance_assets/v2_81_85/overview.png:           PNG image data, 1280 x 720, 8-bit/color RGB, non-interlaced
docs/V2.x/visual_acceptance_assets/v2_81_85/architecture.png:       PNG image data, 1280 x 720, 8-bit/color RGB, non-interlaced
docs/V2.x/visual_acceptance_assets/v2_81_85/sample_contract.png:    PNG image data, 1280 x 720, 8-bit/color RGB, non-interlaced
docs/V2.x/visual_acceptance_assets/v2_81_85/real_e2e.png:           PNG image data, 1280 x 720, 8-bit/color RGB, non-interlaced
docs/V2.x/visual_acceptance_assets/v2_81_85/retrieval_trace.png:    PNG image data, 1280 x 720, 8-bit/color RGB, non-interlaced
docs/V2.x/visual_acceptance_assets/v2_81_85/quality_governance.png: PNG image data, 1280 x 720, 8-bit/color RGB, non-interlaced
docs/V2.x/visual_acceptance_assets/v2_81_85/release_closure.png:    PNG image data, 1280 x 720, 8-bit/color RGB, non-interlaced
docs/V2.x/visual_acceptance_assets/v2_81_85/user_path.png:          PNG image data, 1280 x 720, 8-bit/color RGB, non-interlaced
```
Exit code: 0

