# V2.63-V2.66 Phase 139-142 Detailed Implementation Package

## 1. 文档定位

本文是 V2.63-V2.66 的详细开发及验收执行包，用于把 PRD、目标架构、drawio、schema contract 转成可实施的子阶段计划。本文不是实现完成证据。

阶段编号：

| Version | Phase | Name |
| --- | --- | --- |
| V2.63 | Phase 139 | External Project Full E2E |
| V2.64 | Phase 140 | Portal V3+ Experience Hardening |
| V2.65 | Phase 141 | Delivery Cleanup and Versioning |
| V2.66 | Phase 142 | Public Surface Contract Regression |

## 2. 共享执行循环

每个子阶段按同一顺序执行：

1. 写入或更新 phase-specific development plan。
2. 写入或更新 phase-specific acceptance plan。
3. 执行 pre-implementation audit，fatal/major 必须闭环。
4. 实现 build/read 能力和 persisted artifacts。
5. 运行 focused tests。
6. 执行真实项目 E2E 或记录结构化不可用。
7. 执行 PRD/spec review。
8. 执行 false-green audit。
9. 写入 acceptance audit report。
10. 通过则进入下一阶段，不通过则打回本阶段计划。

共享禁止事项：

- 不修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`，除非用户明确批准。
- 不把 `needs_review`、`structured_unavailable`、`structured_blocker` 写成 accepted。
- 不把 documentation claim 当作 code fact。
- 不声称 full call graph、runtime topology、data/control flow、type inference 或完整设计意图恢复。
- 不自动删除用户文件。

## 3. Phase 139 / V2.63 External Project Full E2E

### 3.1 Development plan

实现模块：

```text
backend/data_service/code_assets/external_e2e_portal_delivery/external_e2e.py
backend/data_service/code_assets/external_e2e_portal_delivery/persistence.py
backend/data_service/code_assets/external_e2e_portal_delivery/shared.py
```

实现步骤：

1. 定义 project registry：data_service、codexPat、HarnessOS、Navia。
2. 为每个项目执行 path/dependency/permission preflight。
3. 对可用项目执行 artifact build/read、Portal read、contract read、restore/readiness read。
4. 生成 failure diagnosis，分类为 dependency_drift、sandbox_limit、path_unavailable、artifact_missing、public_surface_drift、real_regression、needs_review。
5. 写入 external_e2e artifacts。

目标 artifacts：

```text
external_e2e/full_project_matrix.json
external_e2e/project_run_records.json
external_e2e/artifact_readiness.json
external_e2e/external_e2e_report.md
```

### 3.2 Acceptance plan

必测：

```text
pytest -q backend/tests/test_v2_63_external_project_full_e2e.py
```

验收门槛：

- data_service 必须 accepted。
- codexPat、HarnessOS、Navia 必须 accepted 或 structured_unavailable/structured_blocker，且不可用不计 accepted。
- 每个 project row 必须有 evidence_refs 或 unresolved reason。
- mock-only evidence 不能 accepted。

PRD/spec review：

- 外部项目不可用是否被正确保留。
- 失败分类是否能指导下一步。
- 是否没有夸大为完整外部项目验收。

False-green audit：

- 检查 accepted count 是否排除了 structured_unavailable/structured_blocker/needs_review。
- 检查 report 是否没有把路径缺失写成通过。

## 4. Phase 140 / V2.64 Portal V3+ Experience Hardening

### 4.1 Development plan

实现模块：

```text
backend/data_service/code_assets/external_e2e_portal_delivery/portal_v3.py
```

实现步骤：

1. 读取 V2.54-V2.66 persisted artifacts。
2. 生成 experience_model：维护者首页回答“能用什么、风险在哪、下一步做什么、是否能出门”。
3. 生成 navigation_model：阶段总览、外部 E2E、合同、交付、风险、出门状态。
4. 生成 status_panels：每个面板包含 status、artifact_ref、evidence_ref、unresolved、next_action。
5. 生成 `project_portal_v3_plus.html`，HTML 只展示结构化 artifact，不硬编码结论。

目标 artifacts：

```text
portal_v3/experience_model.json
portal_v3/navigation_model.json
portal_v3/status_panels.json
portal_v3/project_portal_v3_plus.html
```

### 4.2 Acceptance plan

必测：

```text
pytest -q backend/tests/test_v2_64_portal_v3_experience.py
```

验收门槛：

- Portal 首页必须包含阶段总览、外部 E2E、合同稳定性、交付状态、风险与下一步、出门条件。
- 每个面板必须有 evidence_ref、artifact_ref 或 unresolved reason。
- `needs_review`、`structured_unavailable`、`structured_blocker` 必须可见。
- HTML 不泄露 absolute path、secret、token、raw traceback。

PRD/spec review：

- 维护者是否可以不翻完整 docs 目录就判断状态。
- Portal 是否只读 persisted artifacts。

False-green audit：

- 检查 HTML 是否隐藏坏消息。
- 检查无证据状态是否被显示为 accepted。

## 5. Phase 141 / V2.65 Delivery Cleanup and Versioning

### 5.1 Development plan

实现模块：

```text
backend/data_service/code_assets/external_e2e_portal_delivery/delivery.py
```

实现步骤：

1. 读取 git status、阶段文档、测试文件、验收报告和 artifact 目录。
2. 将文件分类为 commit_candidate、generated_evidence、local_temp、manual_review、out_of_scope。
3. 生成 version manifest 和 review package manifest。
4. 生成 cleanup execution plan，所有 `safe_to_delete` 默认 false。
5. 生成 delivery audit report。

目标 artifacts：

```text
delivery/version_manifest.json
delivery/review_package_manifest.json
delivery/cleanup_execution_plan.md
delivery/delivery_audit_report.md
```

### 5.2 Acceptance plan

必测：

```text
pytest -q backend/tests/test_v2_65_delivery_cleanup_versioning.py
```

验收门槛：

- 每个 dirty worktree 条目有分类和原因。
- `.tmp/` 和本地临时文件只能进入 local_temp/manual_review，不自动删除。
- 验收证据不能被 cleanup plan 标为可删。
- public output 不含 absolute path、secret、token、raw traceback。

PRD/spec review：

- 交付包是否能让维护者判断提交、保留、复核边界。
- 是否仍保留验收证据。

False-green audit：

- 检查 cleanup plan 没有自动删除动作。
- 检查 local_temp/manual_review 未被写成 accepted delivery。

## 6. Phase 142 / V2.66 Public Surface Contract Regression

### 6.1 Development plan

实现模块：

```text
backend/data_service/code_assets/external_e2e_portal_delivery/contract_regression.py
```

实现步骤：

1. 读取 V2.59-V2.62 contract snapshot。
2. 读取当前 MCP、CLI、HTTP、artifact schema surface。
3. 生成 contract baseline、contract diff。
4. 对变化执行 compatibility classification。
5. 将 breaking_removal、breaking_rename、schema_drift、route_mismatch、tool_command_mismatch 标记为 breaking 或 needs_review。
6. 生成 regression diagnosis 和 next_actions。

目标 artifacts：

```text
contract_regression/contract_baseline.json
contract_regression/contract_diff.json
contract_regression/compatibility_report.json
contract_regression/regression_diagnosis.md
```

### 6.2 Acceptance plan

必测：

```text
pytest -q backend/tests/test_v2_66_public_surface_contract_regression.py \
  backend/tests/test_public_surface_guard.py
```

验收门槛：

- baseline/current 均来自真实 adapter 或 persisted artifact。
- contract diff 必须覆盖 MCP、CLI、HTTP、artifact schema。
- compatible change 和 breaking change 必须区分。
- breaking change 不能静默 accepted。

PRD/spec review：

- 合同回归是否能帮助 Agent 修改前识别风险。
- 是否没有把 public surface 文档当作代码事实。

False-green audit：

- 检查 breaking change 是否进入 needs_review 或 structured_blocker。
- 检查 schema drift 是否有 diagnosis。

## 7. 阶段最终验收命令

```text
pytest -q backend/tests/test_v2_63_external_project_full_e2e.py \
  backend/tests/test_v2_64_portal_v3_experience.py \
  backend/tests/test_v2_65_delivery_cleanup_versioning.py \
  backend/tests/test_v2_66_public_surface_contract_regression.py \
  backend/tests/test_public_surface_guard.py
```

补充命令：

```text
python -m compileall backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

最终 acceptance audit 必须汇总：

- focused tests。
- data_service 真实 E2E。
- codexPat、HarnessOS、Navia accepted 或结构化不可用。
- PRD/spec review。
- false-green audit。
- public surface guard。
- protected file diff check。
