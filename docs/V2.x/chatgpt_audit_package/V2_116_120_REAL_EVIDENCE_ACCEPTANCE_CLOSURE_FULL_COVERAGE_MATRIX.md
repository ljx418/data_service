# V2.116-V2.120 Full Coverage Matrix

| ID | PRD 能力 | 阶段 | Planned artifact | 当前状态 | Required evidence before accepted |
| --- | --- | --- | --- | --- | --- |
| REAC-001 | OCR 样本资格 | V2.116 | `ocr_anchor_registry.json` | planned | source ref、sha256、ocr_anchor 或 needs_review reason |
| REAC-002 | OCR provider 执行 | V2.116 | `ocr_provider_execution.json` | planned | `provider_steps[]`、page_outputs、output hash、anchor_hit、failure category |
| REAC-003 | OCR 闭环报告 | V2.116 | `ocr_closure_report.md` | planned | accepted/non-accepted row summary、next action |
| REAC-004 | Source import 验证 | V2.117 | `source_trace_batch_results.json` | planned | import_ref，不允许仅凭文件存在 accepted |
| REAC-005 | Query 结果验证 | V2.117 | `source_trace_evidence_index.json` | planned | source_id、source_content_hash、query_result_source_ids、trace_source_id、same_source_assertion |
| REAC-006 | Source trace 报告 | V2.117 | `source_trace_closure_report.md` | planned | unresolved rows、structured reason |
| REAC-007 | Headless UI 截图 | V2.118 | `ui_screenshot_manifest.json` | planned | screenshot path、sha256、viewport、scenario |
| REAC-008 | UI 捕获诊断 | V2.118 | `ui_capture_results.json` | planned | headless result 或 browser blocker |
| REAC-009 | Build allowlist | V2.119 | `safe_build_allowlist.json` | planned | command_id、approval_status、normalized_binding_digest、sandbox_policy_digest、project_input_hash |
| REAC-010 | Safe build 执行 | V2.119 | `safe_build_execution_results.json` | planned | approved command only、managed sandbox、timeout/cache/log redaction、process cleanup、original project write check |
| REAC-011 | Build 治理报告 | V2.119 | `safe_build_governance_report.md` | planned | skipped/deferred/unavailable 不得 accepted |
| REAC-012 | 人工例外决策 | V2.120 | `decisions/{decision_set_id}.json` + `evidence_decision_snapshot.json` | planned | approver、reason、risk、scope、decision_set_hash、effective/revoked ids、binding validation |
| REAC-013 | Final gate 聚合 | V2.120 | `final_portfolio_acceptance_gate.json` | planned | high-risk 全 accepted 或 approved out_of_scope |
| REAC-014 | False-green audit | V2.120 | `final_portfolio_false_green_audit.md` | planned | 拒绝 HTML/drawio/docs/mock-only 替代证据 |
| REAC-015 | 可读验收报告 | V2.120 | `final_portfolio_acceptance_report.html` | planned | 中文、证据链接、截图或 blocker、出门原因 |
| REAC-016 | 不可变 run lineage | Shared | `runs/{run_id}/input_manifest.json` + `source_run_refs[]` | planned | input hashes、upstream artifact hashes、latest pointer、lineage-bound cross-run validation |
| REAC-017 | 可信决策与审批 | Shared | `decisions/{decision_set_id}.json` + `evidence_decision_snapshot.json` | planned | approver、scope、expiry、revocation、normalized binding digest、decision set hash |
| REAC-018 | Safe build security runtime | V2.119 | `safe_build_execution_results.json` | planned | shell=False、cwd boundary、env redaction、timeout process cleanup |
| REAC-019 | Prototype/headless UX contract | V2.118 | UI selectors and screenshot manifest | planned | stable selectors、DOM assertion、blank/error page rejection |
| REAC-020 | 机器 Schema Bundle | Shared | `V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_SCHEMA_BUNDLE.json` | planned | JSON Schema draft 2020-12、additionalProperties=false、required、schema validation tests |
| REAC-021 | 权威文档包 | Shared | `V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_CONTRACT_BUNDLE_MANIFEST.json` | planned | 文档 sha256、classification、authority_priority、审计包完整性 |

## 状态规则

- `planned`：文档规划完成，代码和真实证据未实现。
- `accepted`：真实资料、真实执行、artifact refs、focused test、E2E、PRD/spec review、false-green audit 全部具备。
- `needs_review`：缺人工判断、OCR anchor、审批或高风险确认。
- `structured_unavailable`：路径、资料、provider、browser 或外部项目不可用，不是 accepted。
- `structured_blocker`：依赖、环境、安全或实现阻断，不是 accepted。
- `failed`：执行失败，不是 accepted。
