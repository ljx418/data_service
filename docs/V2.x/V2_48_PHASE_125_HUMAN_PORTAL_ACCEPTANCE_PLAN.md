# V2.48 Phase 125 Acceptance Plan：Human Architecture Portal

## 1. 阶段验收目标

Phase 125 通过时，系统必须能基于 persisted artifacts 生成人类可读的项目理解 HTML 页面和图表，并通过 HTTP/MCP/CLI 读取同一 portal model。

## 2. 自动化验收

必须通过：

```text
pytest -q backend/tests/test_v2_48_human_portal.py
pytest -q backend/tests/test_public_surface_guard.py
git diff --check
/usr/bin/python3 -m compileall -q backend/data_service backend/app/api/v1
```

## 3. 真实项目验收

至少运行：

- data_service：必须生成 portal model、HTML、SVG。
- HarnessOS：路径存在时生成 portal 或 structured blocker。
- Navia：路径存在时生成 portal 或 structured blocker。
- codexPat：路径存在时生成 portal 或 structured blocker。

项目路径不可用时必须输出 `PROJECT_REPO_UNAVAILABLE` 或同等级 structured unavailable，不能写 accepted。

## 4. Artifact 验收

必须落盘：

```text
agent_productization/human_portal/portal_model.json
agent_productization/human_portal/charts/architecture_overview.svg
agent_productization/human_portal/project_architecture_portal.html
```

必须验证：

- HTML 原位包含 SVG 图表。
- HTML 不展示 Mermaid 源码。
- HTML/SVG 文本经过 escape。
- portal model 中每个 visible card / chart node 都有 artifact ref、registry evidence 或 structured blocker。
- readback payload 中 artifact refs 指向同一组 artifact。

## 5. HTTP / MCP / CLI Parity

三端读取结果必须比较：

- schema_version
- workspace_id
- codebase_id
- artifact refs count
- section count
- chart node count
- blocker count
- warnings count
- unresolved count
- error code

## 6. False-green 拒绝

以下情况直接判失败：

- HTML 内容不是从 persisted portal model 渲染。
- HTML 展示 Mermaid source 而不是图表。
- HTML/SVG 包含 artifact 外新增事实。
- public payload 泄露本机 absolute path。
- MCP 通过但 CLI / HTTP 不测。
- structured unavailable 被写成 accepted。
- 本阶段声称完成 Phase 126-129 能力。

## 7. PRD 规格检视

Phase 125 只验收 Human Architecture Portal。它不验收 Task Navigation、Doc-Code Governance、Agent Context Playbooks 或 Multi-project Continuous Acceptance。
