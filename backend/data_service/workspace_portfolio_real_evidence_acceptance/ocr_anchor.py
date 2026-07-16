"""OCR anchor discovery for V2.116."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .shared import digest_value, file_hash, safe_path_ref, slug


MEDIA_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp", ".pdf", ".ppt", ".pptx"}
IGNORED_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache", "dist", "build"}


def discover_media(root: Path, *, limit: int = 240) -> list[Path]:
    root = Path(root).expanduser().resolve()
    if not root.exists():
        return []
    results: list[Path] = []
    visited_files = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = [item for item in dirs if item not in IGNORED_DIRS]
        for filename in files:
            visited_files += 1
            if len(results) >= limit or visited_files >= limit * 80:
                return results
            path = Path(current) / filename
            if path.suffix.lower() in MEDIA_SUFFIXES:
                results.append(path)
        if len(results) >= limit:
            break
    return results


def sidecar_anchor(path: Path) -> str:
    candidates = [
        path.with_name(f"{path.name}.ocr-anchor.txt"),
        path.with_suffix(f"{path.suffix}.ocr-anchor.txt"),
        path.with_suffix(".ocr-anchor.txt"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.read_text(encoding="utf-8", errors="replace").strip()
    return ""


def build_anchor_rows(root: Path, *, limit: int = 240) -> list[dict[str, Any]]:
    root = Path(root).expanduser().resolve()
    rows = []
    for path in discover_media(root, limit=limit):
        anchor = sidecar_anchor(path)
        row_status = "accepted" if anchor else "needs_review"
        rows.append(
            {
                "media_id": slug(path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name),
                "source_ref": safe_path_ref(path, root),
                "sha256": file_hash(path) or digest_value(str(path), length=64),
                "ocr_anchor": anchor,
                "anchor_text_hash": digest_value(anchor, length=64) if anchor else "",
                "row_acceptance_status": row_status,
            }
        )
    return rows
