# V2.111-V2.115 Milestones and Exit Gates

## M0：文档开发出门

必须满足：

- PRD、目标架构、开发验收计划、coverage matrix、test/E2E mapping、gap analysis、pre-implementation audit、drawio 全部落盘。
- drawio 页数不超过 8，中文书写，覆盖目标体验、架构差异、实体关系、证据流、开发验收、里程碑、No-Go。
- 文档明确当前状态：`pass for implementation guidance`，not implementation acceptance。

## M1：V2.111 OCR / Media Execution

出门条件：

- `media_execution_results.json` 和 `media_artifact_manifest.json` 生成。
- `ocr_sample_qualification.json` 生成，并明确是否存在真实可 OCR 文本样本。
- 至少对真实 `/mnt/c/workspace` media rows 执行 provider 检测。
- 有 provider 时输出真实 result hash；无 provider 时 structured unavailable。
- OCR/provider readiness 不得替代 OCR result。
- 直接文本抽取不得替代 OCR result；缺真实 OCR 样本时不得 OCR accepted。

## M2：V2.112 Source Trace Closure

出门条件：

- `source_trace_execution.json` 和 `source_trace_audit.json` 生成。
- accepted document row 必须具备 import artifact、query result、source trace refs。
- 缺任一环节不得 accepted。

## M3：V2.113 Headless UI Evidence

出门条件：

- `ui_evidence_capture.json` 和 `ui_screenshot_manifest.json` 生成。
- 成功时有截图 hash、URL、viewport、scenario。
- 失败时有 browser dependency 诊断和 next action。
- 不使用会抢占焦点的可见浏览器，除非提前告知用户。

## M4：V2.114 Safe Build Runtime

出门条件：

- `safe_build_queue.json`、`safe_build_execution.json`、`build_runtime_diagnosis.json` 生成。
- 队列覆盖全部 discovered buildable projects。
- allowlist、timeout、cache、独立 output/cache、日志截断、敏感信息脱敏均有证据。
- 未执行、超时、失败、不可用项目不得 accepted。

## M5：V2.115 Final Acceptance Gate

出门条件：

- `final_acceptance_gate.json`、`final_acceptance_false_green_audit.md`、`final_acceptance_report.html` 生成。
- final gate 聚合 V2.111-V2.114 artifacts。
- 所有高风险项 accepted 或 approved out_of_scope 后才允许 `portfolio_final_status=accepted`。
- public surface guard、focused tests、compileall、frontend build、diff checks 全部通过。

## Final No-Go

任一情况出现时不得声明最终验收通过：

- OCR/source trace/UI/build 任一高风险项仍为 `needs_review`、`structured_unavailable`、`structured_blocker`。
- OCR 只有 provider readiness、直接文本抽取或文件存在，没有真实 OCR 样本资格和 OCR 输出证据。
- drawio 与实现状态明显不一致。
- promised artifact 未生成。
- focused tests 或 public surface guard 阻塞。
- protected legacy file 被修改且无明确批准。
- report 隐藏 non-accepted 状态。
