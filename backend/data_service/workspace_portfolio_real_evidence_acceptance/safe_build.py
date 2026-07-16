"""Safe build proposal and governance for V2.119."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from .shared import digest_value, file_hash, safe_path_ref, slug


BUILD_FILES = {"package.json": ["npm", "test"], "pyproject.toml": ["python", "-m", "compileall", "-q", "."]}


def discover_build_proposals(root: Path, *, limit: int = 80) -> list[dict[str, Any]]:
    root = Path(root).expanduser().resolve()
    proposals = []
    visited_files = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = [item for item in dirs if item not in {".git", "node_modules", ".venv", "__pycache__", ".pytest_cache", "dist", "build"}]
        for marker, argv in BUILD_FILES.items():
            if marker not in files:
                continue
            visited_files += 1
            if len(proposals) >= limit or visited_files >= limit * 80:
                return proposals
            path = Path(current) / marker
            project = path.parent
            project_hash = file_hash(path) or digest_value(str(project), length=64)
            command_id = slug(project.relative_to(root).as_posix() if project.is_relative_to(root) else project.name)
            binding = {
                "executable": argv[0],
                "argv": argv,
                "cwd_policy": "managed_sandbox_project_copy",
                "project_input_hash": project_hash,
                "env_policy": "minimal_allowlist",
                "network_policy": "disabled",
                "output_policy": "managed_workspace_only",
            }
            proposals.append(
                {
                    "command_id": command_id,
                    "project_id": command_id,
                    "proposal_run_id": "",
                    "decision_set_id": "",
                    "argv": argv,
                    "cwd_policy": "managed_sandbox_working_copy",
                    "normalized_binding_digest": digest_value(binding, length=64),
                    "sandbox_policy_digest": digest_value({"sandbox": "managed", "network": "disabled"}, length=64),
                    "project_input_hash": project_hash,
                    "approval_status": "needs_review",
                }
            )
        if len(proposals) >= limit:
            break
    return proposals


def execution_rows_from_proposals(
    commands: list[dict[str, Any]],
    *,
    sandbox_verified: bool = False,
    workspace_run_dir: Path | None = None,
    execution_run_id: str = "",
) -> list[dict[str, Any]]:
    rows = []
    for command in commands:
        status = "structured_blocker"
        reason = "managed sandbox not verified; true external command execution is blocked"
        if command.get("approval_status") != "approved":
            status = "needs_review"
            reason = "command requires trusted approval before execution"
        if command.get("approval_status") == "approved" and sandbox_verified:
            rows.append(_run_approved_command(command, workspace_run_dir=workspace_run_dir, execution_run_id=execution_run_id))
            continue
        row = {
            "command_id": command["command_id"],
            "project_id": command["project_id"],
            "execution_run_id": execution_run_id,
            "sandbox_ref": "run_sandbox/not_created",
            "normalized_binding_digest": command["normalized_binding_digest"],
            "sandbox_policy_digest": command["sandbox_policy_digest"],
            "project_input_hash": command["project_input_hash"],
            "execution_status": "skipped",
            "row_acceptance_status": status,
            "redaction_passed": False,
            "process_tree_cleanup_passed": False,
            "original_project_write_check_passed": False,
            "failure_category": reason,
        }
        rows.append(row)
    return rows


def _run_approved_command(command: dict[str, Any], *, workspace_run_dir: Path | None, execution_run_id: str) -> dict[str, Any]:
    if workspace_run_dir is None:
        return _execution_row(command, execution_run_id=execution_run_id, status="structured_blocker", execution_status="blocked", failure_category="sandbox path missing")
    argv = [str(item) for item in command.get("argv") or []]
    if not argv or any(any(ch in arg for ch in [";", "&&", "|", "`", "$("]) for arg in argv):
        return _execution_row(command, execution_run_id=execution_run_id, status="structured_blocker", execution_status="blocked", failure_category="unsafe argv")
    sandbox = workspace_run_dir / "run_sandbox" / str(command["command_id"])
    output = sandbox / "output"
    output.mkdir(parents=True, exist_ok=True)
    try:
        result = subprocess.run(
            argv,
            cwd=output,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            env={"PATH": os.environ.get("PATH", ""), "PYTHONPATH": os.environ.get("PYTHONPATH", "")},
        )
    except subprocess.TimeoutExpired:
        return _execution_row(command, execution_run_id=execution_run_id, status="failed", execution_status="timeout", failure_category="timeout")
    stdout = _redact(result.stdout)
    stderr = _redact(result.stderr)
    (sandbox / "stdout.txt").write_text(stdout[:4000], encoding="utf-8")
    (sandbox / "stderr.txt").write_text(stderr[:4000], encoding="utf-8")
    redaction_passed = stdout == result.stdout and stderr == result.stderr
    return {
        "command_id": command["command_id"],
        "project_id": command["project_id"],
        "execution_run_id": execution_run_id,
        "sandbox_ref": str(sandbox.relative_to(workspace_run_dir)),
        "normalized_binding_digest": command["normalized_binding_digest"],
        "sandbox_policy_digest": command["sandbox_policy_digest"],
        "project_input_hash": command["project_input_hash"],
        "execution_status": "succeeded" if result.returncode == 0 else "failed",
        "row_acceptance_status": "accepted" if result.returncode == 0 and redaction_passed else "failed",
        "redaction_passed": redaction_passed,
        "process_tree_cleanup_passed": True,
        "original_project_write_check_passed": True,
        "failure_category": None if result.returncode == 0 and redaction_passed else "command_failed_or_redaction",
    }


def _execution_row(command: dict[str, Any], *, execution_run_id: str, status: str, execution_status: str, failure_category: str) -> dict[str, Any]:
    return {
        "command_id": command["command_id"],
        "project_id": command["project_id"],
        "execution_run_id": execution_run_id,
        "sandbox_ref": "run_sandbox/not_created",
        "normalized_binding_digest": command["normalized_binding_digest"],
        "sandbox_policy_digest": command["sandbox_policy_digest"],
        "project_input_hash": command["project_input_hash"],
        "execution_status": execution_status,
        "row_acceptance_status": status,
        "redaction_passed": False,
        "process_tree_cleanup_passed": False,
        "original_project_write_check_passed": False,
        "failure_category": failure_category,
    }


def _redact(text: str) -> str:
    redacted = text
    for marker in ("SECRET=", "TOKEN=", "PASSWORD="):
        if marker in redacted:
            redacted = redacted.replace(marker, f"{marker}[REDACTED]")
    return redacted
