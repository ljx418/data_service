# V2.111-V2.115 Test and E2E Mapping

## 1. Focused Tests

计划 focused tests：

```text
backend/tests/test_v2_111_ocr_media_provider_execution.py
backend/tests/test_v2_112_source_trace_full_closure.py
backend/tests/test_v2_113_headless_ui_evidence.py
backend/tests/test_v2_114_safe_multi_project_build_runtime.py
backend/tests/test_v2_115_final_acceptance_gate.py
backend/tests/test_public_surface_guard.py
```

## 2. Real E2E Inputs

| 输入 | 用途 | 不可用处理 |
| --- | --- | --- |
| `/mnt/c/workspace` | 真实项目组合扫描、media、source trace、build queue | structured_blocker |
| `/mnt/c/workspace/data_service` | 强制代码项目样本和 `/knowledge` UI | failed 或 structured_blocker |
| `v2_106_110_real/portfolio_final_evidence/final_release_gate.json` | 上一阶段真实 gate 输入 | structured_blocker |
| `v2_106_110_real/portfolio_final_evidence/media_evidence_matrix.json` | V2.111 media 输入 | structured_blocker |
| `v2_106_110_real/portfolio_final_evidence/document_source_trace_closure.json` | V2.112 source trace 输入 | structured_blocker |
| `/mnt/c/workspace/技术分享` | PPT/PDF/DOCX/media 样本 | needs_review 或 structured_unavailable |
| `/mnt/c/workspace/1-AI教案` | docs/images 样本 | needs_review 或 structured_unavailable |
| `/mnt/c/workspace/**` 中真实图片或扫描件 | OCR 样本资格确认 | 缺真实文本型 OCR 样本时 `structured_unavailable` |

## 3. Requirement-To-Test Mapping

| Requirement | Focused test | 必须断言 |
| --- | --- | --- |
| OCR 样本资格必须真实 | `test_v2_111_ocr_media_provider_execution.py` | no qualified OCR sample -> OCR not accepted |
| OCR 缺失不得 accepted | `test_v2_111_ocr_media_provider_execution.py` | missing provider -> structured_unavailable |
| OCR 输出必须有 hash | `test_v2_111_ocr_media_provider_execution.py` | accepted media row has output_ref and hash |
| 直接文本抽取不得冒充 OCR | `test_v2_111_ocr_media_provider_execution.py` | PDF/PPT text extraction row cannot satisfy OCR accepted |
| Source trace 三段链路 | `test_v2_112_source_trace_full_closure.py` | import/query/source_trace 任一缺失不得 accepted |
| UI 截图真实存在 | `test_v2_113_headless_ui_evidence.py` | screenshot hash 或 browser structured_unavailable |
| 多项目队列完整 | `test_v2_114_safe_multi_project_build_runtime.py` | all discovered buildable projects in queue |
| 未批准命令不执行 | `test_v2_114_safe_multi_project_build_runtime.py` | command allowlist enforced |
| Final gate 不 false-green | `test_v2_115_final_acceptance_gate.py` | unresolved high-risk -> final not accepted |

## 4. Acceptance Commands

```text
PYTHONPATH=backend python3 -m pytest -q \
  backend/tests/test_v2_111_ocr_media_provider_execution.py \
  backend/tests/test_v2_112_source_trace_full_closure.py \
  backend/tests/test_v2_113_headless_ui_evidence.py \
  backend/tests/test_v2_114_safe_multi_project_build_runtime.py \
  backend/tests/test_v2_115_final_acceptance_gate.py \
  backend/tests/test_public_surface_guard.py

PYTHONPATH=backend python3 -m compileall -q backend/data_service backend/app/api backend/tests

npm --prefix frontend run build

git diff --check

git diff --exit-code -- backend/app/api/v1/data_service.py backend/data_service/service.py
git diff --cached --exit-code -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 5. False-Green Rejection

必须拒绝：

- OCR/provider readiness 替代 OCR result。
- PPT/PDF/DOCX 直接文本抽取替代 OCR 样本资格或 OCR result。
- 无真实 OCR 文本样本却声明 V2.111 OCR accepted。
- source file exists 替代 source import/query/source trace。
- HTML report 替代 UI screenshot。
- 有界 build 替代全量 queue closure。
- docs claim 替代 code/source evidence。
- 把 `needs_review`、`structured_unavailable`、`structured_blocker` 计入 accepted。
