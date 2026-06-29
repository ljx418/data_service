# V2.76-V2.80 Phase-specific Audit Checklist

## 1. 总体结论

本文用于后续每个子阶段开始前和结束后的审计闭环。本文不证明任何实现完成。

## 2. 进入实现前检查

每个子阶段必须逐项检查：

| 检查项 | 必须满足 |
| --- | --- |
| PRD 对齐 | 子阶段目标能映射到 V2.76-V2.80 PRD 用户体验 |
| 目标架构对齐 | 子阶段只写入 `project_acceptance_hardening/` planned package |
| 受保护文件 | 不修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py` |
| Public surface | MCP/CLI/HTTP build/read parity 已规划 |
| Artifact schema | 输出符合 `v2.76-80` shared contract |
| Real E2E | data_service 必须真实执行，外部项目不可用结构化记录 |
| False-green | unavailable、needs_review、structured_blocker 不能 accepted |
| Fatal/Major | 必须为 0 |

## 3. 子阶段审计重点

### V2.76

- 是否把 coverage matrix、final audit、visual report、focused tests 和 persisted artifacts 一起读取。
- 是否把缺证据或冲突项写成 `needs_review`。
- 是否拒绝文档声明直接 accepted。

### V2.77

- 是否要求真实 repo path。
- 是否区分 `structured_unavailable` 和 `structured_blocker`。
- 是否拒绝 mock-only external E2E。

### V2.78

- 是否记录 warning baseline/current/budget。
- 是否给 warning 分类和 owner。
- 是否拒绝删除测试覆盖作为 warning reduction。

### V2.79

- 是否所有 panel 都有 source artifact 或 unresolved。
- 是否所有 action 都有 MCP/CLI/HTTP planned surface 或人工流程。
- 是否 non-accepted 状态可见。

### V2.80

- 是否拆分机器验收和人工审批。
- 是否执行 restore、smoke、warning gate、redaction、public surface guard。
- 是否人工审批缺失时保持 `needs_review`。

## 4. 出门审计

每个子阶段 acceptance audit report 必须包含：

- focused test command/result；
- real data E2E result；
- PRD/spec review；
- false-green audit；
- protected legacy diff check；
- public surface guard result；
- artifact paths；
- unresolved/next actions。

## 5. 高风险确认点

以下情况必须停下来找用户确认：

- 需要修改 protected legacy 文件；
- 需要用真实外部项目私有路径；
- release readiness 要从 `needs_review` 改为 accepted；
- 需要删除或清理无法确认归属的本地文件；
- 测试只能通过 mock 而真实 E2E 失败。
