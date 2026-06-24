# V2.58 / Phase 134 Developer Onboarding Restore UX Development Plan

Date: 2026-06-23

## 1. Phase Goal

V2.58 completes the stage by producing a maintainer-facing restore/onboarding package that explains:

- dependency baseline;
- canonical acceptance commands;
- common failure diagnosis;
- sandbox/TestClient limitations;
- redaction and private-path safety.

## 2. Implementation Scope

New implementation file:

```text
backend/data_service/code_assets/human_agent_deepening/restore_ux.py
```

Existing adapter files may be extended:

```text
backend/data_service/code_assets/human_agent_deepening/persistence.py
backend/data_service/mcp_code_human_agent_deepening_tools.py
backend/data_service/cli_code_human_agent_deepening.py
backend/app/api/v1/code_assets_human_agent_deepening.py
```

Focused test:

```text
backend/tests/test_v2_58_restore_ux.py
```

Real E2E script:

```text
backend/scripts/v2_58_real_e2e.py
```

Protected files must not be modified:

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 3. Required Artifacts

```text
workspace/assets/codebase/{codebase_id}/human_agent_deepening/restore_ux/restore_checklist.md
workspace/assets/codebase/{codebase_id}/human_agent_deepening/restore_ux/troubleshooting.md
workspace/assets/codebase/{codebase_id}/human_agent_deepening/restore_ux/onboarding_report.json
```

## 4. Development Steps

1. Add persistence helpers and artifact refs.
2. Implement `RestoreUXService`.
3. Read V2.53 runner, dependency baseline, restore guide, and V2.54-V2.57 artifact availability.
4. Generate restore checklist and troubleshooting markdown.
5. Generate onboarding report with redacted environment facts, acceptance commands, failure diagnosis coverage, and `path_redaction_passed`.
6. Add MCP/CLI/HTTP build/read parity.
7. Add focused tests and real E2E.

## 5. Exit Criteria

- Focused tests pass.
- Public surface guard passes.
- V2.46-V2.57 accepted gates still pass.
- Real E2E passes on data_service.
- PRD/spec review passes.
- False-green audit passes.
- Acceptance audit is written.
