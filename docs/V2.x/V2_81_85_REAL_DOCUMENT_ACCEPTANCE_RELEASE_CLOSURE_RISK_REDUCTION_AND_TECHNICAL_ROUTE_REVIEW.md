# V2.81-V2.85 Risk Reduction and Technical Route Review

## 1. Review Result

Current documentation can reduce implementation ambiguity, but it cannot eliminate external dependency risk. The stage can be planned and implemented safely only if real document availability, privacy handling, source trace evidence, and human approval are handled explicitly.

Status: pass for implementation guidance after this review is included, not pass for implementation acceptance.

## 2. Route Options

| Route | Description | Strengths | Weaknesses | Verdict |
| --- | --- | --- | --- | --- |
| A. User-provided real documents | User supplies representative real documents or approved redacted copies | Highest acceptance value; directly validates target user experience | Requires user input and privacy control; may block automation | Recommended for final acceptance |
| B. Repo-owned project documents | Use existing project docs under `docs/` as real project documentation | Immediately executable; not mock-only; good for automation and smoke acceptance | Less representative of user business documents; human UX acceptance may remain `needs_review` | Recommended fallback for automated dry run |
| C. Structured unavailable | No valid real document source is available | Prevents false-green acceptance; preserves audit truth | Does not complete user experience acceptance | Required fallback when A/B unavailable |
| D. Mock or synthetic documents | Use generated examples or fixtures | Useful for unit tests and development fixtures | Invalid as real-document acceptance evidence | Rejected for acceptance |

Default route:

1. Use Route A when the user provides real or redacted real documents.
2. Use Route B for automated development and smoke reruns if Route A is not available.
3. Use Route C when no valid material can be accessed.
4. Never use Route D for accepted real-document UX evidence.

## 3. Risk Register

| Risk | Severity | Detection | Mitigation | Acceptance Impact |
| --- | --- | --- | --- | --- |
| Real documents unavailable | Major | Sample contract has no valid source | Mark `needs_review` or `structured_unavailable`; use Route B only for automation fallback | Blocks final real-document UX accepted |
| Sensitive document content leaks | Major | Artifact contains raw private content, path, token, or traceback | Redact content; store safe metadata and repo-relative refs | Blocks public artifact acceptance |
| Source trace missing | Major | Query result has no source refs or evidence refs | Record `needs_review` or `structured_blocker`; do not accept trace experience | Blocks V2.83 accepted |
| GraphRAG overclaim | Major | Report claims full graph, runtime topology, or complete intent recovery | Add boundary notes and false-green audit | Blocks V2.83 accepted |
| Quality correction lacks human review | Major | Correction recommendation has no evidence or approval | Keep `needs_review`; expose next action | Blocks V2.84 accepted |
| External project path missing | Major | `codexPat`, `HarnessOS`, or `Navia` path unavailable | Preserve `structured_unavailable` | Blocks all-project release accepted |
| Human approval missing | Major | No release sign-off artifact | Keep final release `needs_review` | Blocks V2.85 final accepted |
| Protected legacy file drift | Major | Diff shows modifications to protected files | Stop and ask for explicit approval or revert our own change | Blocks implementation exit |

## 4. Development Risk Assessment

After adding the implementation blueprint and detailed phase package, the remaining high-risk items are external or evidence-dependent rather than specification gaps.

Risks that documentation can reduce:

- unclear code placement;
- unclear artifact contract;
- unclear focused test target;
- unclear accepted vs unavailable state;
- unclear public surface expectation.

Risks that documentation cannot fully remove:

- whether the user provides representative real documents;
- whether external repositories are available on this machine;
- whether a human approves final release;
- whether real source trace quality is sufficient after execution.

## 5. Acceptance Risk Decision

The stage may proceed into phase-specific pre-implementation planning if all fatal/major documentation findings are closed. The stage must stop for human confirmation if any of these occur during implementation or validation:

- real document evidence is unavailable but a result would need to be accepted;
- sensitive material cannot be safely redacted;
- protected legacy file modification becomes necessary;
- source trace is missing but product goals require accepted trace experience;
- final release accepted would require bypassing external project status or human approval.

## 6. Final Route Recommendation

For automated development:

- implement against Route B-compatible repo-owned documents where possible;
- preserve Route A as the final human-representative acceptance path;
- record Route C whenever real document conditions are absent;
- exclude Route D from acceptance evidence.

This route keeps automation moving while preventing false acceptance of unverified real-document user experience.
