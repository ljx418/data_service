# V2.116-V2.120 Milestones and Exit Gates

## M1：V2.116 OCR Anchor and Provider Closure

Exit gate:

- `ocr_anchor_registry.json` 存在。
- 每个 OCR accepted row 有 source ref、sha256、anchor、provider output。
- 缺 anchor/provider 的 row 保持 needs_review 或 structured_unavailable。

No-Go:

- PPT/PDF 直接文本抽取替代 OCR accepted。
- Provider readiness 替代 OCR output。

## M2：V2.117 Source Trace Batch Closure

Exit gate:

- `source_trace_batch_results.json` 和 `source_trace_evidence_index.json` 存在。
- Accepted row 具备 import_ref、query_ref、source_trace_refs，并且 import source、query result、trace source 均绑定同一 `source_id` / `source_content_hash`，`same_source_assertion=matched`。

No-Go:

- 文件存在或文档路径存在即 accepted。

## M3：V2.118 Headless UI Visual Acceptance

Exit gate:

- `ui_screenshot_manifest.json` 存在，或 `ui_capture_results.json` 明确 structured browser blocker。
- 截图路径、sha256、viewport、scenario 可复核。
- structured browser blocker 只能支撑 implementation delivery closure，不能支撑 portfolio final accepted。

No-Go:

- HTML report 替代 screenshot evidence。
- 焦点抢占或弹窗未提前告知。

## M4：V2.119 Safe Build Allowlist Governance

Exit gate:

- `safe_build_allowlist.json` 和 `safe_build_execution_results.json` 存在。
- 未批准命令不执行。
- managed sandbox 不存在时真实命令不执行，只能 structured_blocker。
- approval 必须绑定 executable、argv、cwd、env、sandbox、project input、runtime、network 和 output policy 的 normalized binding digest。
- 输出日志截断、脱敏、timeout/cache/retry/resume 可审计。

No-Go:

- 任意执行外部项目 shell script。
- 直接在外部项目目录写入 build/cache/output。
- 用 argv-only digest 作为可信审批。
- 有界 build 冒充全量 accepted。

## M5：V2.120 Final Portfolio Acceptance Rerun

Exit gate:

- `final_portfolio_acceptance_gate.json` 存在。
- `final_portfolio_false_green_audit.md` 存在。
- high-risk 全部 accepted 或 approved out_of_scope，才允许 `portfolio_final_status=accepted`。
- structured_unavailable 或 structured_blocker 不能直接满足 final accepted。
- non-waivable failure 不允许 approved out_of_scope。

No-Go:

- `needs_review`、`structured_unavailable`、`structured_blocker`、`failed` 计入 accepted。
- drawio/docs/HTML/mock-only 替代真实证据。

## Final Release Exit

只有同时满足以下条件，才能声明本阶段出门验收全绿：

1. Focused tests、public surface guard、compileall、frontend build、git diff checks 全部通过。
2. 真实 `/mnt/c/workspace` E2E 有 artifact refs。
3. PRD/spec review 明确通过。
4. False-green audit 明确通过。
5. Protected legacy files 未修改。
6. Final gate 没有未解释 high-risk unresolved。
