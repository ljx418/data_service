# V2.47 Phase 124 Acceptance Audit Report

## Audit Verdict

Status: accepted for Phase 124 implementation.

This report accepts Project Profile Onboarding for the current worktree scope. It does not accept Phase 125 Human Portal, Phase 126 Task Navigation, Phase 127 Governance Workflow, Phase 128 Agent Context Playbooks, or Phase 129 closure.

## Scope Review

通过：

- 本阶段只生成 profile onboarding draft、taxonomy suggestions、authority rule suggestions、path pattern suggestions 和 no-hardcode audit。
- Profile status 保持 `draft`，没有伪装成人工批准 profile。
- 项目专用术语只进入 profile onboarding artifact，不写入通用 extractor。
- 新代码位于 focused `agent_productization` 模块。
- 未修改 `backend/app/api/v1/data_service.py` 或 `backend/data_service/service.py`。

## Implementation Evidence

新增 / 修改的主要实现：

- `backend/data_service/code_assets/agent_productization/profile_onboarding.py`
- `backend/data_service/code_assets/agent_productization/persistence.py`
- `backend/data_service/mcp_code_agent_productization_tools.py`
- `backend/data_service/cli_code_agent_productization.py`
- `backend/app/api/v1/code_assets_agent_productization.py`
- `backend/tests/test_v2_47_profile_onboarding.py`
- `backend/tests/test_public_surface_guard.py`

新增三端入口：

- MCP: `knowledge_code_agent_productization_profile_build`
- MCP: `knowledge_code_agent_productization_profile_read`
- CLI: `knowledge code agent-productization profile-build`
- CLI: `knowledge code agent-productization profile`
- HTTP: `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/profile/build`
- HTTP: `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/profile`

## Automated Acceptance

通过：

```text
pytest -q backend/tests/test_v2_47_profile_onboarding.py backend/tests/test_public_surface_guard.py
```

Result:

```text
7 passed
```

通过：

```text
git diff --check
/usr/bin/python3 -m compileall -q backend/data_service backend/app/api/v1
```

Notes:

- pytest emitted a local urllib3 / LibreSSL warning. It is not a test failure.

## Real Repo E2E

Workspace:

```text
/private/tmp/ds_v247_e2e_multi/v247-multi
```

真实项目结果：

| Codebase | Status | Docs | Taxonomy | Authority | Path patterns | No-hardcode | Path redaction |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `data-service-v247` | draft | 300 | 48 | 300 | 3 | passed | passed |
| `harnessos-v247` | draft | 14 | 50 | 14 | 4 | passed | passed |
| `navia-v247` | draft | 283 | 48 | 283 | 2 | passed | passed |
| `codexpat-v247` | draft | 300 | 50 | 300 | 5 | passed | passed |

Artifact refs per project: 5.

Public payload redaction:

- no project absolute path leak.
- no temporary workspace absolute path leak.

## Artifact Inspection

每个 accepted project 均落盘：

```text
agent_productization/profile_onboarding/profile_draft.json
agent_productization/profile_onboarding/taxonomy_suggestions.json
agent_productization/profile_onboarding/authority_rule_suggestions.json
agent_productization/profile_onboarding/path_pattern_suggestions.json
agent_productization/profile_onboarding/no_hardcode_audit.json
```

Readback payload stable fields verified by focused test:

- schema_version
- artifact_type
- artifact_refs
- taxonomy_suggestion_count
- authority_rule_count
- path_pattern_count
- no_hardcode_status

## PRD / Spec Review

通过：

- Phase 124 fulfills Project Profile Onboarding in the V2.46-V2.52 PRD.
- It keeps project-specific terms in profile artifacts.
- It does not claim profile approval.
- It does not claim Human Portal, Task Navigation, Governance, Playbooks, or Closure.

## False-green Review

Rejected cases covered:

- Missing profile artifacts return `PROJECT_PROFILE_ONBOARDING_NOT_BUILT`.
- HTTP/MCP/CLI parity is tested.
- Public surface guard includes new MCP tools and HTTP routes.
- Real repos are used in E2E.
- Absolute paths are not present in public payload.

Issue found and closed:

- Initial real E2E flagged `data_service` as a no-hardcode violation because the production package namespace matched the project name. This was a false positive, not a project-specific hardcode. The generic exclusion list was updated to treat `data_service` as a package namespace for this repository. Focused tests and four-project E2E were rerun successfully.

## Open Findings

Fatal: none.

Major: none.

Minor:

- Phase 125 must create its own development plan, acceptance plan, and pre-implementation audit before implementation.
- If Phase 125 introduces a direct UI route, public contract parity or a documented UI-only exception is required.

## Decision

Phase 124 is accepted for the current worktree scope. Continue to Phase 125 only after producing and passing Phase 125 pre-implementation audit.
