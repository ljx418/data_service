# V2.71-V2.75 Risk Reduction and Technical Route Review

## 1. Remaining Risks After Documentation Revision

| 风险 | 等级 | 是否可由文档消减 | 处理 |
| --- | --- | --- | --- |
| `codexPat`、`HarnessOS`、`Navia` 无真实路径 | Major | 不能完全消减 | 保留 structured_unavailable/blocker；不计 accepted |
| Warning 数量高 | Major | 可部分消减 | 定义 warning budget、failure diagnosis 和 CI readiness |
| Agent memory 被误解为通用长期记忆 | Major | 可消减 | 明确限定为项目情报长期记忆 |
| 控制台隐藏 non-accepted 状态 | Major | 可消减 | panel schema 强制 unresolved 和 next_action |
| 发布恢复泄露本地路径或 token | Major | 可消减 | redaction check 和 public artifact contract |
| 新 public surface 未纳入 guard | Major | 可消减 | public surface guard 作为出门门槛 |

## 2. 技术路线对比

### 路线 A：独立 `agent_memory_release` package

优点：

- 与 V2.63-V2.70 已实现 package 解耦。
- 不修改 legacy 大文件。
- public surface、artifact、tests 边界清晰。
- 便于后续阶段逐步实现和回滚。

缺点：

- 新增 adapter 和 public guard 工作量较大。
- 需要显式读多个上游 artifact。

结论：推荐。

### 路线 B：继续扩展 `external_e2e_portal_delivery`

优点：

- 复用现有 V2.63-V2.70 package。
- 初期代码文件较少。

缺点：

- 外部 E2E、dashboard、memory、release restore 职责混在一起。
- 后续维护者难以判断能力边界。
- 容易让 Portal/dashboard 变成事实生成器。

结论：不推荐作为主路线。

### 路线 C：直接做前端控制台优先

优点：

- 用户可见速度最快。
- 便于展示目标体验。

缺点：

- 如果没有 memory、CI、release artifact，控制台会依赖硬编码或半结构化数据。
- false-green 风险最高。

结论：只适合作为 V2.74 的消费层，不能作为阶段起点。

## 3. 推荐路线

采用路线 A：

```text
独立 agent_memory_release package
→ 每阶段 build/read artifact
→ MCP/CLI/HTTP parity
→ public surface guard
→ real data_service E2E
→ Portal/console 只消费 artifact
```

## 4. 当前风险判断

文档修订后，阶段可以支撑自动化开发计划和阶段前审计。仍不能保证外部项目全部 accepted，因为这依赖真实路径和真实环境；该风险无法通过文档完全消除，只能通过 structured unavailable/blocker 规则防止虚假验收。

