# V2.55 / Phase 131 Agent Task Workflow Hardening Development Plan

Date: 2026-06-23

## 1. Phase Goal

V2.55 turns the accepted V2.49 task navigation and V2.51 playbook outputs into a task-specific workflow package for coding agents.

The workflow must help an agent understand:

- task-aware reading order;
- bounded impact candidates;
- suggested tests;
- required stop conditions;
- omitted items caused by budget or missing artifacts.

This phase does not claim full call graph, runtime topology, data/control flow, type inference, or complete design-intent recovery.

## 2. Implementation Scope

New implementation files:

```text
backend/data_service/code_assets/human_agent_deepening/task_workflow.py
```

Existing V2.54-V2.58 shared files may be extended:

```text
backend/data_service/code_assets/human_agent_deepening/persistence.py
backend/data_service/mcp_code_human_agent_deepening_tools.py
backend/data_service/cli_code_human_agent_deepening.py
backend/app/api/v1/code_assets_human_agent_deepening.py
```

Focused test:

```text
backend/tests/test_v2_55_agent_task_workflow.py
```

Protected files must not be modified:

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 3. Required Artifacts

V2.55 must write:

```text
workspace/assets/codebase/{codebase_id}/human_agent_deepening/agent_task_workflow/{task_id}/workflow_bundle.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/agent_task_workflow/{task_id}/stop_conditions.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/agent_task_workflow/{task_id}/suggested_tests.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/agent_task_workflow/{task_id}/task_workflow.md
```

## 4. Source Artifacts

Read-only inputs:

- V2.49 `agent_productization/task_navigation/{task_id}/reading_order.json`
- V2.49 `agent_productization/task_navigation/{task_id}/task_impact.json`
- V2.49 `agent_productization/task_navigation/{task_id}/suggested_tests.json`
- V2.51 `agent_productization/playbooks/coding_agent/playbook.json`
- V2.54 `human_agent_deepening/human_portal_deepening/project_story.json`
- V2.54 `human_agent_deepening/human_portal_deepening/risk_priority.json`

If a source artifact is absent, the V2.55 artifact must record `warnings` or `unresolved`; it must not hide the missing input.

## 5. Public Surface

MCP tools:

- `knowledge_code_human_agent_deepening_task_workflow_build`
- `knowledge_code_human_agent_deepening_task_workflow_read`

CLI commands:

- `python -m data_service code human-agent-deepening task-workflow-build`
- `python -m data_service code human-agent-deepening task-workflow`

HTTP routes:

- `POST /api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/task-workflow/build`
- `GET /api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/task-workflow/{task_id}`

## 6. Development Steps

1. Extend persistence helpers for V2.55 task workflow paths and artifact refs.
2. Implement `AgentTaskWorkflowService`.
3. Reuse existing V2.49 task navigation generation when building a workflow for a concrete task.
4. Load V2.51 coding-agent playbook and V2.54 portal artifacts when available.
5. Generate workflow bundle, stop conditions, normalized suggested tests, and markdown readback.
6. Add MCP, CLI, and HTTP build/read parity.
7. Register the new public surface in `test_public_surface_guard.py`.
8. Add focused tests for service, HTTP, MCP, CLI, missing inputs, budget trimming, and claim boundaries.

## 7. Non-goals

- Do not automatically modify analyzed project code.
- Do not rewrite upstream V2.49/V2.51/V2.54 artifacts.
- Do not represent impact candidates as deterministic runtime calls.
- Do not mark `needs_review`, `structured_unavailable`, or `structured_blocker` as accepted.

## 8. Exit Criteria

V2.55 development is complete only after:

- focused tests pass;
- public surface guard passes;
- V2.46-V2.54 accepted baseline still passes;
- real-project E2E passes for `data_service` and at least one available external project or records structured unavailable;
- PRD/spec review passes;
- false-green audit passes;
- V2.55 acceptance audit is written.
