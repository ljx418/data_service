# V2.63-V2.66 Implementation Blueprint and Acceptance Spec

## 1. 文档定位

本文把 V2.63-V2.66 PRD 和目标架构落到实现面、artifact contract、public surface、focused tests 和验收规则。本文是开发与验收基线，不是实现完成证据。

## 2. 建议代码落点

新增实现应放在独立目录，不修改 legacy 大文件：

```text
backend/data_service/code_assets/external_e2e_portal_delivery/
  __init__.py
  shared.py
  persistence.py
  external_e2e.py
  portal_v3.py
  delivery.py
  contract_regression.py
```

可选 adapter：

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

## 3. Artifact layout

所有本阶段 artifact 写入：

```text
workspace/assets/codebase/{codebase_id}/external_e2e_portal_delivery/
```

阶段子目录：

```text
external_e2e/
portal_v3/
delivery/
contract_regression/
acceptance/
```

组件只能通过 read-only reference 消费 V2.54-V2.62 artifact，不得静默改写上游 artifact。

## 4. Planned MCP tools

```text
knowledge_code_external_e2e_portal_delivery_e2e_build
knowledge_code_external_e2e_portal_delivery_e2e_read
knowledge_code_external_e2e_portal_delivery_portal_build
knowledge_code_external_e2e_portal_delivery_portal_read
knowledge_code_external_e2e_portal_delivery_delivery_build
knowledge_code_external_e2e_portal_delivery_delivery_read
knowledge_code_external_e2e_portal_delivery_contract_build
knowledge_code_external_e2e_portal_delivery_contract_read
```

每个 build tool 必须返回 artifact refs；每个 read tool 必须只读取 persisted artifact，不重新制造事实。

## 5. Planned CLI commands

命令组：

```text
python -m data_service code external-e2e-portal-delivery <command>
```

子命令：

```text
e2e-build
e2e-read
portal-build
portal-read
delivery-build
delivery-read
contract-build
contract-read
```

## 6. Planned HTTP routes

路由家族：

```text
/workspaces/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/e2e/build
/workspaces/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/e2e
/workspaces/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/portal/build
/workspaces/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/portal
/workspaces/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/delivery/build
/workspaces/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/delivery
/workspaces/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/contract/build
/workspaces/{workspace_id}/codebases/{codebase_id}/external-e2e-portal-delivery/contract
```

除非记录 UI-only read exception，否则 MCP、CLI、HTTP 必须提供 build/read parity。

## 7. Focused tests

```text
backend/tests/test_v2_63_external_project_full_e2e.py
backend/tests/test_v2_64_portal_v3_experience.py
backend/tests/test_v2_65_delivery_cleanup_versioning.py
backend/tests/test_v2_66_public_surface_contract_regression.py
```

共享守护：

```text
backend/tests/test_public_surface_guard.py
```

## 8. Acceptance spec

每个阶段 accepted 必须满足：

- artifact path 存在且 repo-relative。
- focused test command/result 存在。
- data_service 真实 E2E accepted；外部项目 accepted 或 structured_unavailable/structured_blocker 且不计入 accepted。
- PRD/spec review 明确无 fatal/major 偏差。
- false-green audit 确认没有 mock-only accepted、unavailable accepted、needs_review accepted。
- public output 不包含 absolute path、secret、token、raw traceback。

## 9. Stop conditions

必须停止并回到开发计划或请求人类确认：

- 需要修改 protected legacy 文件。
- contract regression 发现 breaking change 但没有 migration/diagnosis。
- cleanup 需要删除未确认归属文件。
- 外部项目 E2E 只有 mock-only evidence。
- 文档 claim 被实现当作 code fact。
