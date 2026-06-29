# V2.76-V2.80 Test and E2E Mapping

## 1. Focused Tests

| 阶段 | 计划测试 | 验收重点 |
| --- | --- | --- |
| V2.76 | `backend/tests/test_v2_76_acceptance_matrix_reconciliation.py` | planned/accepted diff、evidence requirement、needs_review |
| V2.77 | `backend/tests/test_v2_77_external_project_real_binding.py` | real path、preflight、structured unavailable/blocker |
| V2.78 | `backend/tests/test_v2_78_ci_warning_reduction.py` | warning owner、budget、release gate |
| V2.79 | `backend/tests/test_v2_79_maintainer_console_productization.py` | panel contract、action registry、non-accepted visibility |
| V2.80 | `backend/tests/test_v2_80_release_readiness_closure.py` | restore、smoke、redaction、approval gate |

## 2. Regression Tests

必须继续运行：

```text
backend/tests/test_v2_71_external_project_binding_closure.py
backend/tests/test_v2_72_ci_warning_governance.py
backend/tests/test_v2_73_agent_long_term_memory_productization.py
backend/tests/test_v2_74_interactive_maintainer_console.py
backend/tests/test_v2_75_release_restore_packaging.py
backend/tests/test_public_surface_guard.py
```

## 3. Real E2E

真实 E2E 必须覆盖：

- 当前 `data_service` 仓库；
- `codexPat`、`HarnessOS`、`Navia`，若路径不可用则 `structured_unavailable`；
- 外部项目路径可用但依赖不可用时 `structured_blocker`；
- 所有 accepted 项必须有真实 artifact 和 test result。

## 4. PRD/spec Review

每个阶段结束后检查：

- 是否满足 PRD 目标体验；
- 是否符合目标架构的实体和边界；
- 是否保留 unresolved；
- 是否有 overclaim；
- 是否触碰 protected legacy 文件。

## 5. False-green Audit

必须拒绝：

- unavailable 计入 accepted；
- warning 被隐藏；
- release readiness 跳过人工审批；
- mock-only evidence accepted；
- HTML/console 硬编码成功状态；
- public artifact 泄露敏感信息。

## 6. Final Command Plan

```text
pytest -q \
  backend/tests/test_v2_76_acceptance_matrix_reconciliation.py \
  backend/tests/test_v2_77_external_project_real_binding.py \
  backend/tests/test_v2_78_ci_warning_reduction.py \
  backend/tests/test_v2_79_maintainer_console_productization.py \
  backend/tests/test_v2_80_release_readiness_closure.py \
  backend/tests/test_public_surface_guard.py
python -m compileall backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```
