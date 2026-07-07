# V2.101 / Phase 177 Development Plan

## Scope

- Implement read-only workspace portfolio discovery for real workspace roots.
- Generate `project_registry.json` and `discovery_report.md`.
- Keep all scanned project directories read-only.

## Implementation Targets

- Add `backend/data_service/workspace_portfolio/` service package.
- Add portfolio CLI/MCP/HTTP read/build surface.
- Persist artifacts under `workspace/{workspace_id}/portfolio/`.

## Constraints

- Do not modify `backend/app/api/v1/data_service.py` or `backend/data_service/service.py`.
- Do not install OCR, LibreOffice, poppler, or other system dependencies.
- Do not write into `/mnt/c/workspace/*` project directories.
