# V2.106-V2.110 Full Coverage Matrix

| 能力 | 阶段 | 目标实体 | Planned artifact | 当前状态 | Required evidence |
| --- | --- | --- | --- | --- | --- |
| V2.101-V2.105 状态回填 | V2.106 | Coverage Closure Auditor | `coverage_state_closure.json` | accepted_for_closure_machine | 旧 coverage matrix、acceptance audit、visual report、non-accepted 状态保留 |
| 目标架构状态同步 | V2.106 | Architecture State Closure | `architecture_state_closure.json` | needs_review | drawio/target architecture 标记已实现、待新增、需修改实体；仍需 V2.111-V2.115 同步最新目标 |
| OCR provider 检测 | V2.107 | OCR Evidence Adapter | `ocr_provider_health.json` | structured_unavailable | provider command/API result；缺失时 structured_unavailable |
| Media evidence matrix | V2.107 | Media Evidence Classifier | `media_evidence_matrix.json` | structured_unavailable | image/PDF/PPT rows、format、ocr_required、failure category、next action |
| Full build queue | V2.108 | Full Build Scheduler | `full_build_queue.json` | needs_review | 真实 workspace project rows、queue state、cache policy、timeout policy |
| Project build diagnosis | V2.108 | Project Build Diagnosis | `project_build_diagnosis.json` | needs_review | accepted/build_failed/skipped/timeout/structured_unavailable 分类 |
| Document ingest closure | V2.109 | Source Trace Closure Adapter | `document_source_trace_closure.json` | structured_unavailable | source import command/API result、source refs |
| Query/source trace closure | V2.109 | Source Trace Closure Adapter | `document_source_trace_closure.json` | structured_unavailable | query result refs、source trace refs；缺失不得 accepted |
| UI evidence closure | V2.110 | UI Evidence Capture Adapter | `ui_evidence_capture.json` | structured_unavailable | headless screenshot refs 或 browser dependency structured_unavailable |
| Final release gate | V2.110 | Final Portfolio Release Gate | `final_release_gate.json` | structured_unavailable | project/media/document/UI/public surface statuses、final status |
| False-green recheck | V2.110 | Final Portfolio Release Gate | `false_green_recheck.md` | accepted_for_closure_machine | scan-only、readiness-only、UI-only、OCR、silent skip、docs claim checks |
| Final evidence report | V2.110 | Final Evidence Report Renderer | `final_evidence_report.html` | accepted_for_closure_machine | 中文、可读、证据路径、non-accepted visible、path redaction |

## 状态规则

- `planned`：文档规划完成，代码和证据尚未实现。
- `accepted_for_closure_machine`：闭环机器和报告产物已实现；不等同于 portfolio final accepted。
- `accepted`：真实资料、真实命令/API/MCP/UI 证据、artifact refs、PRD/spec review 和 false-green audit 全部具备。
- `needs_review`：缺人工判断、资料归属或高风险确认。
- `structured_unavailable`：路径、OCR、浏览器、依赖或权限不可用，不是 accepted。
- `structured_blocker`：实现、依赖或环境阻断，不是 accepted。

任何 row 改为 `accepted` 前必须补齐：

- artifact path。
- focused test command and result。
- real workspace E2E result 或 structured unavailable rationale。
- PRD/spec review。
- false-green audit。
- acceptance audit report path。
