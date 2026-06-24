# V2.59-V2.62 Phase Readiness and Schema Contracts

Date: 2026-06-23

## 1. Shared Envelope

All V2.59-V2.62 public reads use:

```json
{
  "schema_version": "v2.59-62",
  "workspace_id": "string",
  "codebase_id": "string",
  "phase": "V2.59|V2.60|V2.61|V2.62",
  "generated_at": "ISO-8601 string",
  "artifact_refs": ["artifact URI or repo-relative path"],
  "evidence_refs": ["artifact URI or repo-relative path"],
  "warnings": ["string"],
  "unresolved": [
    {
      "id": "string",
      "reason": "string",
      "status": "needs_review|structured_unavailable|structured_blocker"
    }
  ]
}
```

## 2. V2.59 Surface Contracts

`public_surface_snapshot.json`:

```json
{
  "schema_version": "v2.59-62",
  "source": {
    "mcp_registry": "repo-relative path",
    "cli_registry": "repo-relative path",
    "http_registry": "repo-relative path"
  },
  "mcp_tools": [{"name": "string", "operation": "build|read|view|other"}],
  "cli_commands": [{"command": "string", "operation": "build|read|view|other"}],
  "http_routes": [{"method": "GET|POST", "path": "string", "operation": "build|read|view|other"}],
  "discovery_mode": "registry_inspection",
  "hardcoded_expected_only": false
}
```

`public_surface_parity_matrix.json`:

```json
{
  "capabilities": [
    {
      "capability": "surface|e2e|package|portal",
      "mcp": "present|missing|needs_review",
      "cli": "present|missing|needs_review",
      "http": "present|missing|needs_review",
      "parity_status": "accepted|needs_review|structured_blocker"
    }
  ]
}
```

`public_surface_drift_report.json`:

```json
{
  "drift_items": [
    {
      "surface": "mcp|cli|http",
      "name": "string",
      "category": "added|removed|renamed|schema_drift|route_mismatch|needs_review",
      "evidence_refs": ["string"]
    }
  ]
}
```

## 3. V2.60 E2E Contracts

`project_e2e_matrix.json`:

```json
{
  "projects": [
    {
      "name": "data_service|codexPat|HarnessOS|Navia",
      "status": "accepted|needs_review|structured_unavailable|structured_blocker",
      "evidence_mode": "real_repo|structured_rationale",
      "artifact_refs": ["string"],
      "reason": "string"
    }
  ]
}
```

`project_failure_diagnosis.json` categories:

```text
dependency_drift
sandbox_limit
path_unavailable
artifact_missing
public_surface_drift
real_regression
needs_review
```

## 4. V2.61 Packaging Contracts

`package_manifest.json`:

```json
{
  "entries": [
    {
      "path": "repo-relative path",
      "classification": "source|test|doc|script|evidence|local_tmp|needs_review",
      "recommended_action": "commit|ignore|document|manual_review|do_not_delete"
    }
  ],
  "destructive_action_required": false
}
```

`cleanup_plan.md` must be advisory unless the user explicitly approves destructive actions.

## 5. V2.62 Portal Contracts

`portal_state_summary.json`:

```json
{
  "contract_stability": "accepted|needs_review|structured_blocker",
  "e2e_coverage": "accepted|needs_review|structured_unavailable|structured_blocker",
  "restore_readiness": "accepted|needs_review",
  "delivery_readiness": "accepted|needs_review|structured_blocker",
  "artifact_refs": ["string"]
}
```

`portal_acceptance_panel.json` must keep these statuses visually and structurally distinct:

```text
accepted
needs_review
structured_unavailable
structured_blocker
out_of_scope
```

## 6. Readiness Gates

Before implementation:

- phase development plan exists;
- phase acceptance plan exists;
- phase pre-implementation audit exists;
- fatal and major findings are closed;
- protected file policy is restated;
- real project availability is confirmed or structured rationale rules are restated.
