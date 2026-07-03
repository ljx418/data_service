"""V2.91 restoreable acceptance runtime service."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    read_focused_regression_result,
    read_restore_checklist,
    read_runtime_diagnosis,
    runtime_restore_artifact_refs,
    write_runtime_restore,
)
from .shared import apply_redaction_guard, base_artifact, public_payload, status_summary, unresolved_item, worst_status


DEFAULT_FOCUSED_COMMAND = "python -m pytest -q backend/tests/test_v2_86_full_corpus_e2e_hardening.py backend/tests/test_v2_87_route_a_representative_acceptance.py backend/tests/test_v2_88_quality_governance_human_review.py backend/tests/test_v2_89_external_project_e2e_closure.py backend/tests/test_v2_90_release_gate_restore_hygiene.py backend/tests/test_public_surface_guard.py"


class AcceptanceRuntimeRestorer:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_runtime_restore(self, codebase_id: str, runtime_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        state = runtime_state or {}
        generated_at = now()
        refs = runtime_restore_artifact_refs(codebase_id)
        python_command = _python_command(state)
        pytest_probe = _run_command(f"{python_command} -m pytest --version", timeout=int(state.get("timeout_seconds") or 60), display_command="python -m pytest --version")
        venv_probe = _probe_venv_create(python_command, timeout=int(state.get("timeout_seconds") or 60))
        legacy_venv_status = _legacy_venv_status(Path("backend/.venv"))
        focused_command = str(state.get("focused_command") or DEFAULT_FOCUSED_COMMAND)
        run_focused = bool(state.get("run_focused_regression", True))
        focused = _run_command(focused_command, timeout=int(state.get("focused_timeout_seconds") or 120)) if run_focused else _skipped_command(focused_command)
        status = "accepted" if pytest_probe["exit_code"] == 0 and venv_probe["exit_code"] == 0 and focused["exit_code"] == 0 else worst_status(
            [
                "accepted" if pytest_probe["exit_code"] == 0 else "structured_blocker",
                "accepted" if venv_probe["exit_code"] == 0 else "structured_blocker",
                "accepted" if focused["exit_code"] == 0 else "structured_blocker",
            ]
        )
        unresolved = []
        if pytest_probe["exit_code"] != 0:
            unresolved.append(unresolved_item("structured_blocker", "pytest is not available in the selected runtime", item_id="pytest_runtime", next_action="install test dependencies from backend/requirements-test.txt"))
        if venv_probe["exit_code"] != 0:
            unresolved.append(unresolved_item("structured_blocker", "python venv creation failed in the selected runtime", item_id="venv_runtime", next_action="install python3.12-venv or provide a working isolated acceptance runtime"))
        if focused["exit_code"] != 0:
            unresolved.append(unresolved_item("structured_blocker", "focused regression command did not pass", item_id="focused_regression", evidence_refs=["command://focused_regression"], next_action="restore pytest runtime and rerun focused regression"))
        diagnosis = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.91",
            artifact_type="runtime_diagnosis",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=["command://pytest_version", "command://focused_regression"],
            unresolved=unresolved,
            status=status,
            next_actions=["knowledge_code_real_acceptance_closure_runtime_restore_read"],
        )
        diagnosis.update(
            {
                "python_runtime": {
                    "system_python_available": shutil.which("python3") is not None,
                    "venv_create_available": venv_probe["exit_code"] == 0,
                    "pytest_available": pytest_probe["exit_code"] == 0,
                    "legacy_venv_status": legacy_venv_status,
                },
                "commands": [
                    {**pytest_probe, "command_id": "pytest_version", "status": "accepted" if pytest_probe["exit_code"] == 0 else "structured_blocker"},
                    {**venv_probe, "command_id": "venv_create", "status": "accepted" if venv_probe["exit_code"] == 0 else "structured_blocker"},
                    {**focused, "command_id": "focused_regression", "status": "accepted" if focused["exit_code"] == 0 else "structured_blocker"},
                ],
                "summary": status_summary([{"status": "accepted" if pytest_probe["exit_code"] == 0 else "structured_blocker"}, {"status": "accepted" if venv_probe["exit_code"] == 0 else "structured_blocker"}, {"status": "accepted" if focused["exit_code"] == 0 else "structured_blocker"}]),
            }
        )
        regression = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.91",
            artifact_type="focused_regression_result",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=["command://focused_regression"],
            unresolved=unresolved,
            status="accepted" if focused["exit_code"] == 0 else "structured_blocker",
        )
        regression.update({"command": focused["command"], "exit_code": focused["exit_code"], "status": "accepted" if focused["exit_code"] == 0 else "structured_blocker"})
        checklist = _checklist(diagnosis)
        apply_redaction_guard(diagnosis, regression, checklist)
        write_runtime_restore(self.workspace, codebase_id, diagnosis, checklist, regression)
        return self.read_runtime_restore(codebase_id)

    def read_runtime_restore(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = runtime_restore_artifact_refs(codebase_id)
        diagnosis = read_runtime_diagnosis(self.workspace, codebase_id)
        checklist = read_restore_checklist(self.workspace, codebase_id)
        regression = read_focused_regression_result(self.workspace, codebase_id)
        return {
            "schema_version": "v2.91-95",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.91",
            "artifact_type": "restoreable_acceptance_runtime",
            "status": str(diagnosis.get("status") or "structured_blocker"),
            "data": {"runtime_diagnosis": diagnosis, "restore_checklist": checklist, "focused_regression_result": regression},
            "summary": dict(diagnosis.get("summary") or {}),
            "artifact_refs": refs,
            "evidence_refs": list(diagnosis.get("evidence_refs") or []),
            "warnings": list(diagnosis.get("warnings") or []),
            "unresolved": list(diagnosis.get("unresolved") or []),
            "next_actions": ["knowledge_code_real_acceptance_closure_runtime_restore_read"],
        }


def _python_command(state: dict[str, Any]) -> str:
    configured = str(state.get("python_command") or "").strip()
    if configured:
        return configured
    if shutil.which("python"):
        return "python"
    return sys.executable if sys.executable else "python3"


def _run_command(command: str, *, timeout: int, display_command: str | None = None) -> dict[str, Any]:
    try:
        result = subprocess.run(command, shell=True, cwd=Path.cwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=timeout)
        return {"command": display_command or command, "exit_code": int(result.returncode)}
    except subprocess.TimeoutExpired:
        return {"command": display_command or command, "exit_code": 124}
    except OSError:
        return {"command": display_command or command, "exit_code": 127}


def _probe_venv_create(python_command: str, *, timeout: int) -> dict[str, Any]:
    try:
        with tempfile.TemporaryDirectory(prefix="v291-venv-probe-") as probe_dir:
            command = f"{python_command} -m venv {probe_dir}"
            return _run_command(command, timeout=timeout, display_command="python -m venv <temporary_acceptance_runtime>")
    except OSError:
        return {"command": "python -m venv <temporary_acceptance_runtime>", "exit_code": 127}


def _skipped_command(command: str) -> dict[str, Any]:
    return {"command": command, "exit_code": 125}


def _legacy_venv_status(path: Path) -> str:
    python = path / "bin" / "python"
    if not python.exists():
        return "not_found"
    try:
        result = subprocess.run([str(python), "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10)
        return "usable" if result.returncode == 0 and "Python" in (result.stdout + result.stderr) else "broken"
    except (OSError, subprocess.TimeoutExpired):
        return "broken"


def _checklist(diagnosis: dict[str, Any]) -> str:
    runtime = diagnosis.get("python_runtime") or {}
    lines = ["# V2.91 Restore Checklist", "", f"Status: {diagnosis.get('status')}", ""]
    if not runtime.get("pytest_available"):
        lines.append("- Install test dependencies: `python -m pip install -r backend/requirements.txt -r backend/requirements-test.txt`.")
    if not runtime.get("venv_create_available"):
        lines.append("- Install or enable Python venv support for the selected interpreter.")
    if runtime.get("legacy_venv_status") != "usable":
        lines.append("- Do not rely on migrated `backend/.venv`; create an isolated acceptance runtime.")
    lines.append("- Rerun focused regression before declaring V2.91 accepted.")
    return "\n".join(lines)


def public_runtime_restore_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)
