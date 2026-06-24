# V2.54-V2.58 Gap Analysis

## 1. Current Accepted Baseline

V2.46-V2.53 已接受：

- MCP Productization。
- Project Profile Onboarding。
- Human Portal。
- Task Navigation。
- Governance Workflow。
- Agent Playbooks。
- Continuous Acceptance Closure。
- Acceptance Infrastructure Hardening。

## 2. Target Gaps

| Gap | Impact | Planned Phase |
| --- | --- | --- |
| Human Portal 可读但项目故事、风险排序和下一步动作不够强 | 维护者仍需读多个 artifact | V2.54 |
| Agent task workflow 仍依赖人工组合 task navigation / playbook / tests | 修改前准备不够稳定 | V2.55 |
| Doc-code governance 有 rule/overlay，但 evidence loop 和 decision history 不够可追踪 | 架构偏差难以长期治理 | V2.56 |
| Continuous acceptance 有 closure matrix，但缺少 artifact diff、trend、failure diagnosis | 回归定位成本高 | V2.57 |
| Restore UX 有命令，但缺少完整 onboarding 和失败诊断 | 新机器迁移仍容易卡在环境问题 | V2.58 |

## 3. Risks

- 过度承诺完整项目理解。
- 把 relationship chain 写成 full call graph。
- 把 impact candidate 写成 runtime call。
- HTML / playbook 美化掉 unresolved、needs_review、contradicted。
- 真实项目 unavailable 被误写 accepted。
- 依赖漂移导致 public surface guard 假失败或假通过。

## 4. Mitigations

- 每个 accepted row 绑定 evidence_refs、artifact path、test command。
- 每阶段执行 focused tests、真实项目 E2E、PRD/spec review、false-green audit。
- 保留 needs_review、structured_unavailable、structured_blocker 作为合法非 accepted 状态。
- Human Portal 只读 persisted artifacts。
- Governance overlay 只读时应用，不改写上游 artifact。
- Restore UX 固化 test dependencies 和 canonical runner。
