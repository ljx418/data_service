# V2.63-V2.66 Gap Analysis

## 1. 当前架构与目标架构差异

| 领域 | 当前状态 | 目标状态 | 差距 |
| --- | --- | --- | --- |
| 外部项目 E2E | data_service 已可作为基线；外部项目可能 structured_unavailable | data_service accepted，codexPat/HarnessOS/Navia accepted 或结构化不可用且不计 accepted | 缺少完整外部项目执行记录和 artifact readiness |
| Portal 体验 | 已集成阶段状态 | Portal V3+ 直接呈现目标体验、风险、合同、E2E、交付、下一步 | 信息仍偏验收报告，需要维护者首页和状态面板 |
| 交付清理 | 工作树包含多阶段新增文件和 `.tmp/` | 版本化 manifest、review package、cleanup plan | 缺少可审查清理边界和版本说明 |
| 合同回归 | public surface guard 存在 | contract baseline、diff、compatibility report、diagnosis | 缺少跨阶段 regression artifact |

## 2. 主要风险

- 把外部项目不可用写成 accepted。
- Portal 为了可读性隐藏 unresolved、needs_review、structured_unavailable。
- cleanup plan 被误解为自动删除计划。
- contract regression 只比较名称，不比较 schema 或 build/read parity。
- 文档 claim 被实现当作 code fact。
- relationship chain 或 impact candidate 被误写为 full call graph 或 runtime call。

## 3. 缓解策略

- 每个 accepted row 必须绑定 artifact path、test command、real E2E 或结构化证据。
- 每个 Portal 状态项必须绑定 evidence_ref 或 unresolved reason。
- Delivery Manager 只输出 manifest 和 cleanup plan，不执行删除。
- Contract Regression 将 breaking change 写入 needs_review 或 structured_blocker。
- PRD/spec review 和 false-green audit 必须在每个子阶段结束后执行。

## 4. 文档支撑度

当前文档补齐后可支撑：

- 阶段级开发：约 94%。
- 立即制定 V2.63 phase-specific development/acceptance/audit：约 92%。
- 端到端 closure：约 88%，剩余取决于外部项目路径、依赖和真实运行结果。

不确定性不影响进入 V2.63 pre-implementation audit，但会影响 V2.63 accepted 覆盖率。
