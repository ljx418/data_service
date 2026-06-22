# V2.49 Phase 126 Development Plan：Task Navigation and Impact v2

## 1. 目标

Phase 126 为 Codex/Copilot 类 Agent 提供基于任务的阅读顺序、影响候选和建议测试，减少大项目中无边界代码阅读造成的 token 浪费。

本阶段输出：

- `agent_productization/task_navigation/{task_id}/reading_order.json`
- `agent_productization/task_navigation/{task_id}/task_impact.json`
- `agent_productization/task_navigation/{task_id}/suggested_tests.json`

## 2. 实现边界

- 只输出 bounded reading order、impact candidates 和 suggested tests。
- impact candidate 是启发式候选，不得描述为 deterministic runtime call。
- 每条 suggested test 必须有 evidence refs 或 `needs_review`。
- 读取 codebase registry、Phase 124 profile onboarding 和 repo-relative 文件结构。
- 不实现 Phase 127-129 的 governance、playbook 或 closure。

## 3. 开发动作

1. 扩展 persistence：
   - 新增 task navigation artifact path 和 refs。
   - 支持 task_id scoped write/readback。

2. 新增 task navigation builder：
   - 根据 task 文本抽取关键词。
   - 从 repo-relative docs/source/test/config 文件中选择 bounded reading order。
   - 生成 impact candidates，标注 match_strategy、confidence、evidence_refs、needs_review。
   - 生成 suggested tests，优先选择测试文件；没有测试时输出 needs_review。

3. 接入三端：
   - MCP: `knowledge_code_agent_productization_task_navigation_build`
   - MCP: `knowledge_code_agent_productization_task_navigation_read`
   - CLI: `knowledge code agent-productization task-build`
   - CLI: `knowledge code agent-productization task`
   - HTTP: `/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/tasks`
   - HTTP: `/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/tasks/{task_id}`

4. 增加 focused tests：
   - reading order 非空且 bounded。
   - impact candidates 不含 runtime-call claim。
   - suggested tests 均有 evidence 或 needs_review。
   - HTTP / MCP / CLI parity。
   - public payload 不泄露 absolute path。

## 4. 不做内容

- 不声称完整调用图。
- 不执行测试。
- 不应用代码修改。
- 不声称 Phase 127-129 完成。
