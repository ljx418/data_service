# V2.116-V2.120 Implementation Blueprint and Acceptance Spec

## 1. 建议代码落点

```text
backend/data_service/workspace_portfolio_real_evidence_acceptance/
  __init__.py
  shared.py
  persistence.py
  service.py
  ocr_anchor.py
  ocr_provider.py
  source_trace_batch.py
  ui_capture.py
  safe_build.py
  decisions.py
  release_gate.py
```

Public adapters：

```text
backend/data_service/cli_portfolio_real_evidence.py
backend/data_service/mcp_workspace_portfolio_real_evidence_tools.py
backend/app/api/v1/workspace_portfolio_real_evidence.py
```

Protected legacy files：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

默认不得修改 protected legacy files，除非用户明确批准。

## 2. 共享行为

- `plan` 只生成计划和 unresolved，不执行 OCR、browser 或 build。
- `build` 生成 artifacts，并复用 V2.111-V2.115 artifacts 作为输入。
- `read` 只读取 persisted artifacts，不重新制造事实。
- `report` 只从 persisted artifacts 生成 HTML/Markdown 报告。
- `/knowledge` 本阶段只读展示 evidence，不直接写 anchor、approval、revoke 或 approved out-of-scope。
- Safe build 真执行需要可信 decision set 和 managed sandbox；缺任一条件时只输出 proposal 和 structured_blocker。
- 所有 public output 使用 repo-relative 或 workspace-relative path，不暴露 token、secret、raw traceback、private venv path。

## 3. 阶段实现规格

V2.116：

- 输入：`ocr_sample_qualification.json`、`media_execution_results.json`。
- 输出：`ocr_anchor_registry.json`、`ocr_provider_execution.json`、`ocr_closure_report.md`。
- 验收：OCR accepted 必须有 source ref、file hash、anchor、provider result；缺 anchor 保持 needs_review。

V2.116 OCR provider implementation details:

- `ocr_anchor.py` 扫描 V2.111 候选文件和 sidecar anchor：
  - `file.png.ocr-anchor.txt`
  - `file.ocr-anchor.txt`
- `ocr_provider.py` 只检测和调用本地依赖，不自动安装：
  - image OCR：`tesseract`
  - scanned PDF rasterize：`pdftoppm`/Poppler
  - PPT/PPTX conversion：`soffice`/LibreOffice
- Provider execution 必须记录：
  - `provider_steps[]`
  - 每步 `provider_name`、`provider_version`
  - 每步 `command_ref` 或脱敏后的 command array
  - 每步 `input_ref`、`input_hash`
  - 每步 `output_ref`、`output_hash`
  - 页码或 slide 编号、语言包、资源限制
  - `anchor_text`
  - `anchor_text_hash`
  - `anchor_hit`
  - `failure_category`
- `accepted` 条件：
  - sample qualification 为 accepted。
  - provider health accepted。
  - execution_status 为 succeeded。
  - output_hash 存在。
  - anchor_hit 为 true，或有 approved human confirmation。
- 缺依赖时：
  - `tesseract` 缺失 -> OCR row `structured_unavailable`。
  - `pdftoppm` 缺失 -> scanned PDF row `structured_unavailable`。
  - `soffice` 缺失 -> PPT/PPTX image route `structured_unavailable`。
  - 直接文本抽取只可输出 source evidence，不得让 OCR row accepted。

V2.117：

- 输入：V2.111 source trace artifacts、source registry/query capabilities。
- 输出：`source_trace_batch_results.json`、`source_trace_evidence_index.json`、`source_trace_closure_report.md`。
- 验收：文件存在不能单独 accepted；accepted 必须满足：
  - `import_ref` resolves to `source_id`。
  - imported source hash equals `source_content_hash`。
  - `source_content_hash` matches input manifest。
  - `source_id` is in `query_result_source_ids`。
  - `trace_source_id == source_id`。
  - `trace_evidence_refs` non-empty。
  - `same_source_assertion=matched`。

V2.118：

- 输入：`/knowledge` route 或 final report path。
- 输出：`ui_capture_results.json`、`ui_screenshot_manifest.json`。
- 验收：优先 headless；不能焦点抢占；截图不可用时 structured_blocker。

V2.119：

- 输入：`safe_build_queue.json`、project manifests、approval policy。
- 输出：`safe_build_allowlist.json`、`safe_build_execution_results.json`、`safe_build_governance_report.md`。
- 验收：未批准命令不执行；无 managed sandbox 时真实命令不执行；stdout/stderr 截断脱敏；timeout/cache/retry/resume、process tree cleanup 和 original project write check 可审计；normalized binding digest 必须覆盖 executable、argv、cwd、env、sandbox、project input、runtime、network 和 output policy。

V2.120：

- 输入：V2.116-V2.119 artifacts。
- 输出：`final_portfolio_acceptance_gate.json`、`final_portfolio_false_green_audit.md`、`final_portfolio_acceptance_report.html`。
- 验收：high-risk 全部 accepted 或有效且非安全类 approved out_of_scope 才能 final accepted；non-waivable failure 不得豁免。
