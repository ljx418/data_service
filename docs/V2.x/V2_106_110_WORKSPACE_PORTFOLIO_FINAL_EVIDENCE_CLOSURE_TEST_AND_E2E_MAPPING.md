# V2.106-V2.110 Test and E2E Mapping

## 1. Focused Tests

计划 focused tests：

```text
backend/tests/test_v2_106_portfolio_coverage_state_closure.py
backend/tests/test_v2_107_ocr_media_evidence_closure.py
backend/tests/test_v2_108_full_workspace_build_governance.py
backend/tests/test_v2_109_document_source_trace_closure.py
backend/tests/test_v2_110_portfolio_final_release_gate.py
backend/tests/test_public_surface_guard.py
```

## 2. Real E2E Inputs

| 输入 | 用途 | 不可用处理 |
| --- | --- | --- |
| `/mnt/c/workspace` | 真实项目组合扫描和 build queue | structured_blocker |
| `/mnt/c/workspace/data_service` | 强制代码项目样本 | failed 或 structured_blocker |
| `/mnt/c/workspace/codexPat` | 外部代码项目样本 | structured_unavailable |
| `/mnt/c/workspace/harnessOS` | 外部代码项目样本 | structured_unavailable |
| `/mnt/c/workspace/navia` | 外部代码项目样本 | structured_unavailable |
| `/mnt/c/workspace/技术分享` | PPT/PDF/DOCX/media 样本 | needs_review 或 structured_unavailable |
| `/mnt/c/workspace/1-AI教案` | docs/images 样本 | needs_review 或 structured_unavailable |
| `/mnt/c/workspace/我在城市的深海里漂流` | 文档/图片资料样本 | needs_review 或 structured_unavailable |

## 3. Acceptance Commands

实现阶段最终命令应包含：

```text
PYTHONPATH=backend python3 -m pytest -q \
  backend/tests/test_v2_106_portfolio_coverage_state_closure.py \
  backend/tests/test_v2_107_ocr_media_evidence_closure.py \
  backend/tests/test_v2_108_full_workspace_build_governance.py \
  backend/tests/test_v2_109_document_source_trace_closure.py \
  backend/tests/test_v2_110_portfolio_final_release_gate.py \
  backend/tests/test_public_surface_guard.py

PYTHONPATH=backend python3 -m compileall -q backend/data_service backend/app/api backend/tests

npm --prefix frontend run build

git diff --check

git diff --exit-code -- backend/app/api/v1/data_service.py backend/data_service/service.py

git diff --cached --exit-code -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

真实 E2E 命令计划：

```text
PYTHONPATH=backend python3 -m data_service portfolio-final-evidence plan \
  --workspace-id v2_106_110_real \
  --root /mnt/c/workspace

PYTHONPATH=backend python3 -m data_service portfolio-final-evidence build \
  --workspace-id v2_106_110_real \
  --root /mnt/c/workspace \
  --max-code-projects 3 \
  --timeout-seconds 120

PYTHONPATH=backend python3 -m data_service portfolio-final-evidence read \
  --workspace-id v2_106_110_real

PYTHONPATH=backend python3 -m data_service portfolio-final-evidence report \
  --workspace-id v2_106_110_real
```

Bounded build assertions:

- Queue must include every discovered buildable project.
- `--max-code-projects 3` limits actual execution only; it must not remove other projects from queue.
- Deferred projects must be marked `deferred_by_limit` and `needs_review`.
- A bounded run cannot produce `portfolio_final_status=accepted` unless all high-risk deferred rows are approved out of scope with evidence.

Requirement-to-test traceability is governed by:

```text
V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_REQUIREMENT_TEST_EVIDENCE_TRACEABILITY_MATRIX.md
```

## 4. Headless UI Acceptance

优先使用 headless browser：

- 打开 `/knowledge?view=portfolio`。
- 截取 portfolio status header。
- 截取 project build queue/diagnosis。
- 截取 media evidence/OCR gap。
- 截取 document source trace closure。
- 截取 final release gate。

如果浏览器或系统库不可用，必须生成 `ui_evidence_capture.json`，状态为 `structured_unavailable`，说明缺失依赖和 next action。不得伪造截图。

## 5. PRD / Spec Review

每个阶段验收报告必须说明：

- PRD 目标体验是否被真实 artifact 支撑。
- 是否仍有 docs claim 被误当 code fact。
- 是否保留 OCR、路径、权限、人工确认的 non-accepted 状态。
- 是否有 mock-only、sample-only、UI-only evidence 被误用。
- 是否明确区分 `implementation_status` 与 `portfolio_final_status`。
