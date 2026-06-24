# V2.63-V2.66 Development and Acceptance Plan

## 1. 总体开发原则

本阶段以真实证据、可读体验、版本化交付和合同回归为主线。每个子阶段必须先完成 development plan、acceptance plan、pre-implementation audit；实现完成后必须完成 focused tests、真实项目 E2E、PRD/spec review、false-green audit、acceptance audit。

任何 fatal 或 major 规格偏差必须在实质开发前闭环。若真实项目不可用，只能记录 `structured_unavailable` 或 `structured_blocker`，不能转写为 accepted。

## 2. V2.63 External Project Full E2E

开发目标：

- 建立 data_service、codexPat、HarnessOS、Navia 的完整 E2E matrix。
- 为每个项目记录路径可用性、依赖状态、artifact readiness、build/read 结果、Portal read 结果。
- 输出 failure diagnosis，区分路径、依赖、沙箱、artifact、public surface、真实回归。

目标体验：

- 维护者可以一眼看到哪些外部项目真的跑通，哪些只是不可用且原因是什么。
- Agent 不能再把外部项目缺失误写成 accepted。

验收计划：

- focused test：`backend/tests/test_v2_63_external_project_full_e2e.py`。
- real E2E：data_service 必须 accepted；codexPat、HarnessOS、Navia 必须 accepted 或 structured_unavailable/structured_blocker 且有原因。
- PRD/spec review：确认外部 E2E 没有 mock-only accepted。
- false-green audit：检查 unavailable、needs_review 没有被计入 accepted。

## 3. V2.64 Portal V3+ Experience Hardening

开发目标：

- 扩展 Portal V3+ 维护者首页、状态面板、风险优先级、合同稳定性、外部 E2E、交付状态和下一步动作。
- 将 V2.54-V2.66 的 evidence、warning、unresolved、acceptance status 统一呈现。

目标体验：

- 维护者无需阅读所有 Markdown，即可判断项目当前可用能力、风险、下一步动作和出门状态。
- Portal 不隐藏 unresolved 或 structured_unavailable。

验收计划：

- focused test：`backend/tests/test_v2_64_portal_v3_experience.py`。
- HTML acceptance：Portal 不展示 raw Mermaid，不泄露 absolute path/secret/token/raw traceback。
- PRD/spec review：确认页面内容来自 persisted artifacts。
- false-green audit：检查 Portal 未将 warning、unresolved 美化成 accepted。

## 4. V2.65 Delivery Cleanup and Versioning

开发目标：

- 生成 version manifest、review package manifest、cleanup execution plan、delivery audit report。
- 对工作树文件分类为 commit_candidate、generated_evidence、local_temp、manual_review、out_of_scope。
- 明确 `.tmp/`、测试依赖、文档、验收产物、源码的交付边界。

目标体验：

- 维护者可以审查“应该提交什么、暂存什么、需要人工确认什么”，不用从 dirty worktree 手工猜测。
- 项目交付状态可复盘、可回滚、可审计。

验收计划：

- focused test：`backend/tests/test_v2_65_delivery_cleanup_versioning.py`。
- cleanup safety：不自动删除用户文件。
- PRD/spec review：确认清理建议不覆盖证据、不删除未确认文件。
- false-green audit：检查 local_temp/manual_review 未被写成 accepted delivery。

## 5. V2.66 Public Surface Contract Regression

开发目标：

- 读取 V2.59-V2.62 baseline 和当前 MCP/CLI/HTTP/artifact schema。
- 生成 contract baseline、contract diff、compatibility report、regression diagnosis。
- 将 breaking change、schema drift、route mismatch、tool mismatch 标为 needs_review 或 structured_blocker。

目标体验：

- 维护者和 Agent 可以在修改 public surface 前知道是否破坏已验收合同。
- 回归失败能定位为兼容新增、破坏删除、重命名、schema 漂移或路由/命令不一致。

验收计划：

- focused test：`backend/tests/test_v2_66_public_surface_contract_regression.py`。
- public surface guard：`pytest -q backend/tests/test_public_surface_guard.py`。
- PRD/spec review：确认合同回归没有把 breaking change 静默通过。
- false-green audit：检查 contract mismatch 必须有 diagnosis 和 next_actions。

## 6. 阶段出门验收

最终出门前必须运行或记录：

```text
pytest -q backend/tests/test_v2_63_external_project_full_e2e.py \
  backend/tests/test_v2_64_portal_v3_experience.py \
  backend/tests/test_v2_65_delivery_cleanup_versioning.py \
  backend/tests/test_v2_66_public_surface_contract_regression.py \
  backend/tests/test_public_surface_guard.py
```

并补充：

- V2.46-V2.62 baseline regression。
- data_service 真实项目 E2E。
- codexPat、HarnessOS、Navia 真实 E2E 或结构化不可用。
- `python -m compileall backend/data_service backend/app/api backend/tests`。
- `git diff --check`。
- protected file diff check。

## 7. 当前文档支撑度评估

本计划完成后，文档对本阶段开发的支撑度目标为：

- 阶段级开发支撑：约 94%。
- 立即进入 V2.63 phase-specific plan/audit 的支撑：约 92%。
- 剩余不确定性：外部项目真实路径和运行依赖必须在 V2.63 开始时重新确认；dirty worktree 清理不能自动执行；contract regression baseline 必须以实际 public surface artifact 为准。
