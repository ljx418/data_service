# V2.116-V2.120 Test and E2E Mapping

## 1. Focused Tests

```text
backend/tests/test_v2_116_ocr_anchor_provider_closure.py
backend/tests/test_v2_117_source_trace_batch_closure.py
backend/tests/test_v2_118_headless_ui_visual_acceptance.py
backend/tests/test_v2_119_safe_build_allowlist_governance.py
backend/tests/test_v2_120_final_portfolio_acceptance_rerun.py
backend/tests/test_public_surface_guard.py
```

详细 fixture、负向用例、stale/mixed-run、approval mismatch、path escape、blank page、wrong-source trace 等测试，以：

```text
V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_DETAILED_TEST_FIXTURES_AND_NEGATIVE_CASES.md
```

为准。

## 2. Requirement-to-test Mapping

| Requirement | Test focus | False-green rejection |
| --- | --- | --- |
| OCR accepted needs anchor and provider output | V2.116 focused test | provider readiness 或 direct text extraction 不得 accepted |
| OCR dependency missing is structured | V2.116 focused test | missing `tesseract`/`pdftoppm`/`soffice` 不得 accepted |
| OCR anchor hit is required | V2.116 focused test | OCR output without anchor hit 不得 accepted |
| Source trace needs import/query/source refs | V2.117 focused test | file existence 不得 accepted |
| Source trace accepted needs same-source proof | V2.117 focused test | source_id/source_hash/query result/trace source 不匹配不得 accepted |
| UI evidence needs screenshot or browser blocker | V2.118 focused test | HTML report 不得替代 screenshot |
| Safe build executes approved commands only | V2.119 focused test | unapproved shell command 不得执行 |
| Safe build requires managed sandbox | V2.119 focused test | sandbox unavailable 时不得执行真实外部项目命令 |
| Final gate aggregates high-risk evidence | V2.120 focused test | unavailable/blocker/failed 不得计入 accepted |
| Public surface remains stable | public surface guard | planned docs 不得替代 registered surface |
| Unbound mixed run is rejected | V2.120 focused test | 未在 source_run_refs 声明或 lineage/hash 不匹配的跨 run artifact 不得聚合 accepted |
| Lineage-bound cross-run input is allowed | V2.120 focused test | source_run_refs 声明且 lineage/hash 匹配时不得误判 mixed-run |
| Approval digest is enforced | V2.119/V2.120 focused test | 程序自批或 normalized binding digest 不一致不得执行/accepted |
| Headless DOM assertion is required | V2.118 focused test | 空白页、500 页、selector 缺失不得 accepted |
| Persisted JSON validates against schema bundle | V2.120 focused test | 缺 envelope、业务字段出现在顶层或 required 缺失不得 accepted |
| `/knowledge` remains read-only for decisions | V2.118/public surface test | UI 写入 anchor/approval/revoke 不得进入本阶段 accepted |

## 3. Real E2E

```text
PYTHONPATH=backend python3 -m data_service portfolio-real-evidence build \
  --workspace-id v2_116_120_real \
  --root /mnt/c/workspace \
  --max-code-projects 3 \
  --timeout-seconds 120 \
  --headless
```

Expected outputs:

```text
v2_116_120_real/portfolio_real_evidence_acceptance/
```

Safe Build E2E guard:

- If managed sandbox is not available, the run must produce command proposals and `structured_blocker` rows, and must prove no external project command was executed.
- A bounded `--max-code-projects 3` run cannot produce portfolio final accepted; non-executed projects must remain queued/deferred with reasons.

OCR-specific E2E expectations:

- If local OCR dependencies are missing, the run must produce `structured_unavailable` rows with provider names and next actions.
- If a sidecar anchor exists and provider is available, the run must produce `output_ref`、`output_hash` and `anchor_hit` evidence before accepted.
- If the input is direct-text PDF/PPTX/DOCX, extracted text may support source evidence but must not satisfy OCR accepted.

## 4. Final Acceptance Command Plan

```text
PYTHONPATH=backend pytest -q \
  backend/tests/test_v2_116_ocr_anchor_provider_closure.py \
  backend/tests/test_v2_117_source_trace_batch_closure.py \
  backend/tests/test_v2_118_headless_ui_visual_acceptance.py \
  backend/tests/test_v2_119_safe_build_allowlist_governance.py \
  backend/tests/test_v2_120_final_portfolio_acceptance_rerun.py \
  backend/tests/test_public_surface_guard.py

PYTHONPATH=backend python3 -m compileall -q backend/data_service backend/app/api backend/tests
npm --prefix frontend run build
git diff --check
git diff --exit-code -- backend/app/api/v1/data_service.py backend/data_service/service.py
git diff --cached --exit-code -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 5. PRD/spec Review

每个子阶段结束后必须检查：

- 是否仍遵守不声明 full call graph、runtime topology、data/control flow、type inference。
- 是否把 docs claim、drawio、HTML report、mock-only、sample-only 当成 accepted evidence。
- 是否保留 needs_review、structured_unavailable、structured_blocker。
- 是否未修改 protected legacy files。
