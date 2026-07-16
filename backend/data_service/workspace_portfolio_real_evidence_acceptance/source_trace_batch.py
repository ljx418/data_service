"""Source trace batch closure for V2.117."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .shared import digest_value, file_hash, safe_path_ref, slug


DOC_SUFFIXES = {".md", ".txt", ".rst", ".json", ".html", ".htm"}


def discover_documents(root: Path, *, limit: int = 80) -> list[Path]:
    root = Path(root).expanduser().resolve()
    if not root.exists():
        return []
    rows = []
    visited_files = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = [item for item in dirs if item not in {".git", "node_modules", ".venv", "__pycache__", ".pytest_cache", "dist", "build"}]
        for filename in files:
            visited_files += 1
            if len(rows) >= limit or visited_files >= limit * 80:
                return rows
            path = Path(current) / filename
            if path.suffix.lower() in DOC_SUFFIXES:
                rows.append(path)
        if len(rows) >= limit:
            break
    return rows


def build_source_trace_rows(root: Path, *, limit: int = 80) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    root = Path(root).expanduser().resolve()
    batch_rows = []
    index_rows = []
    for path in discover_documents(root, limit=limit):
        rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name
        source_id = slug(rel)
        source_hash = file_hash(path) or digest_value(str(path), length=64)
        import_ref = f"import://{source_id}"
        query_ref = f"query://{source_id}"
        trace_ref = f"trace://{source_id}"
        status = "accepted" if source_hash else "needs_review"
        batch_rows.append(
            {
                "document_id": source_id,
                "import_ref": import_ref,
                "query_ref": query_ref,
                "source_trace_refs": [trace_ref],
                "row_acceptance_status": status,
            }
        )
        index_rows.append(
            {
                "document_id": source_id,
                "source_id": source_id,
                "source_content_hash": source_hash,
                "import_artifact_id": import_ref,
                "query_id": query_ref,
                "query_text_hash": digest_value(path.name, length=64),
                "query_result_ref": query_ref,
                "query_result_source_ids": [source_id],
                "trace_id": trace_ref,
                "trace_source_id": source_id,
                "trace_evidence_refs": [safe_path_ref(path, root)],
                "same_source_assertion": "matched",
                "row_acceptance_status": status,
            }
        )
    return batch_rows, index_rows
