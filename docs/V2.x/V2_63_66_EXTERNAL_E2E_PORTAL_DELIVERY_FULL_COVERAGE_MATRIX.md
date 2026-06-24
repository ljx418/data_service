# V2.63-V2.66 Full Coverage Matrix

当前矩阵是 planning baseline，不是实现完成证据。任何 row 只有在 artifact path、focused test、真实 E2E 或结构化原因、PRD/spec review、false-green audit、acceptance audit 全部存在后，才能从 `planned` 转为 `accepted`。

| Capability | Phase | Planned artifacts | Acceptance status | Required evidence |
| --- | --- | --- | --- | --- |
| External full project matrix | V2.63 | `external_e2e/full_project_matrix.json` | planned | focused test, real project E2E, status classification |
| Project run records | V2.63 | `external_e2e/project_run_records.json` | planned | command, result, repo-relative evidence |
| Artifact readiness | V2.63 | `external_e2e/artifact_readiness.json` | planned | artifact existence/readability checks |
| External E2E report | V2.63 | `external_e2e/external_e2e_report.md` | planned | PRD review, false-green audit |
| Portal V3+ experience model | V2.64 | `portal_v3/experience_model.json` | planned | source artifact refs and unresolved reasons |
| Portal navigation model | V2.64 | `portal_v3/navigation_model.json` | planned | maintainer workflow coverage |
| Portal status panels | V2.64 | `portal_v3/status_panels.json` | planned | E2E/contract/delivery status evidence |
| Portal V3+ HTML | V2.64 | `portal_v3/project_portal_v3_plus.html` | planned | HTML acceptance, no leaked private paths |
| Version manifest | V2.65 | `delivery/version_manifest.json` | planned | git status classification, evidence refs |
| Review package manifest | V2.65 | `delivery/review_package_manifest.json` | planned | commit/manual/local/generated classification |
| Cleanup execution plan | V2.65 | `delivery/cleanup_execution_plan.md` | planned | no automatic deletion, human review flags |
| Delivery audit report | V2.65 | `delivery/delivery_audit_report.md` | planned | PRD review, false-green audit |
| Contract baseline | V2.66 | `contract_regression/contract_baseline.json` | planned | V2.59-V2.62 baseline refs |
| Contract diff | V2.66 | `contract_regression/contract_diff.json` | planned | current MCP/CLI/HTTP/schema snapshot |
| Compatibility report | V2.66 | `contract_regression/compatibility_report.json` | planned | compatibility classification |
| Regression diagnosis | V2.66 | `contract_regression/regression_diagnosis.md` | planned | breaking changes routed to review/blocker |

## Status rules

- `planned`：开发计划存在，但尚无实现证据。
- `accepted`：真实 artifact、测试、E2E/结构化证据、审计报告齐全。
- `needs_review`：需要人工或后续实现判断，不能计入 accepted。
- `structured_unavailable`：环境、路径或依赖不可用，不能计入 accepted。
- `structured_blocker`：阻塞明确且不能绕过，不能计入 accepted。
- `out_of_scope`：明确不属于本阶段。
