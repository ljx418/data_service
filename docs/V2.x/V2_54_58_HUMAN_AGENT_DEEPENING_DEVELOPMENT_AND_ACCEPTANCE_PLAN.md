# V2.54-V2.58 Development and Acceptance Plan

## 1. Shared Rules

- 每个阶段开始前必须产出 phase-specific development plan、acceptance plan、pre-implementation audit。
- 每个阶段结束后必须产出 acceptance audit report。
- 具体代码落点、MCP/CLI/HTTP surface、focused test 名称和 coverage matrix 回填规则以 `V2_54_58_HUMAN_AGENT_DEEPENING_IMPLEMENTATION_BLUEPRINT_AND_ACCEPTANCE_SPEC.md` 为准。
- 使用真实项目：data_service、HarnessOS、Navia、codexPat。
- 真实项目不可用时只能 structured_unavailable，不能 accepted。
- 所有 public output 必须 repo-relative path，不能泄露 secret、token、raw traceback。
- 所有 Agent recommendation 必须有 evidence_refs 或 needs_review。
- 不修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`，除非用户明确批准。

## 2. V2.54 Human Portal Deepening

开发：

- 增强 portal model：project story、risk priority、reading path、acceptance state。
- 增强 HTML/SVG 图表：target/current/diff、risk、next actions。
- 增加 evidence-backed portal section audit。

验收：

- data_service 与至少一个外部真实项目生成 readable portal。
- 每个新增 portal section 有 evidence_refs 或 unresolved reason。
- HTML 不展示 raw Mermaid source，不引入 artifact 外事实。
- public route parity 或 UI-only exception 完成审计。

## 3. V2.55 Agent Task Workflow Hardening

开发：

- 组合 task navigation、playbooks、suggested tests、constraints、stop conditions。
- 输出 task workflow bundle，包含 reading order、impact candidates、test plan、omitted_items。
- 增加 low-confidence / needs_review 处理。

验收：

- 给定真实修改任务，workflow 不要求全仓扫描。
- 每个 suggested test 有 evidence_refs 或 needs_review。
- impact candidate 不声称 deterministic runtime call。
- 小 token budget 下保留高风险 evidence 或记录 omitted_items。

## 4. V2.56 Doc-Code Governance Evidence Loop

开发：

- 将 doc-code findings、review decisions、rules、overlay 串成 evidence loop。
- 输出 decision history、rule effect、revocation state。
- 增加 governance readback 和 false-green audit。

验收：

- approve rule 后 read output 显示 applied rule effect。
- revoke rule 后 read output 不再应用该 rule。
- 原始 docs 和上游 code facts hash 不变。
- supported/weak/unsupported/contradicted 状态不被 HTML 或 playbook 抹平。

## 5. V2.57 Multi-project Regression Expansion

开发：

- 扩展 real repo matrix：artifact availability、diff summary、trend、failure diagnosis。
- 记录 project unavailable、provider unavailable、structured blocker、needs_review。
- 输出 regression report 和 acceptance trend。

验收：

- data_service、HarnessOS、Navia、codexPat 均有结果或 structured_unavailable。
- accepted 项必须有 artifact refs 和 test command。
- 不把 mock-only evidence 当作 real repo result。
- public redaction 和 parity guard 通过。

## 6. V2.58 Developer Onboarding / Restore UX

开发：

- 生成 restore checklist、dependency baseline、acceptance troubleshooting。
- 扩展 V2.53 runner 文档，说明非沙箱 TestClient 限制。
- 输出 onboarding report。

验收：

- 新环境可按文档安装 test deps 并运行 canonical acceptance runner。
- 常见失败能被归类为 dependency drift、sandbox limit、artifact missing、public surface drift、real regression。
- restore 文档不包含本机私有路径。

## 7. Stop Conditions

发现以下情况必须停止：

- accepted 结论缺 evidence。
- needs_review、structured_unavailable、structured_blocker 被写成 accepted。
- profile / project-specific rule 被写进通用 extractor。
- HTML 或 playbook 引入 artifact 外事实。
- 真实项目 E2E 被 mock-only 测试替代。
- legacy 大文件被无批准修改。
