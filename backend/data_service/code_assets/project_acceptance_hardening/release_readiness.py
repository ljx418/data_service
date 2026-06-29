"""Release readiness closure artifacts for V2.80."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..agent_memory_release.persistence import read_release_manifest, read_smoke_commands
from ..registry import CodebaseRegistry
from .persistence import (
    read_console_product_report,
    read_e2e_rerun_records,
    read_handoff_package_manifest,
    read_readiness_gate,
    read_release_closure_report,
    read_release_warning_gate,
    read_restore_verification,
    read_smoke_run_records,
    release_readiness_artifact_refs,
    write_release_readiness,
)
from .shared import base_artifact, redaction_findings, unresolved_item, worst_status


PHASE = "V2.80"


class ReleaseReadinessClosureService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_release_readiness(self, codebase_id: str, approval_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = release_readiness_artifact_refs(codebase_id)
        restore = _restore_verification(self.workspace, codebase_id, self.workspace_id, generated_at, refs)
        smoke = _smoke_records(self.workspace, codebase_id, self.workspace_id, generated_at, refs)
        manifest = _handoff_manifest(self.workspace, codebase_id, self.workspace_id, generated_at, refs)
        checks = _checks(self.workspace, codebase_id, restore, smoke, manifest, approval_state or {})
        gate_status = worst_status([check["status"] for check in checks])
        gate = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="release_readiness_gate", generated_at=generated_at, artifact_refs=refs, evidence_refs=_evidence_refs(checks), next_actions=["knowledge_code_project_acceptance_hardening_release_readiness_read"])
        gate["checks"] = checks
        gate["status"] = gate_status
        gate["readiness_status"] = gate_status
        gate["next_action"] = "none" if gate_status == "accepted" else "resolve non-accepted release readiness checks"
        gate["unresolved"].extend([item for check in checks for item in check.get("unresolved") or []])
        report = _report(gate)
        unresolved = redaction_findings(gate) + redaction_findings(restore) + redaction_findings(smoke) + redaction_findings(manifest) + redaction_findings(report)
        if unresolved:
            gate["unresolved"].extend(unresolved)
            gate["status"] = "structured_blocker"
            gate["readiness_status"] = "structured_blocker"
        write_release_readiness(self.workspace, codebase_id, gate, restore, smoke, manifest, report)
        return _bundle(self.workspace_id, codebase_id, gate, restore, smoke, manifest, report, refs)

    def read_release_readiness(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = release_readiness_artifact_refs(codebase_id)
        return _bundle(self.workspace_id, codebase_id, read_readiness_gate(self.workspace, codebase_id), read_restore_verification(self.workspace, codebase_id), read_smoke_run_records(self.workspace, codebase_id), read_handoff_package_manifest(self.workspace, codebase_id), read_release_closure_report(self.workspace, codebase_id), refs)


def public_release_readiness_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "release_readiness_closure",
        "readiness_gate": payload.get("readiness_gate") or {},
        "restore_verification": payload.get("restore_verification") or {},
        "smoke_run_records": payload.get("smoke_run_records") or {},
        "handoff_package_manifest": payload.get("handoff_package_manifest") or {},
        "release_closure_report": {"format": "markdown", "content": payload.get("release_closure_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _restore_verification(workspace: Path, codebase_id: str, workspace_id: str, generated_at: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    restore = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="restore_verification", generated_at=generated_at, artifact_refs=refs, evidence_refs=[])
    try:
        manifest = read_release_manifest(workspace, codebase_id)
        restore["status"] = str(manifest.get("redaction_status") or "needs_review")
        restore["evidence_refs"] = list(manifest.get("artifact_refs") or ["agent_memory_release://release_restore/release_manifest.json"])
    except FileNotFoundError:
        restore["status"] = "needs_review"
        restore["unresolved"].append(unresolved_item("needs_review", "release restore manifest is not built", item_id="restore_manifest", next_action="build V2.75 release restore"))
    return restore


def _smoke_records(workspace: Path, codebase_id: str, workspace_id: str, generated_at: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    smoke = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="smoke_run_records", generated_at=generated_at, artifact_refs=refs, evidence_refs=[])
    try:
        commands = read_smoke_commands(workspace, codebase_id)
        smoke["status"] = "accepted" if "pytest -q" in commands and "agent-memory-release" in commands else "needs_review"
        smoke["commands"] = commands
        smoke["evidence_refs"] = ["agent_memory_release://release_restore/smoke_commands.md"]
    except FileNotFoundError:
        smoke["status"] = "needs_review"
        smoke["commands"] = ""
        smoke["unresolved"].append(unresolved_item("needs_review", "smoke command record is missing", item_id="smoke_commands", next_action="build V2.75 release restore"))
    return smoke


def _handoff_manifest(workspace: Path, codebase_id: str, workspace_id: str, generated_at: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    manifest = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="handoff_package_manifest", generated_at=generated_at, artifact_refs=refs, evidence_refs=[])
    sources = [
        ("external_project_binding", lambda: read_e2e_rerun_records(workspace, codebase_id)),
        ("warning_gate", lambda: read_release_warning_gate(workspace, codebase_id)),
        ("console_product_report", lambda: read_console_product_report(workspace, codebase_id)),
    ]
    items: list[dict[str, Any]] = []
    for name, reader in sources:
        try:
            source = reader()
            items.append({"id": name, "status": _source_status(source), "evidence_refs": _source_evidence_refs(source), "unresolved": _source_unresolved(source)})
        except FileNotFoundError:
            items.append({"id": name, "status": "needs_review", "evidence_refs": [], "unresolved": [unresolved_item("needs_review", f"{name} source is missing", item_id=name, next_action="build prior phase artifact")]})
    manifest["items"] = items
    manifest["status"] = worst_status([item["status"] for item in items])
    manifest["evidence_refs"] = _evidence_refs(items)
    return manifest


def _checks(workspace: Path, codebase_id: str, restore: dict[str, Any], smoke: dict[str, Any], manifest: dict[str, Any], approval: dict[str, Any]) -> list[dict[str, Any]]:
    checks = [
        {"id": "restore_verification", "status": restore.get("status", "needs_review"), "evidence_refs": restore.get("evidence_refs") or [], "unresolved": restore.get("unresolved") or []},
        {"id": "smoke_commands", "status": smoke.get("status", "needs_review"), "evidence_refs": smoke.get("evidence_refs") or [], "unresolved": smoke.get("unresolved") or []},
        {"id": "handoff_manifest", "status": manifest.get("status", "needs_review"), "evidence_refs": manifest.get("evidence_refs") or [], "unresolved": manifest.get("unresolved") or []},
        _source_check(workspace, codebase_id, "warning_gate", read_release_warning_gate),
        _source_check(workspace, codebase_id, "external_project_rerun", read_e2e_rerun_records),
    ]
    if approval.get("status") == "accepted" and approval.get("evidence_refs"):
        checks.append({"id": "human_approval", "status": "accepted", "evidence_refs": list(approval.get("evidence_refs") or []), "unresolved": []})
    else:
        checks.append({"id": "human_approval", "status": "needs_review", "evidence_refs": [], "unresolved": [unresolved_item("needs_review", "high-risk release approval is not captured", item_id="human_approval", next_action="record human approval decision")]})
    return checks


def _source_check(workspace: Path, codebase_id: str, check_id: str, reader) -> dict[str, Any]:
    try:
        source = reader(workspace, codebase_id)
        return {"id": check_id, "status": _source_status(source), "evidence_refs": list(source.get("artifact_refs") or source.get("evidence_refs") or []), "unresolved": list(source.get("unresolved") or [])}
    except FileNotFoundError:
        return {"id": check_id, "status": "needs_review", "evidence_refs": [], "unresolved": [unresolved_item("needs_review", f"{check_id} source is missing", item_id=check_id, next_action="build prior phase artifact")]}


def _source_status(source: dict[str, Any] | str) -> str:
    if isinstance(source, str):
        return "accepted" if source else "needs_review"
    for key in ("status", "readiness_status", "stage_status", "overall_status"):
        if source.get(key):
            return str(source[key])
    if source.get("summary", {}).get("status"):
        return str(source["summary"]["status"])
    if source.get("summary", {}).get("structured_unavailable_count") or source.get("summary", {}).get("unavailable_accepted_count"):
        return "structured_unavailable" if source.get("summary", {}).get("structured_unavailable_count") else "needs_review"
    return "accepted"


def _source_evidence_refs(source: dict[str, Any] | str) -> list[Any]:
    if isinstance(source, str):
        return ["project_acceptance_hardening://console_productization/maintainer_console_product_report.md"] if source else []
    return list(source.get("artifact_refs") or source.get("evidence_refs") or [])


def _source_unresolved(source: dict[str, Any] | str) -> list[Any]:
    if isinstance(source, str):
        return []
    return list(source.get("unresolved") or [])


def _evidence_refs(items: list[dict[str, Any]]) -> list[Any]:
    refs: list[Any] = []
    for item in items:
        refs.extend(item.get("evidence_refs") or [])
    return refs


def _report(gate: dict[str, Any]) -> str:
    lines = ["# V2.80 Release Readiness Closure Report", "", f"Readiness status: {gate.get('readiness_status')}", ""]
    for check in gate.get("checks") or []:
        lines.append(f"- {check['id']}: {check['status']}")
    lines.append("")
    lines.append("Human approval and non-accepted states are preserved as release blockers.")
    return "\n".join(lines) + "\n"


def _bundle(workspace_id: str, codebase_id: str, gate: dict[str, Any], restore: dict[str, Any], smoke: dict[str, Any], manifest: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.76-80",
        "artifact_type": "release_readiness_closure",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "readiness_gate": gate,
        "restore_verification": restore,
        "smoke_run_records": smoke,
        "handoff_package_manifest": manifest,
        "release_closure_report": report,
        "summary": {"readiness_status": gate.get("readiness_status"), "check_count": len(gate.get("checks") or [])},
        "artifact_refs": refs,
        "warnings": list(gate.get("warnings") or []),
        "unresolved": list(gate.get("unresolved") or []),
        "next_actions": ["knowledge_code_project_acceptance_hardening_release_readiness_read"],
    }
