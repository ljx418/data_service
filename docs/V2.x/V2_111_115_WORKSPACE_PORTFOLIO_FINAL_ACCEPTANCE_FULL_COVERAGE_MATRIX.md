# V2.111-V2.115 Full Coverage Matrix

| 能力 | 阶段 | 目标实体 | Planned artifact | 当前状态 | Required evidence |
| --- | --- | --- | --- | --- | --- |
| OCR real sample qualification | V2.111 | Media Execution Provider | `ocr_sample_qualification.json` | planned | real workspace sample refs、hash、sample kind、expected text anchor、qualification status |
| OCR provider real execution | V2.111 | Media Execution Provider | `media_execution_results.json` | planned | provider command/API result、output hash、failure category |
| Media artifact manifest | V2.111 | Media Execution Provider | `media_artifact_manifest.json` | planned | input refs、output refs、format、redaction/path policy |
| Document source import closure | V2.112 | Source Trace Closure Runner | `source_trace_execution.json` | planned | source import command/API result、source artifact refs |
| Query/source trace audit | V2.112 | Source Trace Closure Runner | `source_trace_audit.json` | planned | query result refs、source trace refs、missing reason |
| Headless UI screenshot capture | V2.113 | Headless UI Evidence Runner | `ui_evidence_capture.json` | planned | screenshot refs、viewport、URL、hash 或 browser blocker |
| UI screenshot manifest | V2.113 | Headless UI Evidence Runner | `ui_screenshot_manifest.json` | planned | image path refs、hash、scenario、non-accepted visibility |
| Safe full build queue | V2.114 | Safe Project Build Runtime | `safe_build_queue.json` | planned | all buildable projects、queue state、allowlist、cache key |
| Safe build execution | V2.114 | Safe Project Build Runtime | `safe_build_execution.json` | planned | command refs、timeout、exit code、log summary、artifact refs |
| Build runtime diagnosis | V2.114 | Safe Project Build Runtime | `build_runtime_diagnosis.json` | planned | timeout/skipped/failed/unavailable 分类和 next action |
| Final acceptance rerun gate | V2.115 | Final Acceptance Rerun Gate | `final_acceptance_gate.json` | planned | V2.111-V2.114 statuses、final decision、high-risk summary |
| Final false-green audit | V2.115 | Final Acceptance Rerun Gate | `final_acceptance_false_green_audit.md` | planned | OCR/source trace/UI/build/docs claim/bounded build rejection |
| Final acceptance report | V2.115 | Final Acceptance Report Renderer | `final_acceptance_report.html` | planned | 中文、可读、截图/证据路径、阻断项、出门结论 |

## 状态规则

- `planned`：文档规划完成，代码和证据尚未实现。
- `accepted`：真实执行、artifact refs、evidence refs、PRD/spec review、false-green audit 全部具备。
- `needs_review`：缺人工判断、资料归属或高风险确认。
- `structured_unavailable`：OCR、浏览器、依赖、路径、权限不可用，不是 accepted。
- `structured_blocker`：实现、依赖、安全策略或环境阻断，不是 accepted。
- `out_of_scope`：仅在显式审批和证据记录后允许，不自动计入 accepted。

任何 row 改为 `accepted` 前必须补齐：

- artifact path。
- focused test command and result。
- real workspace E2E result 或 structured unavailable rationale。
- PRD/spec review。
- false-green audit。
- acceptance audit report path。

V2.111 OCR 特别规则：

- `ocr_sample_qualification.json` 未确认至少一个真实可 OCR 文本样本时，OCR provider real execution 不得 accepted。
- 直接文本抽取、PPT/PDF conversion、文件存在、provider readiness 均不得替代 OCR 样本资格或 OCR accepted。
