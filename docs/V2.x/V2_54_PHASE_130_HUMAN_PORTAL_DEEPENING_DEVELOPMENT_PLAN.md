# V2.54 / Phase 130 Human Portal Deepening Development Plan

## 1. Phase Verdict

Status: ready for implementation after this phase plan, acceptance plan, and pre-implementation audit.

This phase implements the first V2.54-V2.58 target capability: Human Portal Deepening. It must not broaden the project into full design-intent recovery, full call graph, runtime topology, data/control flow, or type inference.

## 2. Scope

In scope:

- Build a deeper human-readable project portal from persisted artifacts.
- Produce project story, risk priority, reading path, chart audit, and Portal V2 HTML.
- Expose the artifacts through evidence-first read surfaces after implementation.
- Preserve V2.46-V2.53 artifacts as read-only inputs.

Out of scope:

- Editing analyzed project source code.
- Rewriting upstream documentation.
- Inferring complete runtime topology or full call graph.
- Modifying `backend/app/api/v1/data_service.py` or `backend/data_service/service.py` without explicit user approval.

## 3. Planned Code Surfaces

Primary implementation:

```text
backend/data_service/code_assets/human_agent_deepening/
  __init__.py
  shared.py
  persistence.py
  human_portal.py
```

Public integration surfaces:

```text
backend/data_service/mcp_code_human_agent_deepening_tools.py
backend/data_service/cli_code_human_agent_deepening.py
backend/app/api/v1/code_assets_human_agent_deepening.py
```

Small registry/router wiring may be needed in existing non-legacy entry files. Any required wiring must be listed in the phase acceptance audit.

## 4. Inputs

Read-only input candidates:

- V2.48 Human Portal model, chart, and HTML.
- V2.47 profile onboarding artifacts.
- Architecture inventory, taxonomy, doc-code alignment, public surface evidence, relationship evidence, human review report, and context pack artifacts when available.
- V2.50 governance overlay artifacts when available.
- V2.52 closure and V2.53 acceptance artifacts.

Missing input artifacts must become `warnings` or `unresolved` entries. Missing artifacts must not be hidden or converted to accepted evidence.

## 5. Outputs

All outputs must live under:

```text
workspace/assets/codebase/{codebase_id}/human_agent_deepening/human_portal_deepening/
```

Required outputs:

```text
project_story.json
risk_priority.json
reading_path.json
chart_audit.json
project_portal_v2.html
```

Shared fields for JSON artifacts:

- `schema_version`
- `codebase_id`
- `phase`
- `generated_at`
- `artifact_refs`
- `evidence_refs`
- `warnings`
- `unresolved`

## 6. Functional Requirements

### Project Story

Must summarize:

- project identity and current accepted baseline;
- main entry surfaces and boundaries;
- known limitations and non-claims;
- next actions with evidence refs.

### Risk Priority

Must produce risk items with:

- `id`
- `title`
- `severity`
- `evidence_refs`
- `recommended_action`
- `status`

Allowed status values:

- `accepted_evidence`
- `needs_review`
- `structured_unavailable`
- `structured_blocker`

`accepted_evidence` means the risk item has evidence, not that V2.54 is accepted.

### Reading Path

Must provide:

- maintainer reading order;
- reviewer reading order;
- agent reading order when applicable;
- omitted items with reason.

### Chart Audit

Must verify:

- rendered chart artifacts exist or are marked unavailable;
- raw Mermaid source is not presented as the final chart;
- chart statements are backed by artifact refs.

### Portal V2 HTML

Must display:

- project story;
- risk priority;
- reading path;
- acceptance state;
- warnings/unresolved items;
- artifact refs or equivalent evidence links.

HTML must not invent facts outside persisted artifacts.

## 7. User Experience Goal

After V2.54 implementation, a maintainer should be able to open the portal and answer:

- What is the current accepted baseline?
- What are the highest-risk or needs-review areas?
- What should I read first?
- Which evidence supports each displayed statement?
- What is unavailable or unresolved?
- What is the next audit or implementation action?

## 8. Development Sequence

1. Add persistence helpers for the `human_agent_deepening/human_portal_deepening/` namespace.
2. Add shared envelope, redaction, evidence, warning, and unresolved helpers if not already available.
3. Implement project story builder.
4. Implement risk priority builder.
5. Implement reading path builder.
6. Implement chart audit builder.
7. Implement Portal V2 renderer.
8. Add MCP/CLI/HTTP build/read surfaces.
9. Add focused tests.
10. Run phase acceptance and update coverage matrix only after evidence exists.

## 9. Stop Conditions

Stop implementation if:

- a displayed statement lacks evidence and is not marked unresolved;
- raw Mermaid source is used as the final chart output;
- unavailable input is treated as accepted;
- legacy large files require modification without explicit approval;
- implementation needs to claim full call graph, runtime topology, data/control flow, type inference, or complete design-intent recovery.
