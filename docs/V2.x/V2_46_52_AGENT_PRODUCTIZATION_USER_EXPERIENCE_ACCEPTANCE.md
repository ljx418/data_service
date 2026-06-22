# V2.46-V2.52 User Experience Acceptance

## 1. Target Experience

At the end of V2.46-V2.52, users should experience data_service as a local project intelligence service that helps humans and coding agents understand, audit, and navigate large projects without repeatedly spending large token budgets on raw repository reading.

The product should feel like:

```text
import project -> build project understanding -> open human portal -> ask Agent for task context -> verify docs/code drift -> keep profile and regression updated
```

## 2. User Scenarios

### 2.1 New Maintainer Reads a Large Project

The maintainer imports HarnessOS or Navia and opens the Human Architecture Portal.

Expected visible output:

- project one-liner;
- main modules and public surfaces;
- target/current/diff architecture;
- key diagrams rendered in place;
- risks, weak evidence, structured blockers;
- recommended reading order.

Acceptance:

- The user can identify first five files/docs to read.
- The report does not hide needs_review.
- Every diagram node can be traced to an artifact.

### 2.2 Codex CLI Agent Fixes a Bug

The agent calls MCP tools before editing.

Expected flow:

1. import or locate codebase;
2. refresh snapshot if needed;
3. read overview;
4. read profile and relationship chain;
5. request task navigation and context pack;
6. run suggested tests.

Acceptance:

- Agent receives a bounded reading order.
- Agent receives evidence-backed impact candidates.
- Agent does not need to scan the whole repository.

### 2.3 Architecture Reviewer Checks Drift

The reviewer compares project docs/drawio target architecture against code facts.

Expected visible output:

- supported claims;
- weakly supported claims;
- unsupported claims;
- contradicted claims;
- governance actions.

Acceptance:

- supported claims have document evidence and code evidence.
- weak/unsupported states are visible.
- governance rules apply as read-time overlay only.

### 2.4 New Project Onboarding

The user imports a new project and generates profile draft.

Expected visible output:

- taxonomy terms;
- entrypoint patterns;
- workflow patterns;
- authority rules;
- no-hardcode audit result.

Acceptance:

- project-specific terms are stored in profile.
- generic extractor remains project-agnostic.

### 2.5 Continuous Regression

The team reruns the full flow after new project intelligence changes.

Expected visible output:

- data_service result;
- HarnessOS result;
- Navia result;
- codexPat result;
- accepted/blocker/unavailable/needs_review status.

Acceptance:

- no accepted row lacks evidence.
- unavailable project/provider is not reported as accepted.
- closure report has no fatal/major findings.

## 3. UX Quality Bar

- HTML report should be navigable without reading raw JSON first.
- Mermaid/SVG diagrams should render in place.
- Tables should summarize status before details.
- Warnings and unresolved items must be visible.
- Agent-facing text should be concise and directly actionable.

