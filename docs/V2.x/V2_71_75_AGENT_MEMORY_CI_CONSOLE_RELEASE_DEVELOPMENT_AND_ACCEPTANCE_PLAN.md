# V2.71-V2.75 Development and Acceptance Plan

## 1. 开发计划

### V2.71 External Project Binding Closure

目标效果：

- 维护者能看到每个外部项目是否有真实路径、是否可读、是否完成真实 E2E，以及不可用原因。

计划开发：

- 新增 external closure service，读取 V2.63/V2.67 artifact。
- 支持 data_service 当前仓库真实路径。
- 对 `codexPat`、`HarnessOS`、`Navia` 保留结构化不可用，直到真实路径存在。

验收：

- `data_service` accepted 必须绑定真实 artifact。
- 外部项目无路径时必须是 `structured_unavailable` 或 `structured_blocker`。
- 不可用项目不能计入 accepted。

### V2.72 CI and Warning Governance

目标效果：

- 维护者能看到测试分组、慢测试、warning budget、失败归因和 CI readiness。

计划开发：

- 输出 CI matrix、warning budget、failure diagnosis、CI readiness report。
- 保留慢测试和 warning 为可治理项，不通过删除覆盖制造 false green。

验收：

- warning 超预算时不能 accepted。
- 失败归因必须区分 dependency drift、sandbox limit、artifact missing、public surface drift、real regression、needs_review。
- public surface guard 保持在最终验收命令中。

### V2.73 Agent Long-term Memory Productization

目标效果：

- Agent 能读取项目长期记忆索引、证据索引、验收状态和任务简报。

计划开发：

- 输出 memory index、evidence index、acceptance state、task briefing、retention policy。
- 仅引用 persisted artifacts。
- 所有 recommendation 必须有 evidence refs 或 `needs_review`。

验收：

- memory artifact 不包含无证据事实。
- 不声称通用聊天长期记忆；只覆盖项目情报长期记忆。
- 过期、缺证据、弱证据必须可见。

### V2.74 Interactive Maintainer Console

目标效果：

- 维护者打开一个控制台 HTML 或等价 artifact，能快速判断项目状态、风险、下一步和出门条件。

计划开发：

- 输出 console model、navigation model、status panels、maintainer console HTML。
- 面板覆盖 external closure、CI governance、agent memory、surface baseline、release restore。

验收：

- 每个面板有 status、artifact_ref、evidence_ref 或 unresolved reason。
- 控制台不能隐藏 non-accepted 状态。
- HTML 不硬编码 artifact 外事实。

### V2.75 Release and Restore Packaging

目标效果：

- 维护者可以按 runbook 恢复本地能力、配置 MCP、运行 smoke test，并判断能否发布。

计划开发：

- 输出 release manifest、MCP config template、smoke commands、restore runbook、release readiness report。
- 做 public artifact redaction 规则。

验收：

- restore runbook 可在干净本地环境按步骤执行。
- smoke commands 覆盖 MCP、CLI、HTTP 和 focused tests。
- public artifact 不泄露本地绝对路径、secret、token、raw traceback 或 private venv path。

## 2. 总体验收命令计划

后续实现阶段计划新增：

```text
pytest -q \
  backend/tests/test_v2_71_external_project_binding_closure.py \
  backend/tests/test_v2_72_ci_warning_governance.py \
  backend/tests/test_v2_73_agent_long_term_memory_productization.py \
  backend/tests/test_v2_74_interactive_maintainer_console.py \
  backend/tests/test_v2_75_release_restore_packaging.py \
  backend/tests/test_public_surface_guard.py
```

回归命令计划：

```text
pytest -q backend/tests/test_v2_63_external_project_full_e2e.py \
  backend/tests/test_v2_64_portal_v3_experience.py \
  backend/tests/test_v2_65_delivery_cleanup_versioning.py \
  backend/tests/test_v2_66_public_surface_contract_regression.py \
  backend/tests/test_v2_67_external_repository_path_binding.py \
  backend/tests/test_v2_68_worktree_delivery_consolidation.py \
  backend/tests/test_v2_69_public_surface_baseline_versioning.py \
  backend/tests/test_v2_70_maintainer_home_status_dashboard.py
python -m compileall backend/data_service backend/app/api backend/tests
git diff --check
git diff -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 3. 审计意见

当前文档阶段可进入 implementation planning，但不能进入 implementation acceptance。开始写代码前仍必须生成每个子阶段的 development plan、acceptance plan、pre-implementation audit，并关闭 fatal/major 审计意见。

