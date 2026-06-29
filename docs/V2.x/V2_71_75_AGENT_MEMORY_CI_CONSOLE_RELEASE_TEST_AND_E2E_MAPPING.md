# V2.71-V2.75 Test and E2E Mapping

## 1. Focused Test Map

| Test file | PRD target | Required assertions |
| --- | --- | --- |
| `backend/tests/test_v2_71_external_project_binding_closure.py` | 外部项目真实路径闭环 | `data_service` accepted 有真实 evidence；无路径外部项目 structured unavailable；unavailable 不计 accepted |
| `backend/tests/test_v2_72_ci_warning_governance.py` | CI/warning 治理 | warning budget 生效；失败分类合法；warning 超预算不能 accepted |
| `backend/tests/test_v2_73_agent_long_term_memory_productization.py` | Agent 长期记忆 | memory item 有 source artifact；recommendation 有 evidence 或 needs_review；不声明通用聊天记忆 |
| `backend/tests/test_v2_74_interactive_maintainer_console.py` | 交互式维护者控制台 | panel 有 status/artifact/evidence/unresolved；不隐藏 non-accepted；HTML 不硬编码外部事实 |
| `backend/tests/test_v2_75_release_restore_packaging.py` | 发布恢复打包 | redaction pass；smoke commands 覆盖 MCP/CLI/HTTP/tests；release readiness 不把 unavailable 写 accepted |
| `backend/tests/test_public_surface_guard.py` | Public surface | 新 MCP/CLI/HTTP surface 进入 guard |

## 2. Real Data E2E

Real data E2E 使用当前仓库：

```text
/mnt/c/workspace/data_service
```

必须构建或读取的链路：

```text
codebase import
snapshot
inventory
symbols
trace
overview
Agent context pack
V2.63 external E2E
V2.67 path binding
V2.68 delivery
V2.69 surface baseline
V2.70 dashboard
V2.71 external closure
V2.72 CI governance
V2.73 Agent memory
V2.74 maintainer console
V2.75 release restore
```

## 3. Stage Command Plan

Focused command:

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q \
  backend/tests/test_v2_71_external_project_binding_closure.py \
  backend/tests/test_v2_72_ci_warning_governance.py \
  backend/tests/test_v2_73_agent_long_term_memory_productization.py \
  backend/tests/test_v2_74_interactive_maintainer_console.py \
  backend/tests/test_v2_75_release_restore_packaging.py \
  backend/tests/test_public_surface_guard.py
```

Regression command:

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q \
  backend/tests/test_v2_63_external_project_full_e2e.py \
  backend/tests/test_v2_64_portal_v3_experience.py \
  backend/tests/test_v2_65_delivery_cleanup_versioning.py \
  backend/tests/test_v2_66_public_surface_contract_regression.py \
  backend/tests/test_v2_67_external_repository_path_binding.py \
  backend/tests/test_v2_68_worktree_delivery_consolidation.py \
  backend/tests/test_v2_69_public_surface_baseline_versioning.py \
  backend/tests/test_v2_70_maintainer_home_status_dashboard.py
```

Infrastructure command:

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 4. False-green Rejection

Reject acceptance if:

- External project without real path is accepted.
- HTML/console hides `needs_review`、`structured_unavailable`、`structured_blocker`。
- Memory item has no source artifact and is not marked `needs_review`。
- Warning over budget is accepted without next_action.
- Public artifact contains absolute local path、secret、token、raw traceback、private venv path。
- New public surface is absent from public surface guard.
- Protected legacy files changed without explicit approval.

## 5. Report Requirements

Final acceptance report must include:

- focused command and result；
- regression command and result；
- real `data_service` E2E result；
- external project statuses；
- PRD/spec review；
- false-green audit；
- protected legacy diff check；
- public surface guard result；
- unresolved and next actions。

