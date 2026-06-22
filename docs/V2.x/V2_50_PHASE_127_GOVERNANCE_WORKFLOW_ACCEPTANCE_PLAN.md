# V2.50 Phase 127 Acceptance Plan：Doc-Code Governance Workflow

## 1. 阶段验收目标

Phase 127 通过时，系统必须能记录 governance feedback、生成 rule、approve/revoke rule，并用 read-time overlay 展示治理结果，同时证明原始 artifacts hash 不变。

## 2. 自动化验收

必须通过：

```text
pytest -q backend/tests/test_v2_50_governance_workflow.py
pytest -q backend/tests/test_public_surface_guard.py
git diff --check
/usr/bin/python3 -m compileall -q backend/data_service backend/app/api/v1
```

## 3. 真实项目验收

至少运行：

- data_service：必须完成 feedback → rule → approve → overlay → revoke → overlay。
- HarnessOS：路径存在时完成同样流程或 structured blocker。
- Navia：路径存在时完成同样流程或 structured blocker。
- codexPat：路径存在时完成同样流程或 structured blocker。

## 4. Artifact 验收

必须落盘：

```text
agent_productization/governance/feedback.jsonl
agent_productization/governance/rules.jsonl
agent_productization/governance/applied_overlay.json
```

必须验证：

- approved rule 出现在 `applied_rules`。
- revoked rule 不再出现在 `applied_rules`。
- source artifact hash before == after。
- invalid target 返回 structured error，不得静默接受。

## 5. False-green 拒绝

以下情况直接判失败：

- Governance rule 改写原始 artifact。
- approve/revoke 不影响 overlay。
- target resolver 接受不存在 target。
- public payload 泄露本机 absolute path。
- MCP 通过但 CLI / HTTP 不测。
- 本阶段声称完成 Phase 128-129 能力。

## 6. PRD 规格检视

Phase 127 只验收 Doc-Code Governance Workflow。它不验收 Agent Context Playbooks 或 Multi-project Continuous Acceptance。
