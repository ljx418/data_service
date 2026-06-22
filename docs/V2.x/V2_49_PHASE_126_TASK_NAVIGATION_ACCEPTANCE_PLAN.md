# V2.49 Phase 126 Acceptance Plan：Task Navigation and Impact v2

## 1. 阶段验收目标

Phase 126 通过时，系统必须能针对真实任务生成可执行的阅读顺序、影响候选和建议测试，并通过 HTTP/MCP/CLI 读取同一 task-scoped artifacts。

## 2. 自动化验收

必须通过：

```text
pytest -q backend/tests/test_v2_49_task_navigation.py
pytest -q backend/tests/test_public_surface_guard.py
git diff --check
/usr/bin/python3 -m compileall -q backend/data_service backend/app/api/v1
```

## 3. 真实项目验收

至少运行：

- data_service：任务样例必须生成 reading order、impact candidates、suggested tests。
- HarnessOS：路径存在时生成 task navigation 或 structured blocker。
- Navia：路径存在时生成 task navigation 或 structured blocker。
- codexPat：路径存在时生成 task navigation 或 structured blocker。

## 4. Artifact 验收

必须落盘：

```text
agent_productization/task_navigation/{task_id}/reading_order.json
agent_productization/task_navigation/{task_id}/task_impact.json
agent_productization/task_navigation/{task_id}/suggested_tests.json
```

必须验证：

- reading order 有 token estimate 和 reason。
- impact candidates 有 evidence refs 或 needs_review。
- suggested tests 有 evidence refs 或 needs_review。
- impact candidate 不得使用 `runtime_call`、`data_flow`、`control_flow`、`production_topology` 作为 accepted claim。

## 5. False-green 拒绝

以下情况直接判失败：

- 只返回全仓文件列表，没有 bounded reading order。
- impact candidate 被描述为 deterministic runtime call。
- suggested tests 缺 evidence 且没有 needs_review。
- public payload 泄露本机 absolute path。
- MCP 通过但 CLI / HTTP 不测。
- 本阶段声称完成 Phase 127-129 能力。

## 6. PRD 规格检视

Phase 126 只验收 Task Navigation and Impact v2。它不验收 Governance Workflow、Agent Context Playbooks 或 Multi-project Continuous Acceptance。
