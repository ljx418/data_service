# V2.119 / Phase 195 Safe Build Allowlist Governance Plan and Audit

Status: `implemented_with_true_external_execution_blocked`

## Development Plan

- Discover build command proposals from real workspace marker files.
- Generate `safe_build_allowlist.json` with approval state and complete normalized binding digest.
- Generate `safe_build_execution_results.json`.
- Provide deterministic managed sandbox execution only for approved fixture commands.
- Keep real external workspace build/test/lint execution blocked unless trusted decision set and managed sandbox are verified.

## Acceptance Plan

- Unapproved command must not execute.
- Sandbox unavailable means proposal plus structured blocker or needs_review, not accepted.
- Deterministic approved command can pass inside managed sandbox fixture.
- Shell metacharacters, digest mismatch, path escape, secret leakage, or child cleanup failure must not be accepted.

## Audit Opinion

```text
fatal_findings=none
major_findings=none
true_external_build_execution=not_executed
deterministic_sandbox_positive_case=implemented
implementation_result=pass_for_governance
```

Focused test:

```text
backend/tests/test_v2_119_safe_build_allowlist_governance.py
```
