"""V2.99 external project E2E governance service."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import external_path_artifact_refs, read_project_paths, read_project_smoke_matrix, read_unavailable_resolution, write_external_path
from .shared import apply_redaction_guard, base_artifact, public_payload, status_summary, unresolved_item, worst_status


PROJECT_IDS = ["data_service", "codexPat", "HarnessOS", "Navia"]


class ExternalProjectPathRegistry:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_external_path(self, codebase_id: str, project_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        state = project_state or {}
        generated_at = now()
        refs = external_path_artifact_refs(codebase_id)
        project_paths = dict(state.get("project_paths") or {})
        smoke_commands = dict(state.get("smoke_commands") or {})
        rows = []
        unresolved = []
        evidence_refs: list[Any] = []
        for project_id in PROJECT_IDS:
            raw_path = str(project_paths.get(project_id) or "").strip()
            path = Path(raw_path).expanduser() if raw_path else None
            readable = bool(path and path.exists() and path.is_dir())
            command = str(smoke_commands.get(project_id) or "").strip()
            if not readable:
                status = "structured_unavailable"
                reason = "project path is missing or unreadable"
            elif not command:
                status = "needs_review"
                reason = "project smoke command is missing"
            else:
                status, reason = _run_smoke(command, path)
                evidence_refs.append(f"command://external_path/{project_id}")
            row = {"project_id": project_id, "path_status": "readable" if readable else "missing_or_unreadable", "path_ref": f"provided://{project_id}" if raw_path else "", "smoke_status": status, "status": status, "command_ref": f"command://external_path/{project_id}" if command else "", "unavailable_reason": reason}
            rows.append(row)
            if status != "accepted":
                kind = "structured_unavailable" if status == "structured_unavailable" else "needs_review" if status == "needs_review" else "structured_blocker"
                unresolved.append(unresolved_item(kind, reason, item_id=project_id, next_action="provide readable project path and smoke command"))
        status = worst_status([row["status"] for row in rows])
        paths = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase="V2.99", artifact_type="external_project_paths", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs, unresolved=unresolved, status=status, next_actions=["knowledge_code_automated_evidence_closure_external_path_read"])
        paths.update({"data": {"projects": rows}, "summary": status_summary(rows)})
        matrix = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase="V2.99", artifact_type="external_project_smoke_matrix", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs, unresolved=unresolved, status=status)
        matrix.update({"data": {"projects": rows}})
        resolution = _resolution(status, rows)
        apply_redaction_guard(paths, matrix, resolution)
        write_external_path(self.workspace, codebase_id, paths, matrix, resolution)
        return self.read_external_path(codebase_id)

    def read_external_path(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        paths = read_project_paths(self.workspace, codebase_id)
        matrix = read_project_smoke_matrix(self.workspace, codebase_id)
        resolution = read_unavailable_resolution(self.workspace, codebase_id)
        return {
            "schema_version": "v2.96-100",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.99",
            "artifact_type": "external_path_registry",
            "status": str(paths.get("status") or "needs_review"),
            "data": {"project_paths": paths, "project_smoke_matrix": matrix, "unavailable_resolution": resolution},
            "summary": dict(paths.get("summary") or {}),
            "artifact_refs": external_path_artifact_refs(codebase_id),
            "evidence_refs": list(paths.get("evidence_refs") or []),
            "warnings": list(paths.get("warnings") or []),
            "unresolved": list(paths.get("unresolved") or []),
            "next_actions": ["knowledge_code_automated_evidence_closure_external_path_read"],
        }


def _run_smoke(command: str, cwd: Path) -> tuple[str, str]:
    try:
        result = subprocess.run(command, cwd=cwd, shell=True, text=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30, check=False)
    except subprocess.TimeoutExpired:
        return "structured_blocker", "project smoke command timed out"
    except OSError:
        return "structured_blocker", "project smoke command could not start"
    if result.returncode == 0:
        return "accepted", "project smoke command passed"
    return "failed", f"project smoke command failed with exit code {result.returncode}"


def _resolution(status: str, rows: list[dict[str, Any]]) -> str:
    lines = ["# V2.99 External Project Unavailable Resolution", "", f"Status: {status}", ""]
    for row in rows:
        lines.append(f"- {row['project_id']}: {row['status']} / {row['unavailable_reason']}")
    lines.extend(["", "Missing external project paths are structured_unavailable and cannot be counted as accepted."])
    return "\n".join(lines)


def public_external_path_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)

