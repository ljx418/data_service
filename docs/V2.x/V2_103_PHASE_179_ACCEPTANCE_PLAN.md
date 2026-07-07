# V2.103 / Phase 179 Acceptance Plan

## Acceptance Criteria

- Real workspace media/doc folders produce source candidate and media readiness rows.
- OCR provider absence is visible as `structured_unavailable`.
- No image, scan, or OCR-dependent row is accepted without OCR evidence.
- Readiness-only rows remain non-accepted unless ingest/query/source trace evidence exists.

## Commands

```text
PYTHONPATH=backend pytest -q backend/tests/test_v2_103_document_media_intake.py
PYTHONPATH=backend python3 -m data_service portfolio build --workspace-id v2_101_105_real --root /mnt/c/workspace --limit 40 --max-code-projects 1
```
