"""V2.94 external project path and E2E closure service."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    external_project_closure_artifact_refs,
    read_e2e_result_matrix,
    read_path_binding_decision,
    read_unavailable_decisions,
    write_external_project_closure,
)
from .shared import apply_redaction_guard, base_artifact, public_payload, status_summary, unresolved_item, worst_status


PROJECT_IDS = ["data_service", "codexPat", "HarnessOS", "Navia"]


class ExternalProjectPathE2EValidator:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_external_project_closure(self, codebase_id: str, project_state: dict[str, Any] | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        state = project_state or {}
        generated_at = now()
        refs = external_project_closure_artifact_refs(codebase_id)
        project_paths = dict(state.get("project_paths") or {})
        smoke_commands = dict(state.get("smoke_commands") or {})
        if "data_service" not in project_paths:
            project_paths["data_service"] = asset.root_path
        projects = [_project_row(project_id, project_paths.get(project_id), smoke_commands.get(project_id), timeout=int(state.get("timeout_seconds") or 60)) for project_id in PROJECT_IDS]
        status = "accepted" if all(row["e2e_status"] == "accepted" for row in projects) else worst_status([row["e2e_status"] for row in projects])
        unresolved = [item for row in projects for item in row.get("unresolved") or []]
        binding = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.94",
            artifact_type="path_binding_decision",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[ref for row in projects for ref in row.get("command_refs") or []],
            unresolved=unresolved,
            status=status,
            next_actions=["knowledge_code_real_acceptance_closure_external_project_closure_read"],
        )
        binding.update({"projects": [{"project_id": row["project_id"], "path_status": row["path_status"], "path_ref": row["path_ref"], "unresolved": row["unresolved"]} for row in projects], "summary": status_summary(projects)})
        matrix = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.94",
            artifact_type="e2e_result_matrix",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[ref for row in projects for ref in row.get("command_refs") or []],
            unresolved=unresolved,
            status=status,
        )
        matrix.update({"projects": projects, "summary": status_summary(projects)})
        decisions = _decisions(projects)
        apply_redaction_guard(binding, matrix, decisions)
        write_external_project_closure(self.workspace, codebase_id, binding, matrix, decisions)
        return self.read_external_project_closure(codebase_id)

    def read_external_project_closure(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = external_project_closure_artifact_refs(codebase_id)
        binding = read_path_binding_decision(self.workspace, codebase_id)
        matrix = read_e2e_result_matrix(self.workspace, codebase_id)
        decisions = read_unavailable_decisions(self.workspace, codebase_id)
        return {
            "schema_version": "v2.91-95",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.94",
            "artifact_type": "external_project_path_e2e_closure",
            "status": str(matrix.get("status") or "structured_unavailable"),
            "data": {"path_binding_decision": binding, "e2e_result_matrix": matrix, "unavailable_decisions": decisions},
            "summary": dict(matrix.get("summary") or {}),
            "artifact_refs": refs,
            "evidence_refs": list(matrix.get("evidence_refs") or []),
            "warnings": [],
            "unresolved": list(matrix.get("unresolved") or []),
            "next_actions": ["knowledge_code_real_acceptance_closure_external_project_closure_read"],
        }


def _project_row(project_id: str, path_value: Any, command: Any, *, timeout: int) -> dict[str, Any]:
    unresolved = []
    path_text = str(path_value or "").strip()
    path = Path(path_text).expanduser() if path_text else None
    if not path or not path.exists():
        unresolved.append(unresolved_item("structured_unavailable", f"{project_id} path is missing", item_id=project_id, next_action=f"provide readable {project_id} path"))
        return {"project_id": project_id, "path_status": "missing", "path_ref": "", "e2e_status": "structured_unavailable", "command_refs": [], "artifact_refs": [], "unresolved": unresolved}
    if not path.is_dir():
        unresolved.append(unresolved_item("structured_blocker", f"{project_id} path is not a directory", item_id=project_id, next_action=f"provide project directory for {project_id}"))
        return {"project_id": project_id, "path_status": "needs_review", "path_ref": f"provided://{project_id}", "e2e_status": "structured_blocker", "command_refs": [], "artifact_refs": [], "unresolved": unresolved}
    command_text = str(command or "").strip()
    if not command_text:
        unresolved.append(unresolved_item("structured_blocker", f"{project_id} smoke command is missing", item_id=f"{project_id}_smoke", next_action=f"provide scoped smoke command for {project_id}"))
        return {"project_id": project_id, "path_status": "readable", "path_ref": f"provided://{project_id}", "e2e_status": "structured_blocker", "command_refs": [], "artifact_refs": [], "unresolved": unresolved}
    exit_code = _run(command_text, cwd=path, timeout=timeout)
    status = "accepted" if exit_code == 0 else "failed"
    if status != "accepted":
        unresolved.append(unresolved_item("structured_blocker", f"{project_id} smoke command failed", item_id=f"{project_id}_smoke", evidence_refs=[f"command://{project_id}_smoke"], next_action=f"fix or rerun {project_id} smoke command"))
    return {"project_id": project_id, "path_status": "readable", "path_ref": f"provided://{project_id}", "e2e_status": status, "command_refs": [f"command://{project_id}_smoke"], "artifact_refs": [], "unresolved": unresolved}


def _run(command: str, *, cwd: Path, timeout: int) -> int:
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return int(result.returncode)
    except subprocess.TimeoutExpired:
        return 124
    except OSError:
        return 127


def _decisions(projects: list[dict[str, Any]]) -> str:
    lines = ["# V2.94 External Project Unavailable Decisions", ""]
    for row in projects:
        lines.append(f"- {row['project_id']}: {row['e2e_status']} ({row['path_status']})")
    lines.extend(["", "Missing or unavailable external projects are structured evidence, not accepted evidence."])
    return "\n".join(lines)


def public_external_project_closure_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)
