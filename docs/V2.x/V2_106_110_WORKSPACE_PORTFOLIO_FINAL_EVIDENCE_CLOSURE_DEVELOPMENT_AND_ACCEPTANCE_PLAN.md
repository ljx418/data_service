# V2.106-V2.110 Development and Acceptance Plan

## 1. Overall Plan

当前文档仅作为后续实现计划，不证明 V2.106-V2.110 已实现。

Detailed execution authority:

- `V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_PHASE_182_186_DETAILED_DEVELOPMENT_AND_ACCEPTANCE_PACKAGE.md`
- `V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_RISK_CLOSURE_AUDIT_REPORT.md`
- `V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_EXTERNAL_AUDIT_RESPONSE_AND_P0_CLOSURE_REPORT.md`
- `V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_ARTIFACT_SCHEMA_AND_ID_CONTRACTS.md`
- `V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_STATUS_ALGEBRA_AND_FINAL_GATE_DECISION_TABLE.md`
- `V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_BUILD_EXECUTION_SECURITY_AND_RUNTIME_SPEC.md`
- `V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_RUN_LINEAGE_PERSISTENCE_AND_STALENESS_SPEC.md`
- `V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_REQUIREMENT_TEST_EVIDENCE_TRACEABILITY_MATRIX.md`
- `V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_BASELINE_EVIDENCE_PACKAGE.md`
- `V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_PUBLIC_SURFACE_INTERFACE_CONTRACT.md`
- `V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_PROTOTYPE_UX_SPEC.md`

Revised readiness:

- Before P0 closure: `pass_with_major_findings`.
- After this document revision: `pass_after_P0_contract_closure` for implementation guidance.
- Direct continuous Phase 182-186 autonomous coding remains not approved until Phase 182 acceptance closes.

阶段入口条件：

- V2.101-V2.105 acceptance audit 已存在。
- V2.101-V2.105 coverage matrix 已回填真实状态。
- 受保护 legacy 文件默认不修改。
- `needs_review`、`structured_unavailable`、`structured_blocker` 不计入 accepted。

## 2. Phase Plan

| Phase | Development Plan | Acceptance Plan |
| --- | --- | --- |
| V2.106 | 读取 V2.101-V2.105 artifacts、验收报告、coverage matrix、drawio，生成 coverage/architecture closure | focused test 验证状态回填，不把 non-accepted 写成 accepted |
| V2.107 | 增加 OCR/provider health、media evidence matrix、media failure categories | 使用真实 media rows；OCR 缺失时必须 structured_unavailable |
| V2.108 | 增加 full build queue、cache/timeout policy、project build diagnosis | 真实 `/mnt/c/workspace` 多项目调度；失败隔离，不 silent skip |
| V2.109 | 增加 document source trace closure，绑定 ingest/query/source trace evidence | accepted 文档必须有 source refs、query refs、trace refs |
| V2.110 | 增强 final release gate 和 false-green recheck | 高风险项全部 accepted 或结构化阻断；否则 final non-accepted |

## 3. Shared Acceptance Rules

- 每个 phase 开始前必须有 phase-specific development plan、acceptance plan、pre-implementation audit。
- 每个 phase 结束后必须有 focused tests、真实 workspace E2E、PRD/spec review、false-green audit、acceptance audit report。
- `portfolio_final_status=accepted` 只能在所有高风险项 accepted 或明确 out_of_scope 且有证据时出现。
- OCR、source trace、UI evidence 不可用时必须结构化输出，不允许伪造。

## 4. Exit Criteria

文档阶段出门条件：

- 所有 V2.106-V2.110 文档已落盘。
- drawio 中文、页数不超过 8、XML parse 通过。
- coverage matrix 和目标架构不再把已实现实体写作 planned。
- pre-implementation audit fatal/major 为 none。
- document audit 结论为 `pass for implementation guidance, not pass for implementation acceptance`。
- risk closure audit 结论为 residual risks manageable by strict evidence closure route。
- external audit response confirms P0 contract gaps are closed for guidance, not implementation acceptance。
