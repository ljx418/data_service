# V2.51 Phase 128 Acceptance Plan：Agent Context Playbooks

## 1. 阶段验收目标

Phase 128 通过时，系统必须能为四类角色生成 evidence-aware Agent playbook，并通过 HTTP/MCP/CLI 读取同一 role-scoped artifacts。

## 2. 自动化验收

必须通过：

```text
pytest -q backend/tests/test_v2_51_agent_playbooks.py
pytest -q backend/tests/test_public_surface_guard.py
git diff --check
/usr/bin/python3 -m compileall -q backend/data_service backend/app/api/v1
```

## 3. 真实项目验收

至少运行：

- data_service：四类 playbook 均生成。
- HarnessOS：路径存在时四类 playbook 均生成或 structured blocker。
- Navia：路径存在时四类 playbook 均生成或 structured blocker。
- codexPat：路径存在时四类 playbook 均生成或 structured blocker。

## 4. Artifact 验收

必须落盘：

```text
agent_productization/playbooks/{role}.json
agent_productization/playbooks/{role}.md
```

必须验证：

- recommendation 均有 evidence_refs 或 needs_review。
- small token budget 下不保留无 evidence / needs_review 的 recommendation。
- omitted_items 有 reason。
- Markdown 与 JSON 来自同一 model。

## 5. False-green 拒绝

以下情况直接判失败：

- recommendation 缺 evidence_refs 且没有 needs_review。
- token 裁剪删除 evidence 但保留建议。
- 只生成 Markdown，不生成 JSON。
- public payload 泄露本机 absolute path。
- MCP 通过但 CLI / HTTP 不测。
- 本阶段声称完成 Phase 129。

## 6. PRD 规格检视

Phase 128 只验收 Agent Context Playbooks。它不验收 Multi-project Continuous Acceptance 或最终 closure。
