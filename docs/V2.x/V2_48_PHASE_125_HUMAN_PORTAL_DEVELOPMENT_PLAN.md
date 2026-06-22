# V2.48 Phase 125 Development Plan：Human Architecture Portal

## 1. 目标

Phase 125 将 Phase 123 MCP usage bundle、Phase 124 profile onboarding、以及已有 V2 project intelligence artifacts 渲染为人类可读的项目理解入口。目标不是新增事实抽取，而是让维护者能快速看到项目定位、可用 Agent 工作流、profile draft、风险、图表和下一步阅读路径。

本阶段输出：

- `agent_productization/human_portal/portal_model.json`
- `agent_productization/human_portal/charts/architecture_overview.svg`
- `agent_productization/human_portal/project_architecture_portal.html`

## 2. 实现边界

- Human Portal 只能从 persisted artifacts 和 codebase registry 渲染。
- HTML / SVG 不能引入 artifact 中不存在的新事实。
- 图表必须原位渲染，不展示 Mermaid 源码。
- 文档和项目文本必须 HTML escaped。
- 不新增 direct UI route；HTTP 只返回 persisted artifact / HTML content。
- 不实现 Phase 126-129 的 task impact、governance、playbook 或 closure。

## 3. 开发动作

1. 扩展 agent productization persistence：
   - 新增 portal model、HTML、SVG path。
   - 新增 portal artifact refs。

2. 新增 Human Portal builder：
   - 读取 Phase 123 MCP usage artifacts；缺失时显示 structured blocker。
   - 读取 Phase 124 profile onboarding artifacts；缺失时显示 structured blocker。
   - 从 registry 读取 codebase name/status。
   - 生成 portal model：summary、available_artifacts、workflow cards、profile snapshot、risk/blocker list、reading path。
   - 生成 SVG architecture overview。
   - 生成 HTML report，包含 project overview、Agent workflows、profile draft、graph/chart、needs_review/blockers、recommended next steps。

3. 接入三端：
   - MCP: `knowledge_code_agent_productization_portal_build`
   - MCP: `knowledge_code_agent_productization_portal_read`
   - CLI: `knowledge code agent-productization portal-build`
   - CLI: `knowledge code agent-productization portal`
   - HTTP: `/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/portal/build`
   - HTTP: `/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/portal`
   - HTTP: `/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/portal/view`

4. 增加 focused tests：
   - HTML/SVG artifact 落盘。
   - HTML 包含原位 SVG，不包含 Mermaid source。
   - HTML/SVG 中节点均来自 portal model。
   - public payload 不泄露 absolute path。
   - HTTP / MCP / CLI stable field parity。

## 4. 不做内容

- 不创建新的架构事实。
- 不声明完整理解项目。
- 不提供编辑 UI。
- 不声称 Phase 126-129 完成。
