"""V2.100 automated release evidence gate service."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from data_service.mcp_common import now

from ..real_acceptance_closure.persistence import read_final_gate_summary as read_v95_final_gate_summary
from ..registry import CodebaseRegistry
from .persistence import (
    read_cli_gap,
    read_evidence_summary,
    read_final_release_gate,
    read_false_green_recheck,
    read_material_scan,
    read_project_paths,
    read_risk_queue,
    release_gate_artifact_refs,
    write_release_gate,
)
from .shared import apply_redaction_guard, base_artifact, public_payload, status_summary, unresolved_item, worst_status


class AutomatedReleaseEvidenceGate:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_release_gate(self, codebase_id: str, gate_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        state = gate_state or {}
        generated_at = now()
        refs = release_gate_artifact_refs(codebase_id)
        checks = [
            _artifact_status("cli_gap", lambda: read_cli_gap(self.workspace, codebase_id), "needs_review"),
            _artifact_status("route_a_evidence", lambda: read_material_scan(self.workspace, codebase_id), "needs_review"),
            _artifact_status("quality_workbench", lambda: read_risk_queue(self.workspace, codebase_id), "needs_review"),
            _artifact_status("external_path_registry", lambda: read_project_paths(self.workspace, codebase_id), "structured_unavailable"),
            _artifact_status("v95_release_finalizer", lambda: read_v95_final_gate_summary(self.workspace, codebase_id), "needs_review"),
            _state_status("dependency_hygiene", state.get("dependency_hygiene_state"), required_evidence=True),
            _state_status("restore_smoke", state.get("restore_smoke_state"), required_evidence=True),
            _state_status("prd_spec_review", state.get("prd_spec_review_state"), required_evidence=True),
            _state_status("human_approval", state.get("human_approval_state"), required_evidence=True),
        ]
        final_status = "accepted" if all(check["status"] == "accepted" for check in checks) else worst_status([check["status"] for check in checks])
        unresolved = [item for check in checks for item in check.get("unresolved") or []]
        evidence_refs = [ref for check in checks for ref in check.get("evidence_refs") or []]
        summary = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase="V2.100", artifact_type="release_evidence_summary", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs, unresolved=unresolved, status=final_status, next_actions=["knowledge_code_automated_evidence_closure_release_gate_read"])
        summary.update({"final_release_status": final_status, "data": {"checks": checks}, "checks": checks, "false_green_recheck": {"passed": final_status == "accepted" or bool(unresolved), "rejected_claims": _rejected_claims(checks)}, "summary": status_summary(checks)})
        gate = _gate(summary)
        false_green = _false_green(summary)
        apply_redaction_guard(summary, gate, false_green)
        write_release_gate(self.workspace, codebase_id, summary, gate, false_green)
        return self.read_release_gate(codebase_id)

    def read_release_gate(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        summary = read_evidence_summary(self.workspace, codebase_id)
        gate = read_final_release_gate(self.workspace, codebase_id)
        false_green = read_false_green_recheck(self.workspace, codebase_id)
        return {
            "schema_version": "v2.96-100",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.100",
            "artifact_type": "release_evidence_gate",
            "status": str(summary.get("final_release_status") or summary.get("status") or "needs_review"),
            "data": {"evidence_summary": summary, "final_release_gate": gate, "false_green_recheck": false_green},
            "summary": dict(summary.get("summary") or {}),
            "artifact_refs": release_gate_artifact_refs(codebase_id),
            "evidence_refs": list(summary.get("evidence_refs") or []),
            "warnings": list(summary.get("warnings") or []),
            "unresolved": list(summary.get("unresolved") or []),
            "next_actions": ["knowledge_code_automated_evidence_closure_release_gate_read"],
        }


def _artifact_status(check_id: str, reader: Callable[[], dict[str, Any]], missing: str) -> dict[str, Any]:
    try:
        payload = reader()
        status = str(payload.get("final_release_status") or payload.get("status") or "needs_review")
        return {"id": check_id, "status": status, "evidence_refs": list(payload.get("evidence_refs") or []), "unresolved": list(payload.get("unresolved") or [])}
    except FileNotFoundError:
        return {"id": check_id, "status": missing, "evidence_refs": [], "unresolved": [unresolved_item(missing, f"{check_id} artifact is missing", item_id=check_id, next_action=f"build {check_id} artifact")]}


def _state_status(check_id: str, state: Any, *, required_evidence: bool) -> dict[str, Any]:
    body = state if isinstance(state, dict) else {}
    status = str(body.get("status") or "needs_review")
    evidence_refs = list(body.get("evidence_refs") or [])
    if status == "accepted" and required_evidence and not evidence_refs:
        status = "needs_review"
    if status not in {"accepted", "needs_review", "structured_unavailable", "structured_blocker", "failed"}:
        status = "needs_review"
    unresolved = []
    if status != "accepted":
        kind = "needs_review" if status == "needs_review" else status
        unresolved.append(unresolved_item(kind, f"{check_id} is not accepted", item_id=check_id, evidence_refs=evidence_refs, next_action=f"provide {check_id} evidence"))
    return {"id": check_id, "status": status, "evidence_refs": evidence_refs, "unresolved": unresolved}


def _rejected_claims(checks: list[dict[str, Any]]) -> list[str]:
    return [f"{check['id']} is not accepted; final release accepted claim rejected" for check in checks if check.get("status") != "accepted"]


def _gate(summary: dict[str, Any]) -> str:
    lines = ["# V2.100 Automated Release Evidence Gate", "", f"Final status: {summary.get('final_release_status')}", ""]
    for check in summary.get("checks") or []:
        lines.append(f"- {check['id']}: {check['status']}")
    lines.extend(["", "Final release accepted requires CLI gap, Route A, quality workbench, external project governance, V2.95 release closure, dependency hygiene, restore smoke, PRD/spec review, and human approval to be accepted."])
    return "\n".join(lines)


def _false_green(summary: dict[str, Any]) -> str:
    lines = ["# V2.100 False-green Recheck", "", f"Passed: {summary.get('false_green_recheck', {}).get('passed')}", ""]
    for claim in summary.get("false_green_recheck", {}).get("rejected_claims") or []:
        lines.append(f"- {claim}")
    return "\n".join(lines)


def public_release_gate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)
