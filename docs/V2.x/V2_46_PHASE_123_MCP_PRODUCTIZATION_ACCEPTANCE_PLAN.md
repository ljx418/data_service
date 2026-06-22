# V2.46 Phase 123 Acceptance Plan：MCP 使用产品化

## 1. 阶段验收目标

Phase 123 通过时，系统必须能从真实 MCP registry 生成 Agent 可消费的 MCP 使用包，并通过 HTTP/MCP/CLI 三端读取同一组稳定 artifact。

## 2. 自动化验收

必须通过：

```text
pytest -q backend/tests/test_v2_46_agent_productization.py
pytest -q backend/tests/test_public_surface_guard.py
git diff --check
```

如果全量测试因环境或依赖阻塞，必须记录 blocker，不得伪装通过。

## 3. 真实项目验收

至少运行：

- data_service：必须生成 accepted MCP usage guide。
- HarnessOS：路径存在时生成 accepted 或 structured unavailable，不得 mock accepted。
- Navia：路径存在时生成 accepted 或 structured unavailable，不得 mock accepted。
- codexPat：路径存在时生成 accepted 或 structured unavailable，不得 mock accepted。

项目路径不可用时必须输出 `PROJECT_REPO_UNAVAILABLE` 或同等级 structured unavailable。

## 4. Artifact 验收

必须落盘：

```text
agent_productization/mcp_usage_guide.json
agent_productization/mcp_tool_catalog_readable.json
agent_productization/mcp_agent_workflows.json
agent_productization/docs/generated/codex_mcp_usage_guide.md
```

必须验证：

- tool catalog count == `len(all_tool_specs())`。
- workflow 中引用的 tool 要么 available，要么明确 missing。
- Codex CLI guide 包含 MCP 配置、推荐调用序列、失败处理。
- readback payload 中 artifact refs 指向同一组 artifact。

## 5. HTTP / MCP / CLI Parity

三端读取结果必须比较：

- schema_version
- workspace_id
- codebase_id
- artifact refs count
- tool_count
- workflow_count
- warnings count
- unresolved count
- error code

## 6. False-green 拒绝

以下情况直接判失败：

- tool catalog 不是来自 MCP registry。
- registry count 与 catalog count 不一致且没有 blocker。
- 只生成 Markdown，没有 JSON artifact。
- 只测 mock fixture，不跑 data_service 真实项目。
- public payload 泄露本机 absolute path。
- MCP 通过但 CLI / HTTP 不测。
- structured unavailable 被写成 accepted。
- 本阶段声称完成 Phase 124-129 能力。

## 7. PRD 规格检视

Phase 123 只验收 MCP 使用产品化。它不验收 Project Profile Onboarding、Human Portal、Task Navigation、Doc-Code Governance、Agent Context Playbooks 或 Multi-project Continuous Acceptance。

