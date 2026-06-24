"""Acceptance artifact cleanup and packaging for V2.61."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import packaging_artifact_refs, read_cleanup_plan, read_handoff_checklist, read_package_audit_report, read_package_manifest, write_packaging
from .shared import base_artifact, redaction_findings


PHASE = "V2.61"
CANONICAL_RUNNER = "PYTHONPATH=.tmp/pytest-deps:backend python3 backend/scripts/v2_53_acceptance.py"
FOCUSED_COMMAND = "PYTHONPATH=.tmp/pytest-deps:backend python3 -m pytest -q backend/tests/test_v2_59_public_surface_stabilization.py backend/tests/test_v2_60_real_project_e2e_expansion.py backend/tests/test_v2_61_acceptance_packaging.py backend/tests/test_v2_62_portal_ux_integration.py backend/tests/test_public_surface_guard.py"


class AcceptancePackagingService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_package(self, codebase_id: str, repo_root: str | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = packaging_artifact_refs(codebase_id)
        root = Path(repo_root or ".")
        manifest = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="package_manifest", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
        manifest["entries"] = _manifest_entries(root)
        manifest["destructive_action_required"] = False
        manifest["summary"] = {
            "entry_count": len(manifest["entries"]),
            "local_tmp_count": sum(1 for item in manifest["entries"] if item["classification"] == "local_tmp"),
            "destructive_action_required": False,
        }
        cleanup = _cleanup_plan(manifest)
        handoff = _handoff_checklist()
        audit = _package_audit(manifest)
        unresolved = redaction_findings(manifest) + redaction_findings(cleanup) + redaction_findings(handoff) + redaction_findings(audit)
        if unresolved:
            manifest["unresolved"].extend(unresolved)
        write_packaging(self.workspace, codebase_id, manifest, cleanup, handoff, audit)
        return _bundle(self.workspace_id, codebase_id, manifest, cleanup, handoff, audit, refs)

    def read_package(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = packaging_artifact_refs(codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            read_package_manifest(self.workspace, codebase_id),
            read_cleanup_plan(self.workspace, codebase_id),
            read_handoff_checklist(self.workspace, codebase_id),
            read_package_audit_report(self.workspace, codebase_id),
            refs,
        )


def public_package_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "acceptance_packaging",
        "package_manifest": payload.get("package_manifest") or {},
        "cleanup_plan": {"format": "markdown", "content": payload.get("cleanup_plan") or ""},
        "handoff_checklist": {"format": "markdown", "content": payload.get("handoff_checklist") or ""},
        "package_audit_report": {"format": "markdown", "content": payload.get("package_audit_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _manifest_entries(root: Path) -> list[dict[str, str]]:
    candidates = [
        ("backend/data_service/code_assets/stabilization_e2e_portal", "source", "commit"),
        ("backend/data_service/mcp_code_stabilization_e2e_portal_tools.py", "source", "commit"),
        ("backend/data_service/cli_code_stabilization_e2e_portal.py", "source", "commit"),
        ("backend/app/api/v1/code_assets_stabilization_e2e_portal.py", "source", "commit"),
        ("backend/tests/test_v2_59_public_surface_stabilization.py", "test", "commit"),
        ("backend/tests/test_v2_60_real_project_e2e_expansion.py", "test", "commit"),
        ("backend/tests/test_v2_61_acceptance_packaging.py", "test", "commit"),
        ("backend/tests/test_v2_62_portal_ux_integration.py", "test", "commit"),
        ("backend/scripts", "script", "manual_review"),
        ("docs/V2.x", "doc", "manual_review"),
        (".tmp", "local_tmp", "do_not_delete"),
    ]
    entries = []
    for rel, classification, action in candidates:
        status = "present" if (root / rel).exists() else "missing"
        entries.append({"path": rel, "classification": classification, "recommended_action": action, "status": status})
    return entries


def _cleanup_plan(manifest: dict[str, Any]) -> str:
    lines = ["# Cleanup Plan", "", "This plan is advisory. It does not authorize deletion.", ""]
    for item in manifest.get("entries", []):
        lines.append(f"- `{item['path']}`: {item['classification']} -> {item['recommended_action']} ({item['status']})")
    return "\n".join(lines) + "\n"


def _handoff_checklist() -> str:
    return "\n".join(
        [
            "# Handoff Checklist",
            "",
            f"1. Run canonical baseline: `{CANONICAL_RUNNER}`.",
            f"2. Run V2.59-V2.62 focused checks: `{FOCUSED_COMMAND}`.",
            "3. Run `PYTHONPATH=.tmp/pytest-deps:backend python3 -m compileall -q backend`.",
            "4. Run `git diff --check`.",
            "5. Verify protected legacy diff is empty.",
            "",
        ]
    )


def _package_audit(manifest: dict[str, Any]) -> str:
    destructive = manifest.get("destructive_action_required") is True
    return "\n".join(
        [
            "# Package Audit Report",
            "",
            f"- destructive_action_required: {str(destructive).lower()}",
            f"- entry_count: {len(manifest.get('entries') or [])}",
            f"- local_tmp_count: {manifest.get('summary', {}).get('local_tmp_count', 0)}",
            "- verdict: pass for advisory packaging baseline",
            "",
        ]
    )


def _bundle(workspace_id: str, codebase_id: str, manifest: dict[str, Any], cleanup: str, handoff: str, audit: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.59-62",
        "artifact_type": "acceptance_packaging",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "package_manifest": manifest,
        "cleanup_plan": cleanup,
        "handoff_checklist": handoff,
        "package_audit_report": audit,
        "summary": dict(manifest.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(manifest.get("warnings") or []),
        "unresolved": list(manifest.get("unresolved") or []),
        "next_actions": ["knowledge_code_stabilization_package_read"],
    }
