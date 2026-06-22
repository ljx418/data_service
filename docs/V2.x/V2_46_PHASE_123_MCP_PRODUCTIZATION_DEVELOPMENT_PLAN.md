# V2.46 Phase 123 Development Plan：MCP 使用产品化

## 1. 目标

Phase 123 将现有 MCP registry、V2 project intelligence artifacts 和 Codex CLI 使用路径产品化为可读、可复制、可验收的 Agent 使用包。

本阶段输出：

- `agent_productization/mcp_usage_guide.json`
- `agent_productization/mcp_tool_catalog_readable.json`
- `agent_productization/mcp_agent_workflows.json`
- `agent_productization/docs/generated/codex_mcp_usage_guide.md`

## 2. 实现边界

- 读取 `mcp_tool_registry.all_tool_specs()` 作为唯一 MCP tool catalog 来源。
- 新逻辑放在 `backend/data_service/code_assets/agent_productization/*`。
- 新 MCP 入口放在 focused MCP module，不把逻辑塞进 legacy 大文件。
- CLI 只做参数到 MCP tool payload 的薄转发。
- HTTP route 如新增，只能读取或构建同一 persisted artifact，不能产生独立事实源。
- 不实现 Phase 124-129 的 profile onboarding、Human Portal、task impact、governance、playbook closure。

## 3. 开发动作

1. 新增 agent productization persistence：
   - 统一 artifact root。
   - 写入 / 读取 JSON artifact 和 Markdown guide。
   - 输出 stable artifact refs。

2. 新增 MCP usage guide builder：
   - 从 MCP registry 构建 readable tool catalog。
   - 按 project reading、coding task、architecture review、governance review 生成 workflow。
   - 生成 Codex CLI usage guide markdown。
   - 记录 registry count parity。

3. 新增 public payload：
   - schema version `v2.46-52`。
   - tool_count、workflow_count、validation_summary、artifact_refs。
   - 未配置或 artifact 缺失时返回结构化错误。

4. 接入三端：
   - MCP: `knowledge_code_agent_productization_mcp_build`
   - MCP: `knowledge_code_agent_productization_mcp_read`
   - CLI: `knowledge code agent-productization mcp-build`
   - CLI: `knowledge code agent-productization mcp`
   - HTTP: `/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/mcp/build`
   - HTTP: `/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/mcp`

5. 增加 focused tests：
   - registry count parity。
   - artifact 落盘和 readback。
   - MCP / CLI / HTTP stable fields parity。
   - Markdown guide 包含 Codex CLI usage path。
   - public payload 不泄露 absolute path。

## 4. 不做内容

- 不新增 profile onboarding。
- 不生成 Human Portal。
- 不实现 task impact。
- 不实现 governance overlay。
- 不声称 V2.46-V2.52 closure。

