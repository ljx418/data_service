# V2.96-V2.100 Test and E2E Mapping

## 1. Focused Tests

计划 focused tests：

```text
backend/tests/test_v2_96_default_cli_gap_closure.py
backend/tests/test_v2_97_route_a_evidence_automation.py
backend/tests/test_v2_98_quality_decision_minimization.py
backend/tests/test_v2_99_external_project_e2e_governance.py
backend/tests/test_v2_100_automated_release_evidence_gate.py
backend/tests/test_public_surface_guard.py
```

## 2. E2E Inputs

| 输入 | 用途 | 不可用处理 |
| --- | --- | --- |
| `docs/V2.x` | Full Corpus、PRD/spec review、文档一致性 | structured_blocker 或 failed |
| `workspace/v2_91_95_real_acceptance_e2e` | 当前 release gate 基线 | structured_blocker |
| `workspace/data_service_docs_demo` | 多产物 workspace 样本 | needs_review |
| Route A 用户真实资料 | V2.97 accepted 前置条件 | needs_review |
| `codexPat`、`HarnessOS`、`Navia` 路径 | V2.99 external E2E | structured_unavailable |
| `docs/present` | 说明材料 | 不计 accepted |

## 3. Acceptance Commands

文档阶段只规划命令，不执行实现验收。实现阶段最终命令应包含：

```text
PYTHONPATH=backend python3 -m pytest -q \
  backend/tests/test_v2_96_default_cli_gap_closure.py \
  backend/tests/test_v2_97_route_a_evidence_automation.py \
  backend/tests/test_v2_98_quality_decision_minimization.py \
  backend/tests/test_v2_99_external_project_e2e_governance.py \
  backend/tests/test_v2_100_automated_release_evidence_gate.py \
  backend/tests/test_public_surface_guard.py

PYTHONPATH=backend python3 -m compileall -q backend/data_service backend/app/api backend/tests

git diff --check

git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 4. PRD / Spec Review

每个阶段验收报告必须说明：

- PRD 目标体验是否被真实 artifact 支撑。
- 是否存在文档 claim 被误当 code fact。
- 是否保留 non-accepted 状态。
- 是否有 mock-only 或 sample-only evidence 被误用。

## 5. False-green Audit

重点拒绝：

- default CLI 未通过却写 CLI accepted。
- Route A 缺真实资料却 accepted。
- Quality 缺 reviewer decision 却 accepted。
- External 缺路径却 accepted。
- Release Gate 缺 human approval 或 dependency hygiene 却 final accepted。
