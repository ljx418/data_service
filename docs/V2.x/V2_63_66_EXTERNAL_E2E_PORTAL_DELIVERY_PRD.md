# V2.63-V2.66 PRD：外部项目完整 E2E、Portal V3+、交付版本化、Public Surface Contract Regression

## 1. 阶段定位

V2.63-V2.66 承接已验收的 V2.59-V2.62 Stabilization / E2E / Portal 阶段。上一阶段已经完成 public surface 稳定化、真实项目 E2E 扩展、验收打包和 Portal 集成，但仍保留三个明确事实：

- 外部项目 HarnessOS、Navia、codexPat 的可用性和完整 E2E 不能用 `structured_unavailable` 替代 accepted。
- Portal 已能汇总阶段状态，但维护者还需要更直接的“现在能用什么、风险在哪里、下一步怎么做”的体验。
- 工作树和交付包需要进入版本化、合同回归和可审计交付状态，不能依靠人工口头解释。

本阶段目标不是扩大代码理解承诺，而是把已经形成的产品化能力推进到“外部证据更完整、用户体验更清晰、交付边界更稳定、公共合同可回归”的状态。

| 阶段 | 名称 | 核心目标 |
| --- | --- | --- |
| V2.63 | External Project Full E2E | 对 data_service、codexPat、HarnessOS、Navia 执行完整真实项目 E2E，减少或精确解释不可用状态 |
| V2.64 | Portal V3+ Experience Hardening | 让维护者在 Portal 中直接看到目标体验、合同稳定性、外部 E2E、交付状态和下一步动作 |
| V2.65 | Delivery Cleanup and Versioning | 将工作树、文档、测试、验收产物整理为版本化交付包和人工可审查清理计划 |
| V2.66 | Public Surface Contract Regression | 对 MCP、CLI、HTTP、artifact schema 建立跨阶段合同回归和兼容性诊断 |

## 2. 用户问题

当前项目的下一轮开发需要解决：

- 外部项目 E2E 仍存在不可用或局部验收，维护者不能把这些结果当作完整外部验收。
- Portal 的信息密度已经提高，但对非开发维护者仍需要更清晰的目标体验、风险优先级和出门状态。
- 当前工作树包含多阶段新增实现、测试、文档和 `.tmp/`，缺少版本化交付解释和清理边界。
- Public surface 已被 guard 覆盖，但缺少面向回归的跨阶段合同 baseline、diff、兼容性规则和失败分类。

## 3. 目标体验

### 3.1 人类维护者

维护者可以打开 Portal 或阶段验收摘要，直接判断：

- data_service、codexPat、HarnessOS、Navia 哪些项目已经通过真实 E2E，哪些因为路径、依赖、沙箱、artifact 缺失或真实回归不可用；
- 当前 MCP、CLI、HTTP 和 artifact schema 是否与合同一致；
- 当前交付包包含哪些源码、测试、文档、验收报告和本地临时文件处理建议；
- 哪些能力已经 accepted，哪些仍是 `needs_review`、`structured_unavailable` 或 `structured_blocker`；
- 下一步是否可以进入实现、发布、人工复核或需要回到开发计划阶段。

### 3.2 Coding Agent

Agent 在后续开发前可以读取：

- 外部项目 E2E 的真实结果和失败分类；
- 版本化 delivery manifest 和 cleanup plan；
- public surface contract baseline、contract diff、compatibility report；
- Portal V3+ 生成的风险优先级、stop conditions、建议测试和出门状态；
- 明确的禁止事项，避免把文档 claim 写成代码事实，或把不可用状态写成 accepted。

### 3.3 架构审计者

审计者可以检查：

- 目标架构是否仍围绕 persisted artifact、read-only evidence 和 public adapter，而不是改写 legacy 大文件；
- 外部项目 E2E 是否使用真实路径和真实产物；
- Portal 是否完整保留 unresolved、needs_review、structured_unavailable、structured_blocker；
- delivery cleanup 是否只生成计划和版本化解释，不自动删除用户文件；
- contract regression 是否能定位新增、删除、重命名、schema drift、route/tool/command mismatch。

## 4. In Scope

- data_service、codexPat、HarnessOS、Navia 的完整真实项目 E2E 计划、执行记录、失败分类和证据路径。
- Portal V3+ 的维护者首页、状态面板、外部 E2E 面板、合同稳定性面板、交付状态面板、下一步动作。
- delivery version manifest、review package manifest、cleanup execution plan、delivery audit report。
- MCP、CLI、HTTP、artifact schema 的 contract baseline、contract diff、compatibility report、regression diagnosis。
- 每阶段 development plan、acceptance plan、pre-implementation audit、focused tests、真实 E2E、PRD/spec review、false-green audit、acceptance audit。

## 5. Out of Scope

- 不声称完整恢复复杂项目设计意图。
- 不声称 full call graph、runtime topology、data/control flow 或 type inference。
- 不把 documentation claim 当作 code fact。
- 不把 `needs_review`、`structured_unavailable`、`structured_blocker` 写成 accepted。
- 不为了通过验收而伪造外部项目路径、mock-only evidence 或 hardcoded accepted result。
- 不自动删除 `.tmp/` 或任何未确认归属的用户文件。
- 不修改 legacy 大文件 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`，除非用户明确批准。

## 6. 完成定义

V2.63-V2.66 完成必须满足：

1. 每个子阶段开始前都有独立 development plan、acceptance plan、pre-implementation audit，并闭环 fatal/major 审计意见。
2. 每个子阶段结束后都有 focused tests、真实项目 E2E 或结构化不可用、PRD/spec review、false-green audit、acceptance audit。
3. 外部项目 E2E 的 accepted 结果必须绑定真实 artifact、命令、结果和 repo-relative evidence；不可用不能计入 accepted。
4. Portal V3+ 的每个状态项必须有 artifact_ref、evidence_ref 或 unresolved reason。
5. Delivery cleanup 只输出 reviewable plan 和 version manifest，不自动删除用户文件。
6. Public surface contract regression 必须能比较 baseline 与当前 surface，并输出兼容性分类。
7. 出门验收必须包含 V2.46-V2.62 baseline regression、V2.63-V2.66 focused tests、public surface guard、真实项目 E2E、`git diff --check`、protected file diff check。
