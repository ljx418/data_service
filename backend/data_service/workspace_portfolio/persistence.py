"""Persistence helpers for workspace portfolio artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json


def portfolio_dir(workspace: Path) -> Path:
    return Path(workspace) / "portfolio"


def artifact_path(workspace: Path, filename: str) -> Path:
    return portfolio_dir(workspace) / filename


def write_artifact(workspace: Path, filename: str, payload: dict[str, Any]) -> None:
    write_json(artifact_path(workspace, filename), payload)


def read_artifact(workspace: Path, filename: str) -> dict[str, Any]:
    payload = read_json(artifact_path(workspace, filename), None)
    if not payload:
        raise FileNotFoundError(filename)
    return payload


def remove_artifacts(workspace: Path, filenames: list[str]) -> None:
    for filename in filenames:
        path = artifact_path(workspace, filename)
        if path.exists():
            path.unlink()


def write_text_artifact(workspace: Path, filename: str, text: str) -> None:
    path = artifact_path(workspace, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_text_artifact(workspace: Path, filename: str) -> str:
    path = artifact_path(workspace, filename)
    if not path.exists():
        raise FileNotFoundError(filename)
    return path.read_text(encoding="utf-8")
