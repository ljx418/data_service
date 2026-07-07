# V2.103 / Phase 179 Development Plan

## Scope

- Implement document and media intake readiness for discovered projects and corpus folders.
- Generate `source_candidate_matrix.json` and `media_readiness.json`.
- Distinguish extractor readiness from actual ingest acceptance.

## Implementation Targets

- Classify Markdown, HTML, JSON, CSV, YAML, PDF, PPT/PPTX, DOCX, and image files by suffix and provider readiness.
- Mark images, scans, and OCR-dependent rows as `structured_unavailable` when OCR/provider evidence is missing.
- Mark text-extractable readiness rows as `needs_review` until ingest/query/source trace evidence exists.

## Constraints

- Do not install OCR, LibreOffice, poppler, or other system dependencies.
- Do not mark readiness-only rows as accepted.
- Do not write into scanned source folders.
