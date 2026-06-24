"""Developer onboarding and restore UX for V2.58."""

from __future__ import annotations

import platform
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    read_onboarding_report,
    read_restore_checklist,
    read_troubleshooting,
    restore_ux_artifact_refs,
    write_restore_ux,
)
from .shared import base_artifact, redaction_findings, structured_unavailable


PHASE = "V2.58"
CANONICAL_RUNNER = "PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py"
FOCUSED_STAGE_COMMAND = "PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_54_human_portal_deepening.py backend/tests/test_v2_55_agent_task_workflow.py backend/tests/test_v2_56_doc_code_evidence_loop.py backend/tests/test_v2_57_multi_project_regression.py backend/tests/test_v2_58_restore_ux.py backend/tests/test_public_surface_guard.py"
FAILURE_CATEGORIES = ["dependency_drift", "sandbox_limit", "artifact_missing", "public_surface_drift", "real_regression", "needs_review"]


class RestoreUXService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_restore_ux(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = restore_ux_artifact_refs(codebase_id)
        sources, warnings, unresolved = _source_status()
        checklist = _restore_checklist()
        troubleshooting = _troubleshooting()
        report = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="restore_onboarding_report",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=sources,
            warnings=warnings,
            unresolved=unresolved,
        )
        report.update(
            {
                "environment_summary": {
                    "python": platform.python_version(),
                    "platform": platform.system(),
                    "machine": platform.machine(),
                    "paths_redacted": True,
                },
                "dependency_baseline": {
                    "requirements_ref": "backend/requirements-test.txt",
                    "test_dependency_target": ".tmp/pytest-deps",
                },
                "acceptance_commands": [
                    CANONICAL_RUNNER,
                    FOCUSED_STAGE_COMMAND,
                    "PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend",
                    "git diff --check",
                ],
                "failure_diagnosis": [{"category": item, "section_ref": f"troubleshooting#{item}"} for item in FAILURE_CATEGORIES],
                "known_limitations": [
                    "FastAPI TestClient focused tests may need to run outside the restricted sandbox when local app transport hangs.",
                    "HarnessOS and Navia full artifact preparation can be recorded as structured_unavailable when bounded E2E time budget is exceeded.",
                ],
                "path_redaction_passed": True,
                "summary": {
                    "failure_category_count": len(FAILURE_CATEGORIES),
                    "acceptance_command_count": 4,
                    "canonical_runner_present": True,
                },
            }
        )
        redaction = redaction_findings(report) + redaction_findings(checklist) + redaction_findings(troubleshooting)
        if redaction:
            report["path_redaction_passed"] = False
            report["unresolved"].extend(redaction)
        write_restore_ux(self.workspace, codebase_id, checklist, troubleshooting, report)
        return _bundle(self.workspace_id, codebase_id, checklist, troubleshooting, report, refs)

    def read_restore_ux(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = restore_ux_artifact_refs(codebase_id)
        checklist = read_restore_checklist(self.workspace, codebase_id)
        troubleshooting = read_troubleshooting(self.workspace, codebase_id)
        report = read_onboarding_report(self.workspace, codebase_id)
        return _bundle(self.workspace_id, codebase_id, checklist, troubleshooting, report, refs)


def public_restore_ux_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "restore_ux",
        "restore_checklist": {"format": "markdown", "content": payload.get("restore_checklist") or ""},
        "troubleshooting": {"format": "markdown", "content": payload.get("troubleshooting") or ""},
        "onboarding_report": payload.get("onboarding_report") or {},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _bundle(workspace_id: str, codebase_id: str, checklist: str, troubleshooting: str, report: dict[str, Any], refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.54-58",
        "artifact_type": "restore_ux",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "restore_checklist": checklist,
        "troubleshooting": troubleshooting,
        "onboarding_report": report,
        "summary": dict(report.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(report.get("warnings") or []),
        "unresolved": list(report.get("unresolved") or []),
        "next_actions": ["knowledge_code_human_agent_deepening_restore_read"],
    }


def _source_status() -> tuple[list[dict[str, str]], list[str], list[dict[str, Any]]]:
    sources = []
    warnings = []
    unresolved = []
    for ref in [
        "backend/scripts/v2_53_acceptance.py",
        "backend/requirements-test.txt",
        "docs/V2.x/V2_46_52_CODEX_HANDOFF_AND_RESTORE_GUIDE.md",
        "docs/V2.x/V2_54_58_HUMAN_AGENT_DEEPENING_FULL_COVERAGE_MATRIX.md",
    ]:
        if Path(ref).exists():
            sources.append({"type": "restore_source", "artifact_ref": ref})
        else:
            unresolved.append(structured_unavailable(ref, "restore source file is not available"))
    if unresolved:
        warnings.append("RESTORE_UX_SOURCE_PARTIAL")
    return sources, warnings, unresolved


def _restore_checklist() -> str:
    return "\n".join(
        [
            "# Restore Checklist",
            "",
            "1. Install or reuse the test dependency baseline from `backend/requirements-test.txt` into `.tmp/pytest-deps`.",
            f"2. Run canonical accepted baseline: `{CANONICAL_RUNNER}`.",
            f"3. Run V2.54-V2.58 focused stage checks: `{FOCUSED_STAGE_COMMAND}`.",
            "4. Run `PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend`.",
            "5. Run `git diff --check`.",
            "6. If a FastAPI TestClient focused test hangs in the restricted sandbox, rerun the same command outside the restricted sandbox and record the limitation.",
            "",
        ]
    )


def _troubleshooting() -> str:
    sections = {
        "dependency_drift": "Reinstall test dependencies into `.tmp/pytest-deps` from `backend/requirements-test.txt` and rerun the exact failed command.",
        "sandbox_limit": "If TestClient local transport hangs only in the restricted sandbox, rerun the same focused test outside the restricted sandbox and record the sandbox limitation.",
        "artifact_missing": "Rebuild the relevant phase artifact before marking any matrix row accepted.",
        "public_surface_drift": "Update public surface guard only when the new MCP, CLI, or HTTP surface is intentional and documented.",
        "real_regression": "Treat repeatable focused test failure as implementation regression and return to development before acceptance.",
        "needs_review": "Keep uncertain evidence as needs_review until a focused test, real E2E result, or structured unavailable rationale exists.",
    }
    lines = ["# Troubleshooting", ""]
    for key, text in sections.items():
        lines.extend([f"## {key}", "", text, ""])
    return "\n".join(lines)
