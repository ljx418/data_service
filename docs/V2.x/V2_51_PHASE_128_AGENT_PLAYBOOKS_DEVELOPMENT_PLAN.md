# V2.51 Phase 128 Development Plan：Agent Context Playbooks

## 1. 目标

Phase 128 为不同角色生成可直接交给 Agent 使用的上下文 playbook，包括 maintainer、coding_agent、documentation_agent、architecture_reviewer。每个 playbook 必须保留证据边界，不能输出无 evidence 或 needs_review 的建议。

本阶段输出：

- `agent_productization/playbooks/{role}.json`
- `agent_productization/playbooks/{role}.md`

## 2. 实现边界

- Playbook 只消费 Phase 123-127 artifacts。
- 每条 recommendation 必须有 `evidence_refs` 或 `needs_review=true`。
- 小 token budget 下先删除低优先级 recommendation，并写入 omitted_items。
- 不声称 Agent 可以跳过真实代码审查。
- 不实现 Phase 129 closure。

## 3. 开发动作

1. 扩展 persistence：
   - 新增 playbook JSON / Markdown path。
   - 新增 role-scoped artifact refs。

2. 新增 playbook builder：
   - 支持 roles：maintainer、coding_agent、documentation_agent、architecture_reviewer。
   - 合成 workflow、profile、portal、task、governance 摘要。
   - 输出 recommendations、constraints、risk summary、recommended tool sequence、omitted_items。
   - 实现 max_tokens 预算裁剪。

3. 接入三端：
   - MCP: `knowledge_code_agent_productization_playbook_build`
   - MCP: `knowledge_code_agent_productization_playbook_read`
   - CLI: `knowledge code agent-productization playbook-build`
   - CLI: `knowledge code agent-productization playbook`
   - HTTP: `/agent-productization/playbooks`
   - HTTP: `/agent-productization/playbooks/{role}`

4. 增加 focused tests：
   - 四类 role artifact 落盘。
   - 每条 recommendation 有 evidence_refs 或 needs_review。
   - small token budget 保留 evidence policy。
   - HTTP / MCP / CLI parity。

## 4. 不做内容

- 不自动执行开发任务。
- 不生成 patch。
- 不声称 Phase 129 closure。
