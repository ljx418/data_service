# V2.91-V2.95 Test and E2E Mapping

## 1. Focused Tests

计划新增测试：

```text
backend/tests/test_v2_91_restoreable_acceptance_runtime.py
backend/tests/test_v2_92_route_a_material_closure.py
backend/tests/test_v2_93_human_quality_decision_closure.py
backend/tests/test_v2_94_external_project_path_e2e_closure.py
backend/tests/test_v2_95_final_release_gate_closure.py
backend/tests/test_public_surface_guard.py
```

## 2. 真实 E2E 映射

| 阶段 | 输入 | E2E 动作 | 成功证据 | 不可用处理 |
| --- | --- | --- | --- | --- |
| V2.91 | 当前本机环境 | 创建/验证 pytest runtime，复跑 focused regression | command result、diagnosis artifact | structured_blocker |
| V2.92 | 用户代表性资料包 | 脱敏、导入、截图、人工验收 | material manifest、screenshot refs、review decision | needs_review |
| V2.93 | V2.84/V2.88 quality artifacts | 人工审查质量建议和 rule effect | decision history、rule effect closure | needs_review |
| V2.94 | 外部项目路径 | 路径检查和 E2E smoke | e2e matrix、unavailable decisions | structured_unavailable |
| V2.95 | M1-M4 artifacts | 聚合 final release gate | final gate summary、false-green audit | structured_blocker 或 structured_unavailable |

## 3. 公共接口验收

若新增 public surface，必须验证：

- MCP build/read parity。
- CLI command group inventory。
- HTTP route family build/read parity。
- Read 接口只读 persisted artifacts。
- Public artifact 不包含 secret、token、raw traceback、private absolute path。

## 4. 环境恢复验收

V2.91 必须明确区分：

- 服务能启动。
- API 能返回。
- `compileall` 能通过。
- pytest focused regression 能复跑。

只有最后一项满足，才可声明 focused tests passed。

