# V2.106-V2.110 Prototype UX Spec：Knowledge Portfolio Final Evidence

## 1. Purpose

This document closes the UI prototype gap. The drawio file is an architecture and target-state diagram, not a page-level `/knowledge` prototype.

## 2. Target Route

```text
/knowledge?view=portfolio
```

The page must read persisted artifacts through HTTP/API read models. It must not hardcode accepted conclusions.

## 3. Page Information Architecture

Required panels:

1. Final Evidence Status Header
2. Run Selector and Freshness Banner
3. Coverage and Architecture Closure Panel
4. Project Build Queue and Diagnosis Table
5. OCR / Media Evidence Matrix
6. Document Source Trace Closure Table
7. UI Evidence Capture Panel
8. Final Release Gate and False-green Recheck
9. Evidence Drawer

## 4. Component Requirements

### 4.1 Final Evidence Status Header

Fields:

- `implementation_status`
- `portfolio_final_status`
- `run_id`
- `generated_at`
- blocker count
- needs_review count
- structured_unavailable count

Required behavior:

- show `portfolio_final_status` separately from `implementation_status`
- never display final green if high-risk blockers exist

### 4.2 Run Selector and Freshness Banner

Fields:

- latest run
- selected run
- stale status
- mixed-run rejection reason

States:

- loading
- empty
- stale
- mixed-run blocked
- accepted
- non-accepted

### 4.3 Project Build Queue Table

Columns:

- project
- queue state
- execution status
- acceptance status
- failure category
- command refs
- artifact refs
- next action

Required behavior:

- deferred rows remain visible
- timeout/skipped rows are not counted as accepted
- long tables support filtering by status and project type

### 4.4 OCR / Media Evidence Matrix

Columns:

- project
- file
- format
- requires OCR
- provider status
- acceptance status
- evidence refs
- next action

Required behavior:

- OCR missing rows use warning/error styling
- no media row shows accepted without evidence refs

### 4.5 Document Source Trace Closure Table

Columns:

- source file
- source import ref
- query result ref
- source trace refs
- acceptance status
- failure category
- next action

Required behavior:

- readiness-only rows are visibly non-accepted
- evidence drawer opens source refs

### 4.6 Final Release Gate

Fields:

- final decision
- high-risk blocker list
- false-green rejected patterns
- minimal next actions

Required behavior:

- final accepted only when all high-risk rows are accepted or approved out of scope
- HTML report link must not be treated as evidence acceptance

## 5. Evidence Drawer

The drawer must display:

- artifact ref
- evidence ref
- hash or run id where available
- source artifact path
- status rationale
- next action

The drawer must not display raw secrets, full raw tracebacks or unredacted private paths.

## 6. Responsive and Accessibility Requirements

- Tables must remain readable at desktop width.
- Narrow layouts may collapse to stacked rows.
- Status colors require text labels.
- Buttons must have accessible names.
- No text-only color meaning.

## 7. Acceptance Evidence

UI acceptance requires:

- API read result for the selected run.
- Screenshot refs or `ui_evidence_capture.json=structured_unavailable`.
- Field-to-artifact mapping check.
- PRD/spec review that confirms non-accepted states are visible.

