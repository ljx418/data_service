# V2.53 Acceptance Commands

Use a normal local process rather than the restricted Codex sandbox when running FastAPI `TestClient` tests.

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -U pip
./.venv/bin/python -m pip install -e backend[test]
./.venv/bin/python backend/scripts/v2_53_acceptance.py
```

The runner executes:

- V2.46-V2.52 focused Agent Productization tests.
- V2.53 acceptance infrastructure test.
- public surface guard.
- `git diff --check`.
- `compileall` for `backend/data_service` and `backend/app/api/v1`.
