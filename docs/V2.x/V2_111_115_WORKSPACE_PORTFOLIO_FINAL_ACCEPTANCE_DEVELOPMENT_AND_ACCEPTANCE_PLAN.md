# V2.111-V2.115 Development and Acceptance Plan

## 1. 总体开发策略

本阶段只在完成阶段级 development plan、acceptance plan、pre-implementation audit 后进入代码实现。实现必须按 V2.111 到 V2.115 顺序推进，每个子阶段结束后执行 focused tests、真实 E2E、PRD/spec review 和 false-green audit。

默认实现落点：

```text
backend/data_service/workspace_portfolio_final_acceptance/
```

默认禁止修改：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 2. V2.111 OCR / Media Provider Real Execution Closure

开发目标：

- 读取 V2.106-V2.110 `media_evidence_matrix.json` 和 `ocr_provider_health.json`。
- 扫描 `/mnt/c/workspace` 中的真实图片、扫描 PDF、PPT/PDF/DOCX，先生成 OCR 样本资格结论。
- 对可执行 provider 运行真实 OCR/转换；不可执行时记录 structured unavailable。
- 输出 media execution evidence，不把 readiness、文件存在、PPT/PDF 直接文本抽取当作 OCR accepted。

计划 artifacts：

```text
ocr_sample_qualification.json
media_execution_results.json
media_artifact_manifest.json
```

验收标准：

- 每个 media row 有 execution_status、acceptance_status、provider、input_ref、output_ref 或 unavailable reason。
- `ocr_sample_qualification.json` 必须列出候选样本、来源 ref、格式、hash、样本类型、预期文本锚点来源和资格结论。
- 没有真实文本型图片或扫描件时，OCR 验收结论必须是 `structured_unavailable` 或 `needs_review`，不得 accepted。
- PPT/PDF/DOCX 可直接文本抽取只能计入 conversion/text extraction evidence，不得替代 OCR accepted。
- 缺 provider 或执行失败时不得 accepted。
- OCR 输出必须有 hash、repo/managed-workspace relative artifact ref，并能命中样本资格记录中的文本锚点或给出人工复核 reason。

## 3. V2.112 Document Ingest / Query / Source Trace Full Closure

开发目标：

- 对可抽取文档执行 source import。
- 对 imported source 执行 query。
- 验证 query hit 到 source trace refs 的链路。

计划 artifacts：

```text
source_trace_execution.json
source_trace_audit.json
```

验收标准：

- accepted document row 必须具备 import artifact、query result、source trace refs。
- 缺任一环节时为 `needs_review` 或 `structured_unavailable`。
- 不允许用 document readiness 或文件存在替代 source trace accepted。

## 4. V2.113 Headless UI Evidence Capture Closure

开发目标：

- 对 `/knowledge?view=portfolio` 执行 headless 截图。
- 截图必须覆盖 final evidence panel、phase status、unresolved/no-go 状态。
- 浏览器不可用时输出 structured unavailable，不抢占用户焦点。

计划 artifacts：

```text
ui_evidence_capture.json
ui_screenshot_manifest.json
```

验收标准：

- 截图文件存在并有 hash、viewport、URL、timestamp。
- 截图报告不能遮盖或隐藏 non-accepted 状态。
- 失败时必须记录 browser dependency、命令、stderr 摘要和 next action。

## 5. V2.114 Safe Multi-project Build Runtime Governance

开发目标：

- 生成完整 safe build queue。
- 对允许的项目执行受控 build/readiness command。
- 提供 timeout、cache、retry、resume、日志截断、敏感信息脱敏。

计划 artifacts：

```text
safe_build_queue.json
safe_build_execution.json
build_runtime_diagnosis.json
```

验收标准：

- 队列包含所有 discovered buildable projects。
- 未执行项目必须有 deferred/blocked reason。
- 不运行未批准 shell command。
- timeout 或失败不计 accepted。
- 输出不得包含 secret、token、raw traceback 或本机私有绝对路径。

## 6. V2.115 Final Portfolio Release Gate Rerun and Packaging

开发目标：

- 聚合 V2.111-V2.114 artifacts。
- 重新计算 `portfolio_final_status`。
- 输出 final acceptance report 和 false-green audit。

计划 artifacts：

```text
final_acceptance_gate.json
final_acceptance_false_green_audit.md
final_acceptance_report.html
```

验收标准：

- 所有高风险项 accepted 或 approved out_of_scope 才能 final accepted。
- `needs_review`、`structured_unavailable`、`structured_blocker` 不得计入 accepted。
- report 必须展示目标体验、当前实现、证据路径、阻断项、下一步动作。

## 7. 最终验收命令计划

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

真实 E2E 命令计划：

```text
PYTHONPATH=backend python3 -m data_service portfolio-final-acceptance build \
  --workspace-id v2_111_115_real \
  --root /mnt/c/workspace \
  --max-code-projects 3 \
  --timeout-seconds 120 \
  --headless
```
