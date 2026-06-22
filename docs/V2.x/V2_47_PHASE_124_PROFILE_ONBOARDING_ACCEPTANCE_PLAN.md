# V2.47 Phase 124 Acceptance Plan：Project Profile Onboarding

## 1. 阶段验收目标

Phase 124 通过时，系统必须能基于真实 repo 生成 profile onboarding draft，并通过 HTTP/MCP/CLI 读取同一组 persisted artifact。输出必须帮助人类和 Agent 理解项目术语、文档权威、路径结构和 no-hardcode 风险。

## 2. 自动化验收

必须通过：

```text
pytest -q backend/tests/test_v2_47_profile_onboarding.py
pytest -q backend/tests/test_public_surface_guard.py
git diff --check
/usr/bin/python3 -m compileall -q backend/data_service backend/app/api/v1
```

如果全量测试因环境或依赖阻塞，必须记录 blocker，不得伪装通过。

## 3. 真实项目验收

至少运行：

- data_service：必须生成 accepted profile onboarding artifact。
- HarnessOS：路径存在时生成 accepted profile onboarding artifact；路径不可用时 structured unavailable。
- Navia：路径存在时生成 accepted profile onboarding artifact；路径不可用时 structured unavailable。
- codexPat：路径存在时生成 accepted profile onboarding artifact；路径不可用时 structured unavailable。

项目路径不可用时必须输出 `PROJECT_REPO_UNAVAILABLE` 或同等级 structured unavailable，不能写 accepted。

## 4. Artifact 验收

必须落盘：

```text
agent_productization/profile_onboarding/profile_draft.json
agent_productization/profile_onboarding/taxonomy_suggestions.json
agent_productization/profile_onboarding/authority_rule_suggestions.json
agent_productization/profile_onboarding/path_pattern_suggestions.json
agent_productization/profile_onboarding/no_hardcode_audit.json
```

必须验证：

- `profile_draft.project_name`、`doc_assets`、`path_patterns` 非空或给出 structured blocker。
- taxonomy suggestions 有 evidence refs 或 source path。
- authority rule suggestions 区分 PRD、target architecture、gap、audit、acceptance、README、drawio。
- no-hardcode audit 扫描通用 production modules，项目术语只能出现在 profile artifact。
- readback payload 中 artifact refs 指向同一组 artifact。

## 5. HTTP / MCP / CLI Parity

三端读取结果必须比较：

- schema_version
- workspace_id
- codebase_id
- artifact refs count
- taxonomy suggestion count
- authority suggestion count
- path pattern count
- warnings count
- unresolved count
- error code

## 6. False-green 拒绝

以下情况直接判失败：

- 只用 mock repo，不跑 data_service 真实项目。
- 项目路径不可用却标记 accepted。
- 项目术语写入通用 extractor 或通用 architecture module。
- 只生成 profile draft，没有 taxonomy / authority / path / no-hardcode artifact。
- public payload 泄露本机 absolute path。
- MCP 通过但 CLI / HTTP 不测。
- structured unavailable 被写成 accepted。
- 本阶段声称完成 Phase 125-129 能力。

## 7. PRD 规格检视

Phase 124 只验收 Project Profile Onboarding。它不验收 Human Portal、Task Navigation、Doc-Code Governance、Agent Context Playbooks 或 Multi-project Continuous Acceptance。
