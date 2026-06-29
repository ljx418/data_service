# V2.71-V2.75 Gap Analysis

## 1. 当前架构到目标架构差异

| 能力 | 当前状态 | 目标状态 | 差距 |
| --- | --- | --- | --- |
| 外部项目闭环 | data_service accepted，其他外部项目 structured_unavailable | 每个项目有真实路径、E2E、不可用原因和 next action | 缺少 closure-level 汇总与路径再验证 |
| CI/warning 治理 | 测试通过但 warning 较高，慢测试存在 | 有 CI matrix、warning budget、failure diagnosis | 缺少治理 artifact 和出门门槛 |
| Agent 长期记忆 | 有 context pack、Portal、dashboard | 有 memory index、evidence index、acceptance state、retention policy | 缺少稳定 memory surface |
| 维护者控制台 | 有 Portal/Dashboard artifact | 有交互式首页模型、导航、状态面板、证据跳转 | 缺少统一控制台模型 |
| 发布恢复 | 有 restore UX、delivery manifest | 有 release manifest、MCP config template、smoke commands、runbook | 缺少发布恢复打包体验 |

## 2. 风险

- 外部项目仍不可用时被误写 accepted。
- CI 治理阶段通过降低覆盖或跳过测试制造 false green。
- 长期记忆被误解为通用聊天记忆或完整项目理解。
- 控制台 HTML 通过硬编码隐藏 unresolved 状态。
- 发布恢复文档泄露本地路径或 token。
- 新 surface 未进入 public surface guard。

## 3. 缓解策略

- 所有 accepted 状态必须绑定 artifact_ref、evidence_ref、command 和 result。
- 外部项目无真实路径时只能 structured_unavailable 或 structured_blocker。
- memory artifact 只能引用 persisted artifacts，不生成无证据事实。
- 控制台每个面板必须保留 non-accepted 状态和 next actions。
- release artifact 必须通过 redaction check。
- 每个新增 MCP/CLI/HTTP surface 必须有 build/read parity 和 focused tests。

## 4. 文档阶段结论

本 gap analysis 支持进入后续 implementation planning。它不证明 V2.71-V2.75 已实现。

