# V2.53 Acceptance Infrastructure Acceptance Plan

## Acceptance Commands

Run from repository root in a normal local Python environment:

```bash
python3 -m pip install -e backend[test]
python3 backend/scripts/v2_53_acceptance.py
```

Equivalent focused test command:

```bash
python3 -m pytest -q \
  backend/tests/test_v2_46_agent_productization.py \
  backend/tests/test_v2_47_profile_onboarding.py \
  backend/tests/test_v2_48_human_portal.py \
  backend/tests/test_v2_49_task_navigation.py \
  backend/tests/test_v2_50_governance_workflow.py \
  backend/tests/test_v2_51_agent_playbooks.py \
  backend/tests/test_v2_52_continuous_acceptance.py \
  backend/tests/test_v2_53_acceptance_infrastructure.py \
  backend/tests/test_public_surface_guard.py
```

## Required Results

- Focused tests pass.
- `git diff --check` passes.
- `python3 -m compileall -q backend/data_service backend/app/api/v1` passes.
- V2.46-V2.52 coverage matrix and Phase 129 closure report agree that direct UI route parity / exception is closed by Phase 129 evidence.
- Test dependency baseline includes pinned `pytest`, `pytest-asyncio`, `httpx`, `fastapi`, and `starlette`.

## False-Green Rejection

Reject acceptance if:

- pytest is unavailable in the documented environment.
- only documentation is updated without focused tests.
- V2.46-V2.52 closure claims are broadened beyond existing evidence.
- a historical `structured_blocker` is left ambiguous after closure evidence says `structured_blocker_count = 0`.
- acceptance requires editing either legacy large file.
