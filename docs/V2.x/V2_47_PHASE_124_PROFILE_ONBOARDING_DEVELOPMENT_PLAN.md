# V2.47 Phase 124 Development Plan：Project Profile Onboarding

## 1. 目标

Phase 124 将真实项目的目录、文档、命名和入口候选转换为可审计的 profile onboarding draft，帮助 Agent 在进入大型项目开发前先获得项目词汇、路径模式、文档权威规则和 no-hardcode 审计结果。

本阶段输出：

- `agent_productization/profile_onboarding/profile_draft.json`
- `agent_productization/profile_onboarding/taxonomy_suggestions.json`
- `agent_productization/profile_onboarding/authority_rule_suggestions.json`
- `agent_productization/profile_onboarding/path_pattern_suggestions.json`
- `agent_productization/profile_onboarding/no_hardcode_audit.json`

## 2. 实现边界

- 读取 codebase registry 中的真实 repo path 作为输入。
- 只生成 onboarding 建议，不自动修改项目 profile、项目文档或上游 V2 artifacts。
- 项目专用术语只能写入 profile onboarding artifact，不得写入通用 extractor、通用 taxonomy 或硬编码规则。
- 新逻辑继续放在 `backend/data_service/code_assets/agent_productization/*`。
- 复用 Phase 123 的 public envelope / artifact ref 风格。
- 不实现 Phase 125-129 的 Human Portal、Task Navigation、Governance、Playbooks 或 Closure。

## 3. 开发动作

1. 扩展 agent productization persistence：
   - 新增 profile onboarding artifact path。
   - 新增 profile onboarding artifact refs。
   - 支持 profile onboarding write/readback。

2. 新增 profile onboarding builder：
   - 扫描 repo-relative top-level paths、`docs/**`、README、drawio 等文档资产。
   - 生成 taxonomy suggestions：项目名、目录名、文档名、架构关键词。
   - 生成 authority rule suggestions：PRD、target architecture、gap、audit、acceptance、README、drawio 等文档角色。
   - 生成 path pattern suggestions：docs、source、tests、config、generated/vendor candidates。
   - 生成 no-hardcode audit：扫描通用 agent/architecture production modules，确认 HarnessOS/Navia/codexPat 等项目术语没有进入通用代码。

3. 接入三端：
   - MCP: `knowledge_code_agent_productization_profile_build`
   - MCP: `knowledge_code_agent_productization_profile_read`
   - CLI: `knowledge code agent-productization profile-build`
   - CLI: `knowledge code agent-productization profile`
   - HTTP: `/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/profile/build`
   - HTTP: `/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/profile`

4. 增加 focused tests：
   - artifact 落盘和 readback。
   - authority / taxonomy / path pattern 非空。
   - no-hardcode audit 通过或明确 findings。
   - HTTP / MCP / CLI stable field parity。
   - public payload 不泄露 absolute path。

## 4. 不做内容

- 不把 profile 建议自动写回项目源码或文档。
- 不把某个真实项目的术语写死到通用 extractor。
- 不声称 profile 已人工批准。
- 不声称 V2.46-V2.52 closure。
