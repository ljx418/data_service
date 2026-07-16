"""Persistence helpers for V2.106-V2.110 final evidence artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json


def evidence_dir(workspace: Path) -> Path:
    return Path(workspace) / "portfolio_final_evidence"


def artifact_path(workspace: Path, filename: str) -> Path:
    return evidence_dir(workspace) / filename


def write_artifact(workspace: Path, filename: str, payload: dict[str, Any]) -> None:
    write_json(artifact_path(workspace, filename), payload)


def read_artifact(workspace: Path, filename: str) -> dict[str, Any]:
    payload = read_json(artifact_path(workspace, filename), None)
    if not payload:
        raise FileNotFoundError(filename)
    return payload


def optional_artifact(workspace: Path, filename: str) -> dict[str, Any] | None:
    try:
        return read_artifact(workspace, filename)
    except FileNotFoundError:
        return None


def write_text_artifact(workspace: Path, filename: str, text: str) -> None:
    path = artifact_path(workspace, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_text_artifact(workspace: Path, filename: str) -> str:
    path = artifact_path(workspace, filename)
    if not path.exists():
        raise FileNotFoundError(filename)
    return path.read_text(encoding="utf-8")
