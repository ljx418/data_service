# V2.105 / Phase 181 Acceptance Plan

## Acceptance Criteria

- Release gate contains phase statuses, `implementation_status`, `portfolio_final_status`, blocker summary, next actions, and unresolved rows.
- Top-level public status matches release gate final status, not implementation status.
- False-green audit rejects UI-only, scan-only, OCR-missing, docs-claim, and silent skip cases.
- HTML report is readable, Chinese, path-redacted, and lists target/current status without overstating acceptance.

## Commands

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_105_portfolio_release_gate.py
PYTHONPATH=backend python3 -m data_service portfolio report --workspace-id v2_101_105_real
```
