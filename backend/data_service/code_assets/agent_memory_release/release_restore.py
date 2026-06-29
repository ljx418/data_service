"""Release and restore packaging artifacts for V2.75."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..external_e2e_portal_delivery.persistence import read_delivery_review_manifest, read_surface_baseline_version
from ..human_agent_deepening.persistence import read_restore_checklist
from ..registry import CodebaseRegistry
from .persistence import (
    read_acceptance_state,
    read_mcp_config_template,
    read_release_manifest,
    read_release_readiness_report,
    read_restore_runbook,
    read_smoke_commands,
    release_restore_artifact_refs,
    write_release_restore,
)
from .shared import base_artifact, redaction_findings, worst_status


PHASE = "V2.75"


class ReleaseRestoreService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_release_restore(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = release_restore_artifact_refs(codebase_id)
        sources = {
            "delivery": _try_read(lambda: read_delivery_review_manifest(self.workspace, codebase_id)),
            "restore": _try_text(lambda: read_restore_checklist(self.workspace, codebase_id)),
            "surface": _try_read(lambda: read_surface_baseline_version(self.workspace, codebase_id)),
            "memory": _try_read(lambda: read_acceptance_state(self.workspace, codebase_id)),
        }
        evidence_refs = _evidence_refs(sources)
        manifest = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="release_manifest", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs, next_actions=["knowledge_code_agent_memory_release_release_restore_read"])
        manifest["items"] = _manifest_items(sources)
        manifest["readiness_status"] = worst_status([item["status"] for item in manifest["items"]])
        mcp_config = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="mcp_config_template", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs)
        mcp_config["config"] = {"command": "python", "args": ["-m", "data_service", "mcp"], "env": {"DATA_SERVICE_WORKSPACE_ROOT": "<workspace-root>"}}
        smoke = _smoke_commands(codebase_id)
        runbook = _restore_runbook(manifest)
        report = _release_report(manifest)
        unresolved = redaction_findings(manifest) + redaction_findings(mcp_config) + redaction_findings(smoke) + redaction_findings(runbook) + redaction_findings(report)
        manifest["redaction_status"] = "accepted" if not unresolved else "structured_blocker"
        if unresolved:
            manifest["unresolved"].extend(unresolved)
            manifest["readiness_status"] = "structured_blocker"
        write_release_restore(self.workspace, codebase_id, manifest, mcp_config, smoke, runbook, report)
        return _bundle(self.workspace_id, codebase_id, manifest, mcp_config, smoke, runbook, report, refs)

    def read_release_restore(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = release_restore_artifact_refs(codebase_id)
        return _bundle(self.workspace_id, codebase_id, read_release_manifest(self.workspace, codebase_id), read_mcp_config_template(self.workspace, codebase_id), read_smoke_commands(self.workspace, codebase_id), read_restore_runbook(self.workspace, codebase_id), read_release_readiness_report(self.workspace, codebase_id), refs)


def public_release_restore_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "release_restore_packaging",
        "release_manifest": payload.get("release_manifest") or {},
        "mcp_config_template": payload.get("mcp_config_template") or {},
        "smoke_commands": {"format": "markdown", "content": payload.get("smoke_commands") or ""},
        "restore_runbook": {"format": "markdown", "content": payload.get("restore_runbook") or ""},
        "release_readiness_report": {"format": "markdown", "content": payload.get("release_readiness_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _try_read(reader) -> dict[str, Any]:
    try:
        return reader()
    except FileNotFoundError:
        return {}


def _try_text(reader) -> str:
    try:
        return reader()
    except FileNotFoundError:
        return ""


def _evidence_refs(sources: dict[str, Any]) -> list[Any]:
    refs: list[Any] = []
    for source in sources.values():
        if isinstance(source, dict):
            refs.extend(source.get("artifact_refs") or [])
            refs.extend(source.get("evidence_refs") or [])
    return refs


def _source_status(source: Any) -> str:
    if not source:
        return "needs_review"
    if isinstance(source, str):
        return "accepted"
    if source.get("readiness_status"):
        return str(source["readiness_status"])
    if source.get("overall_status"):
        return str(source["overall_status"])
    if source.get("exit_gate", {}).get("status"):
        return str(source["exit_gate"]["status"])
    return "accepted" if source else "needs_review"


def _manifest_items(sources: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {"release_item": name, "classification": "generated_evidence", "artifact_ref": _artifact_ref(source), "status": _source_status(source), "safe_to_delete": False, "next_action": "review source artifact" if _source_status(source) != "accepted" else "none"}
        for name, source in sources.items()
    ]


def _artifact_ref(source: Any) -> str:
    if isinstance(source, dict) and source.get("artifact_refs"):
        first = source["artifact_refs"][0]
        return str(first.get("artifact_ref") if isinstance(first, dict) else first)
    return "agent_memory_release://missing/source"


def _smoke_commands(codebase_id: str) -> str:
    return "\n".join([
        "# V2.75 Smoke Commands",
        "",
        "```text",
        f"python -m data_service code agent-memory-release release-restore-read --workspace-id <workspace-id> --codebase-id {codebase_id}",
        f"python -m data_service code agent-memory-release memory-read --workspace-id <workspace-id> --codebase-id {codebase_id}",
        "curl -s http://127.0.0.1:8000/api/workspaces/<workspace-id>/codebases/<codebase-id>/agent-memory-release/release-restore",
        "pytest -q backend/tests/test_v2_75_release_restore_packaging.py backend/tests/test_public_surface_guard.py",
        "```",
    ]) + "\n"


def _restore_runbook(manifest: dict[str, Any]) -> str:
    return "\n".join([
        "# V2.75 Restore Runbook",
        "",
        "1. Configure DATA_SERVICE_WORKSPACE_ROOT for the managed workspace.",
        "2. Import or locate the target codebase.",
        "3. Build V2.71-V2.75 artifacts in phase order.",
        "4. Run smoke commands.",
        f"5. Review readiness status: {manifest.get('readiness_status')}.",
    ]) + "\n"


def _release_report(manifest: dict[str, Any]) -> str:
    lines = ["# V2.75 Release Readiness Report", "", f"Readiness status: {manifest.get('readiness_status')}", f"Redaction status: {manifest.get('redaction_status', 'pending')}", "", "Unavailable or review states are not accepted."]
    return "\n".join(lines) + "\n"


def _bundle(workspace_id: str, codebase_id: str, manifest: dict[str, Any], mcp_config: dict[str, Any], smoke: str, runbook: str, report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.71-75",
        "artifact_type": "release_restore_packaging",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "release_manifest": manifest,
        "mcp_config_template": mcp_config,
        "smoke_commands": smoke,
        "restore_runbook": runbook,
        "release_readiness_report": report,
        "summary": {"readiness_status": manifest.get("readiness_status"), "redaction_status": manifest.get("redaction_status")},
        "artifact_refs": refs,
        "warnings": list(manifest.get("warnings") or []),
        "unresolved": list(manifest.get("unresolved") or []),
        "next_actions": ["knowledge_code_agent_memory_release_release_restore_read"],
    }

