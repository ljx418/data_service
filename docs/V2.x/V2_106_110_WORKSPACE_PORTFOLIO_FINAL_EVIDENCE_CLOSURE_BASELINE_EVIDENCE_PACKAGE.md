# V2.106-V2.110 Baseline Evidence Package

## 1. Purpose

This document closes the P0 baseline evidence gap. Phase 182 must not rely on summary claims alone; it must read and hash the V2.101-V2.105 baseline evidence package.

## 2. Required Baseline Inputs

| Baseline artifact | Required role |
| --- | --- |
| `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_ACCEPTANCE_AUDIT_REPORT.md` | authoritative V2.101-V2.105 implementation acceptance statement |
| `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_FULL_COVERAGE_MATRIX.md` | row-level previous coverage state |
| `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_AUTOMATED_VISUAL_ACCEPTANCE_REPORT.html` | visual/HTTP acceptance report and screenshot-unavailable explanation |
| `v2_101_105_visual_acceptance_assets/cli_e2e_summary.json` | real CLI E2E summary |
| `v2_101_105_visual_acceptance_assets/http_e2e_summary.json` | real HTTP E2E summary |
| `v2_101_105_visual_acceptance_assets/screenshot_result.json` | headless screenshot structured unavailable evidence |
| `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_TARGET_STATE.drawio` | previous target state and status view |
| `V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_TARGET_ARCHITECTURE.md` | previous architecture target |

## 3. Baseline Facts To Verify

Phase 182 must verify, not assume:

```text
implementation_status=accepted
portfolio_final_status=structured_unavailable
project_count=18
accepted_project_count=1
needs_review_count=17
ocr_required_count=86
headless_screenshot_status=structured_unavailable
```

If any value cannot be verified from baseline artifacts, Phase 182 must produce `needs_review`, not accepted.

## 4. Hash Manifest

Phase 182 must generate:

```text
baseline_evidence_manifest.json
```

Required fields:

```json
{
  "schema_version": "v2.106-110.baseline_evidence_manifest.1",
  "run_id": "run_...",
  "baseline_refs": [
    {
      "path": "repo-relative path",
      "sha256": "hex",
      "required": true,
      "exists": true
    }
  ],
  "verified_facts": {
    "implementation_status": "accepted",
    "portfolio_final_status": "structured_unavailable"
  },
  "missing_or_mismatched": []
}
```

Missing required baseline artifacts must block Phase 182 accepted status.

## 5. Source-of-truth Precedence

When documents disagree, use this precedence:

1. Real command/API/MCP evidence artifact with hash.
2. Acceptance audit report.
3. Coverage matrix row with evidence refs.
4. Target architecture.
5. Drawio target state.
6. PRD statement.

Drawio and PRD statements cannot override real evidence artifacts.

