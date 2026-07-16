# V2.118 / Phase 194 Headless UI Visual Acceptance Plan and Audit

Status: `implemented_with_environment_dependent_result`

## Development Plan

- Add read-only `/knowledge` real evidence panel.
- Add API client functions for `portfolio-real-evidence`.
- Generate `ui_capture_results.json` and `ui_screenshot_manifest.json`.
- Use stable selector contract: `[data-testid='portfolio-real-evidence-panel']`.

## Acceptance Plan

- Screenshot evidence accepted only when selector assertions pass and screenshot hash/path exist.
- Browser missing is `structured_unavailable`.
- Blank page, 500 page, or missing DOM contract is not accepted.
- UI must not write anchor, approval, revoke, or approved out-of-scope decisions.

## Audit Opinion

```text
fatal_findings=none
major_findings=none
ui_write_surface=not_added
implementation_result=pass_for_read_only_contract
```

Focused test:

```text
backend/tests/test_v2_118_headless_ui_visual_acceptance.py
```
