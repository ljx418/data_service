# V2.63 / Phase 139 Development Plan：External Project Full E2E

## 1. 阶段目标

Phase 139 的目标是把 V2.63-V2.66 总控文档落到第一个可实现子阶段：对 data_service、codexPat、HarnessOS、Navia 做真实项目 E2E 编排，并用结构化结果区分 accepted、needs_review、structured_unavailable、structured_blocker。

本文是 phase-specific development plan，不是实现完成证据。

## 2. 实现边界

允许新增：

```text
backend/data_service/code_assets/external_e2e_portal_delivery/
  __init__.py
  shared.py
  persistence.py
  external_e2e.py
```

后续若需要 public adapter，优先新增独立 adapter：

```text
backend/data_service/cli_code_external_e2e_portal_delivery.py
backend/data_service/mcp_code_external_e2e_portal_delivery_tools.py
backend/app/api/v1/code_assets_external_e2e_portal_delivery.py
```

禁止默认修改：

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 3. 开发步骤

1. 定义 project registry，包含 data_service、codexPat、HarnessOS、Navia。
2. 为每个项目执行 preflight：path、dependency、permission、artifact root、required command availability。
3. 对可用项目执行 artifact build/read、Portal read、contract read、restore/readiness read。
4. 对不可用项目写入 structured_unavailable 或 structured_blocker，记录 reason、failure_category、next_action。
5. 生成 full project matrix、project run records、artifact readiness、external E2E report。
6. 提供 read path，确保后续 Portal V3+ 可以只读 persisted artifacts。

## 4. 目标 artifacts

```text
external_e2e/full_project_matrix.json
external_e2e/project_run_records.json
external_e2e/artifact_readiness.json
external_e2e/external_e2e_report.md
```

## 5. 状态规则

- `accepted`：真实命令、真实 artifact、evidence_refs、focused test 支持。
- `needs_review`：结构化信息不足或需要人工判断，不能计入 accepted。
- `structured_unavailable`：路径、依赖、权限或沙箱不可用，不能计入 accepted。
- `structured_blocker`：阻塞明确且当前无法绕过，不能计入 accepted。

## 6. Stop conditions

必须停止并回到计划或请求用户确认：

- 需要修改 protected legacy 文件。
- 只能得到 mock-only evidence。
- 外部项目不可用但实现路径试图写成 accepted。
- artifact 需要写入本地 absolute path、secret、token 或 raw traceback。
- 需要自动删除或改写用户文件。

## 7. 预计用户体验

Phase 139 完成后，维护者应能看到：

- data_service 是否真实 E2E accepted。
- codexPat、HarnessOS、Navia 是 accepted、structured_unavailable 还是 structured_blocker。
- 每个项目失败属于路径、依赖、沙箱、artifact、public surface drift、真实回归还是 needs_review。
- 下一步应该修复依赖、补路径、调整合同，还是进入人工复核。
