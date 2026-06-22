# V2.52 Phase 129 Acceptance Plan：Multi-project Continuous Acceptance Closure

## 1. 阶段验收目标

Phase 129 通过时，V2.46-V2.52 可以声明当前 worktree 的 Agent Productization closure accepted，前提是 closure report 无 fatal / major finding，且每个 accepted row 都有真实 artifact、测试或结构化验收证据。

## 2. 自动化验收

必须通过：

```text
pytest -q backend/tests/test_v2_52_continuous_acceptance.py
pytest -q backend/tests/test_public_surface_guard.py
git diff --check
/usr/bin/python3 -m compileall -q backend/data_service backend/app/api/v1
```

最终还必须跑 Phase 123-129 focused suite。

## 3. 真实项目验收

至少覆盖：

- data_service
- HarnessOS
- Navia
- codexPat

项目不可用时只能记录 `structured_unavailable`，不能 accepted。

## 4. Artifact 验收

必须落盘：

```text
agent_productization/closure/real_repo_matrix.json
agent_productization/closure/public_contract_parity.json
agent_productization/closure/redaction_audit.json
agent_productization/closure/closure_audit_report.md
```

必须验证：

- Phase 123-128 artifact availability 被逐项列出。
- `accepted` row 均有 artifact refs 或 test evidence。
- public payload 不泄露 absolute path、secret、raw traceback。
- closure report 无 open fatal / major finding。

## 5. False-green 拒绝

以下情况直接判失败：

- skipped / unavailable 项目被标记 accepted。
- accepted row 缺 evidence。
- redaction audit 未执行。
- HTTP/MCP/CLI 只测一端。
- closure report 隐藏 fatal / major。

## 6. PRD 规格检视

Phase 129 是 V2.46-V2.52 final closure。它只在 Phase 123-128 均已通过时成立。
