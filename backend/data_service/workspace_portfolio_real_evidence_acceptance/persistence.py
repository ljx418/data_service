"""Lineage-bound persistence helpers for V2.116-V2.120 artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json


def acceptance_dir(workspace: Path) -> Path:
    return Path(workspace) / "portfolio_real_evidence_acceptance"


def runs_dir(workspace: Path) -> Path:
    return acceptance_dir(workspace) / "runs"


def decisions_dir(workspace: Path) -> Path:
    return acceptance_dir(workspace) / "decisions"


def run_dir(workspace: Path, run_id: str) -> Path:
    return runs_dir(workspace) / run_id


def run_artifact_path(workspace: Path, run_id: str, filename: str) -> Path:
    return run_dir(workspace, run_id) / filename


def latest_path(workspace: Path) -> Path:
    return acceptance_dir(workspace) / "latest.json"


def decision_path(workspace: Path, decision_set_id: str) -> Path:
    return decisions_dir(workspace) / f"{decision_set_id}.json"


def write_run_artifact(workspace: Path, run_id: str, filename: str, payload: dict[str, Any]) -> None:
    write_json(run_artifact_path(workspace, run_id, filename), payload)


def read_run_artifact(workspace: Path, run_id: str, filename: str) -> dict[str, Any]:
    payload = read_json(run_artifact_path(workspace, run_id, filename), None)
    if not payload:
        raise FileNotFoundError(f"runs/{run_id}/{filename}")
    return payload


def write_latest(workspace: Path, payload: dict[str, Any]) -> None:
    write_json(latest_path(workspace), payload)


def read_latest(workspace: Path) -> dict[str, Any]:
    payload = read_json(latest_path(workspace), None)
    if not payload:
        raise FileNotFoundError("latest.json")
    return payload


def write_decision_set(workspace: Path, decision_set_id: str, payload: dict[str, Any]) -> None:
    write_json(decision_path(workspace, decision_set_id), payload)


def read_decision_set(workspace: Path, decision_set_id: str) -> dict[str, Any]:
    payload = read_json(decision_path(workspace, decision_set_id), None)
    if not payload:
        raise FileNotFoundError(f"decisions/{decision_set_id}.json")
    return payload


def write_text_artifact(workspace: Path, run_id: str, filename: str, text: str) -> None:
    path = run_artifact_path(workspace, run_id, filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def read_text_artifact(workspace: Path, run_id: str, filename: str) -> str:
    path = run_artifact_path(workspace, run_id, filename)
    if not path.exists():
        raise FileNotFoundError(f"runs/{run_id}/{filename}")
    return path.read_text(encoding="utf-8")
