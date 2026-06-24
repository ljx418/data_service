# V2.56 / Phase 132 Doc-Code Governance Evidence Loop Development Plan

Date: 2026-06-23

## 1. Phase Goal

V2.56 turns the accepted V2.50 governance feedback/rule/overlay workflow into an evidence loop that reviewers can read as claim, decision, rule effect, and immutable upstream hash evidence.

This phase must not rewrite source docs, code facts, or upstream V2.50 artifacts.

## 2. Implementation Scope

New implementation file:

```text
backend/data_service/code_assets/human_agent_deepening/evidence_loop.py
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
backend/tests/test_v2_56_doc_code_evidence_loop.py
```

Protected files must not be modified:

```text
backend/app/api/v1/data_service.py
backend/data_service/service.py
```

## 3. Required Artifacts

```text
workspace/assets/codebase/{codebase_id}/human_agent_deepening/doc_code_evidence_loop/evidence_loop.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/doc_code_evidence_loop/decision_history.jsonl
workspace/assets/codebase/{codebase_id}/human_agent_deepening/doc_code_evidence_loop/rule_effect.json
workspace/assets/codebase/{codebase_id}/human_agent_deepening/doc_code_evidence_loop/evidence_loop_report.md
```

## 4. Development Steps

1. Add persistence helpers and artifact refs.
2. Implement `DocCodeEvidenceLoopService`.
3. Read V2.50 governance feedback, rules, and overlay as read-only inputs.
4. Build findings with `supported`, `weak`, `unsupported`, `contradicted`, or `needs_review` status.
5. Build decision history from rule review state.
6. Build rule effect report with upstream hashes before/after and `hash_unchanged: true`.
7. Add MCP, CLI, and HTTP build/read parity.
8. Add focused tests for approve/revoke readback, unchanged upstream hashes, status visibility, and redaction.

## 5. Exit Criteria

- Focused tests pass.
- Public surface guard passes.
- V2.46-V2.55 accepted gates still pass.
- Real-project E2E passes for `data_service` and one external project or records structured unavailable.
- PRD/spec review passes.
- False-green audit passes.
- Acceptance audit is written.
