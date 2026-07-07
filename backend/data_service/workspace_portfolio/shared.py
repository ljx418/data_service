"""Shared constants and helpers for workspace portfolio artifacts."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "v2.101-105"
STATUSES = {"accepted", "needs_review", "structured_unavailable", "structured_blocker", "failed", "planned"}
IGNORED_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    ".cache",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    "target",
}
CODE_MARKERS = {
    "pyproject.toml",
    "package.json",
    "requirements.txt",
    "setup.py",
    "go.mod",
    "Cargo.toml",
    "pom.xml",
    "build.gradle",
}
DOC_SUFFIXES = {".md", ".markdown", ".txt", ".html", ".htm", ".json", ".csv", ".yaml", ".yml", ".pdf", ".ppt", ".pptx", ".docx"}
MEDIA_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".pdf", ".ppt", ".pptx"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff"}


def slug(value: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip().lower()).strip("-")
    return text[:64] or "project"


def path_ref(path: Path, root: Path | None = None) -> str:
    resolved = path.expanduser().resolve()
    if root is not None:
        try:
            return f"<workspace-root>/{resolved.relative_to(root.expanduser().resolve()).as_posix()}"
        except ValueError:
            pass
    return f"path-ref://{slug(resolved.name)}"


def unresolved(kind: str, reason: str, *, item_id: str, next_action: str, evidence_refs: list[Any] | None = None) -> dict[str, Any]:
    safe_kind = kind if kind in {"needs_review", "structured_unavailable", "structured_blocker"} else "needs_review"
    return {
        "id": item_id,
        "kind": safe_kind,
        "status": safe_kind,
        "reason": reason,
        "next_action": next_action,
        "evidence_refs": list(evidence_refs or []),
    }


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    statuses = [str(row.get("status") or "needs_review") for row in rows]
    return {
        "accepted_count": sum(1 for item in statuses if item == "accepted"),
        "needs_review_count": sum(1 for item in statuses if item == "needs_review"),
        "structured_unavailable_count": sum(1 for item in statuses if item == "structured_unavailable"),
        "structured_blocker_count": sum(1 for item in statuses if item == "structured_blocker"),
        "failed_count": sum(1 for item in statuses if item == "failed"),
    }


def worst_status(statuses: list[str]) -> str:
    normalized = [item if item in STATUSES else "needs_review" for item in statuses]
    for status in ("structured_blocker", "failed", "structured_unavailable", "needs_review"):
        if status in normalized:
            return status
    return "accepted" if normalized else "needs_review"


def artifact_ref(kind: str, filename: str) -> dict[str, str]:
    return {"type": kind, "artifact_ref": f"workspace_portfolio://portfolio/{filename}"}
