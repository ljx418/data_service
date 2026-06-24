# V2.59-V2.62 Development and Acceptance Plan

## 1. 总体执行纪律

每个子阶段执行顺序固定：

1. 根据本 PRD 和目标架构生成 phase development plan。
2. 生成 phase acceptance plan。
3. 生成 phase pre-implementation audit，并关闭 fatal / major finding。
4. 实现代码和 artifact。
5. 运行 focused tests、public surface guard、baseline regression、real E2E。
6. 生成 PRD/spec review。
7. 生成 false-green audit。
8. 生成 acceptance audit。
9. 回填 coverage matrix。

如果真实 E2E 不通过，应回到 development plan，重新评估实现和验收标准；不可用项目只能记录为 `structured_unavailable` 或 `structured_blocker`。

## 2. V2.59 Public Surface Stabilization

开发目标：

- 新增 public surface contract snapshot service。
- 生成 MCP / CLI / HTTP parity matrix。
- 生成 drift report 和 migration notes。
- 将 public surface guard 从“是否存在”扩展到“合同是否稳定、是否可解释迁移”。

目标体验：

- 维护者可以看到当前 public surface 是否稳定。
- Agent 可以知道新增/变更 surface 会触发哪些测试和迁移说明。
- 审计者可以区分 route/tool/command 缺失、命名漂移、schema drift。

验收计划：

- Focused test 覆盖 snapshot、parity、drift、migration note。
- Public surface guard 通过。
- V2.46-V2.58 baseline regression 通过。
- Real data_service E2E 构建并读取 contract artifacts。
- False-green audit 拒绝 snapshot 只来自 hardcoded expected list。

## 3. V2.60 Real Project E2E Expansion

开发目标：

- 扩展 multi-project E2E runner。
- 尝试对 data_service、codexPat、HarnessOS、Navia 运行真实 E2E。
- 对外部项目不可用进行结构化诊断。
- 输出 project matrix、failure diagnosis、artifact availability、E2E report。

目标体验：

- 维护者知道哪些项目真实通过、哪些不可用、不可用原因是什么、下一步怎么处理。
- 不再把“没有跑完整”写成模糊通过。

验收计划：

- data_service 必须 accepted。
- codexPat 尽量 accepted；不可用时必须给结构化原因。
- HarnessOS/Navia 若不可用，必须是 `structured_unavailable` 或 `structured_blocker`，不能 accepted。
- Mock-only evidence 必须被拒绝。
- Failure categories 必须包含 dependency_drift、sandbox_limit、path_unavailable、artifact_missing、public_surface_drift、real_regression、needs_review。

## 4. V2.61 Acceptance Artifact Cleanup and Packaging

开发目标：

- 生成 package manifest。
- 生成 cleanup plan。
- 生成 handoff checklist。
- 生成 package audit report。
- 明确 `.tmp/`、测试依赖、E2E 产物、文档和代码的提交/忽略策略。

目标体验：

- 维护者可以判断当前工作树哪些是阶段交付，哪些是本地临时产物。
- 新接手者可以按 handoff checklist 恢复验收。
- 清理过程不会误删证据或用户文件。

验收计划：

- Focused test 验证 manifest 分类、redaction、cleanup action safety。
- 不自动删除未确认归属的文件。
- Public artifact 不泄露 absolute path、secret、token、raw traceback。
- Handoff checklist 包含 canonical acceptance runner 和 V2.59-V2.62 focused command。

## 5. V2.62 Human Portal UX Integration

开发目标：

- 将 V2.59 contract stability、V2.60 E2E coverage、V2.61 packaging readiness 接入 Portal。
- 生成 portal state summary、sections、acceptance panel 和 project_portal_v3.html。
- 在 Portal 中保留 warnings、unresolved、needs_review、structured_unavailable。

目标体验：

- 维护者打开 Portal 后可以一屏理解：功能是否稳定、E2E 是否覆盖、交付是否干净、下一步动作是什么。
- Agent 可以从 Portal 派生阅读路径、测试路径和 stop condition。

验收计划：

- Focused test 验证 Portal section 只来自 persisted artifacts。
- HTML 不展示 raw Mermaid source。
- Portal 不把 unavailable/needs_review 渲染为 accepted。
- Real data_service E2E 生成可读 portal_v3。
- PRD/spec review 和 false-green audit 必须通过。

## 6. 总阶段出门验收

总阶段完成必须运行：

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_59_public_surface_stabilization.py backend/tests/test_v2_60_real_project_e2e_expansion.py backend/tests/test_v2_61_acceptance_packaging.py backend/tests/test_v2_62_portal_ux_integration.py backend/tests/test_public_surface_guard.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend
git diff --check
git diff --name-only -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

总阶段 acceptance audit 必须列出：

- phase verdict；
- focused test result；
- real E2E result；
- structured_unavailable / structured_blocker 明细；
- PRD/spec review；
- false-green audit；
- protected file diff result；
- residual risk。
