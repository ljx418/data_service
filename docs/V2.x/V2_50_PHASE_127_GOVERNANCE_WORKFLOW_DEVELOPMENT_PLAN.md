# V2.50 Phase 127 Development Plan：Doc-Code Governance Workflow

## 1. 目标

Phase 127 为 Agent Productization artifacts 增加治理闭环：人类或 Agent 可以对 portal、profile、task navigation 等目标记录 feedback，生成 read-time overlay rule，审核 approve/revoke，并读取 overlay 报告。

本阶段输出：

- `agent_productization/governance/feedback.jsonl`
- `agent_productization/governance/rules.jsonl`
- `agent_productization/governance/applied_overlay.json`

## 2. 实现边界

- Governance 只做 read-time overlay，不改写 Phase 123-126 artifacts。
- 目标必须能解析到 persisted artifact 或其内部 target。
- approve / revoke 必须改变 overlay 读出结果，但 source artifact hash 必须不变。
- 不实现 Phase 128 playbooks 或 Phase 129 closure。

## 3. 开发动作

1. 扩展 persistence：
   - 新增 governance feedback / rules / overlay path。
   - 支持 JSONL feedback/rules 和 JSON overlay。

2. 新增 governance service：
   - `record_feedback`
   - `build_rules`
   - `review_rule`
   - `read_overlay`
   - target resolver 覆盖 portal section、profile artifact、task artifact、mcp workflow。

3. 接入三端：
   - MCP: `knowledge_code_agent_productization_governance_feedback`
   - MCP: `knowledge_code_agent_productization_governance_rules_build`
   - MCP: `knowledge_code_agent_productization_governance_rule_review`
   - MCP: `knowledge_code_agent_productization_governance_overlay`
   - CLI: `knowledge code agent-productization governance-feedback`
   - CLI: `knowledge code agent-productization governance-rules-build`
   - CLI: `knowledge code agent-productization governance-rule-review`
   - CLI: `knowledge code agent-productization governance-overlay`
   - HTTP: `/agent-productization/governance/feedback`
   - HTTP: `/agent-productization/governance/rules/build`
   - HTTP: `/agent-productization/governance/rules/{rule_id}/review`
   - HTTP: `/agent-productization/governance/overlay`

4. 增加 focused tests：
   - feedback/rules/overlay artifact 落盘。
   - approve 后 overlay 出现 applied rule。
   - revoke 后 overlay 不再应用该 rule。
   - source artifact hash unchanged。
   - HTTP / MCP / CLI parity。

## 4. 不做内容

- 不自动修改源代码。
- 不自动修改项目文档。
- 不改写 Phase 123-126 artifacts。
- 不声称 Phase 128-129 完成。
