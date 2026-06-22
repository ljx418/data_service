# V2.52 Phase 129 Development Plan：Multi-project Continuous Acceptance Closure

## 1. 目标

Phase 129 对 V2.46-V2.52 Agent Productization 做最终收口。它不新增新的产品能力，而是把 Phase 123-128 的产物、真实项目验收、public contract parity、redaction/no-hardcode 检查汇总为可审计 closure artifact。

本阶段输出：

- `agent_productization/closure/real_repo_matrix.json`
- `agent_productization/closure/public_contract_parity.json`
- `agent_productization/closure/redaction_audit.json`
- `agent_productization/closure/closure_audit_report.md`

## 2. 实现边界

- Closure 只读取 Phase 123-128 persisted artifacts。
- Closure 可以记录 structured unavailable，但不能把 unavailable 记为 accepted。
- Closure 不重建上游 artifacts，不改写 profile、portal、task、governance、playbook 原始产物。
- Closure 不声称完整 call graph、runtime topology 或无证据开发建议。

## 3. 开发动作

1. 扩展 persistence：
   - closure artifact paths；
   - closure artifact refs；
   - write/read closure bundle。

2. 新增 closure builder：
   - 检查 Phase 123-128 artifact availability；
   - 生成 real repo matrix；
   - 生成 public contract parity summary；
   - 生成 redaction/no-hardcode audit；
   - 生成 Markdown closure report。

3. 接入三端：
   - MCP: `knowledge_code_agent_productization_closure_build`
   - MCP: `knowledge_code_agent_productization_closure_read`
   - CLI: `knowledge code agent-productization closure-build`
   - CLI: `knowledge code agent-productization closure`
   - HTTP: `/agent-productization/closure/build`
   - HTTP: `/agent-productization/closure`

4. 增加 focused tests：
   - closure artifacts 落盘；
   - accepted rows 有 evidence；
   - redaction audit 无泄露；
   - HTTP / MCP / CLI parity。

## 4. 不做内容

- 不新增 direct UI route。
- 不自动推送 git。
- 不替代阶段 acceptance audit 的原始证据。
