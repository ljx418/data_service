# V2.55 / Phase 131 Agent Task Workflow Hardening Acceptance Plan

Date: 2026-06-23

## 1. Acceptance Target

V2.55 can be accepted only when the task workflow package is implemented and validated with focused tests, public surface guard, real-project E2E, PRD/spec review, false-green audit, and acceptance audit.

## 2. Required Assertions

Focused tests must verify:

- workflow bundle contains task summary, reading order, impact candidates, suggested tests, stop conditions, and omitted items;
- every recommendation has `evidence_refs` or `needs_review`;
- every suggested test has status `recommended`, `needs_review`, or `structured_unavailable`;
- a suggested test without evidence is `needs_review`;
- impact candidates are static candidates and never `runtime_call`, `data_flow`, `control_flow`, or `production_topology` claims;
- low token budget records omitted items instead of silently dropping context;
- missing upstream artifacts produce `warnings` or `unresolved`;
- public payload has no local absolute path, secret, token, or raw traceback.

## 3. Required Commands

```text
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_55_agent_task_workflow.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_public_surface_guard.py
PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py
PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend
git diff --check
git diff --name-only -- backend/app/api/v1/data_service.py backend/data_service/service.py
```

## 4. Real-project E2E

Required:

- Build/read workflow for `data_service` with a concrete implementation task.
- Build/read workflow for one available external project.

A project may be recorded as `structured_unavailable` only with a concrete reason. It must not be counted as accepted.

## 5. PRD / Spec Review

Review questions:

- Does the output give a coding agent a concrete task-aware workflow before editing code?
- Are reading order, impact candidates, and tests bounded and evidence-backed?
- Are stop conditions explicit enough to prevent protected file mutation, mock-only acceptance, and static-analysis overclaims?
- Are omitted items visible when budget or artifact availability limits the bundle?

## 6. False-green Rejection Rules

Reject V2.55 acceptance if:

- impact candidates are described as runtime calls;
- a recommendation lacks both `evidence_refs` and `needs_review`;
- missing upstream artifacts are hidden;
- suggested tests without evidence are marked `recommended`;
- low-budget truncation does not record omitted items;
- mock-only or unavailable projects are counted as accepted;
- public payload leaks absolute paths, secrets, tokens, or raw traceback.

## 7. Required Post-implementation Documents

```text
docs/V2.x/V2_55_PHASE_131_AGENT_TASK_WORKFLOW_PRD_SPEC_REVIEW_REPORT.md
docs/V2.x/V2_55_PHASE_131_AGENT_TASK_WORKFLOW_FALSE_GREEN_AUDIT_REPORT.md
docs/V2.x/V2_55_PHASE_131_AGENT_TASK_WORKFLOW_ACCEPTANCE_AUDIT_REPORT.md
```
