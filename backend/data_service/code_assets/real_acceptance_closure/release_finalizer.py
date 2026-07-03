"""V2.95 final release gate closure service."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from data_service.mcp_common import now

from ..real_document_acceptance.persistence import read_import_run
from ..real_document_full_corpus_release.persistence import read_full_corpus_run
from ..registry import CodebaseRegistry
from .persistence import (
    read_e2e_result_matrix,
    read_final_gate_summary,
    read_final_release_report,
    read_false_green_audit,
    read_material_manifest,
    read_rule_effect_closure,
    read_runtime_diagnosis,
    release_finalizer_artifact_refs,
    write_release_finalizer,
)
from .shared import apply_redaction_guard, base_artifact, public_payload, status_summary, unresolved_item, worst_status


class FinalReleaseGateFinalizer:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_release_finalizer(self, codebase_id: str, gate_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        state = gate_state or {}
        generated_at = now()
        refs = release_finalizer_artifact_refs(codebase_id)
        checks = [
            _artifact_status("runtime", lambda: read_runtime_diagnosis(self.workspace, codebase_id), "structured_blocker"),
            _artifact_status("route_a", lambda: read_material_manifest(self.workspace, codebase_id), "needs_review"),
            _artifact_status("route_b", lambda: read_import_run(self.workspace, codebase_id), "needs_review"),
            _artifact_status("full_corpus", lambda: read_full_corpus_run(self.workspace, codebase_id), "needs_review"),
            _artifact_status("quality", lambda: read_rule_effect_closure(self.workspace, codebase_id), "needs_review"),
            _artifact_status("external_project", lambda: read_e2e_result_matrix(self.workspace, codebase_id), "structured_unavailable"),
            _state_status("dependency_hygiene", state.get("dependency_hygiene_state"), required_evidence=False),
            _state_status("restore_smoke", state.get("restore_smoke_state"), required_evidence=False),
            _state_status("public_surface", state.get("public_surface_state"), required_evidence=False),
            _state_status("protected_legacy_diff", state.get("protected_legacy_diff_state"), required_evidence=False),
            _state_status("prd_spec_review", state.get("prd_spec_review_state"), required_evidence=True),
            _state_status("human_approval", state.get("human_approval_state"), required_evidence=True),
        ]
        final_status = "accepted" if all(check["status"] == "accepted" for check in checks) else worst_status([check["status"] for check in checks])
        unresolved = [item for check in checks for item in check.get("unresolved") or []]
        summary = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.95",
            artifact_type="final_gate_summary",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[ref for check in checks for ref in check.get("evidence_refs") or []],
            unresolved=unresolved,
            status=final_status,
            next_actions=["knowledge_code_real_acceptance_closure_release_finalizer_read"],
        )
        summary.update(
            {
                "final_release_status": final_status,
                "checks": checks,
                "false_green_audit": {
                    "passed": final_status == "accepted" or all(check["status"] != "accepted" for check in checks if check["id"] in {"route_a", "quality", "external_project", "human_approval"}),
                    "rejected_claims": _rejected_claims(checks),
                },
                "summary": status_summary(checks),
            }
        )
        report = _report(summary)
        false_green = _false_green(summary)
        apply_redaction_guard(summary, report, false_green)
        write_release_finalizer(self.workspace, codebase_id, summary, report, false_green)
        return self.read_release_finalizer(codebase_id)

    def read_release_finalizer(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = release_finalizer_artifact_refs(codebase_id)
        summary = read_final_gate_summary(self.workspace, codebase_id)
        report = read_final_release_report(self.workspace, codebase_id)
        false_green = read_false_green_audit(self.workspace, codebase_id)
        return {
            "schema_version": "v2.91-95",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.95",
            "artifact_type": "final_release_gate_closure",
            "status": str(summary.get("final_release_status") or summary.get("status") or "needs_review"),
            "data": {"final_gate_summary": summary, "final_release_report": report, "false_green_audit": false_green},
            "summary": dict(summary.get("summary") or {}),
            "artifact_refs": refs,
            "evidence_refs": list(summary.get("evidence_refs") or []),
            "warnings": [],
            "unresolved": list(summary.get("unresolved") or []),
            "next_actions": ["knowledge_code_real_acceptance_closure_release_finalizer_read"],
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
        unresolved.append(unresolved_item("needs_review" if status == "needs_review" else status, f"{check_id} is not accepted", item_id=check_id, evidence_refs=evidence_refs, next_action=f"provide {check_id} evidence"))
    return {"id": check_id, "status": status, "evidence_refs": evidence_refs, "unresolved": unresolved}


def _rejected_claims(checks: list[dict[str, Any]]) -> list[str]:
    claims = []
    for check in checks:
        if check["status"] != "accepted":
            claims.append(f"{check['id']} is not accepted; final release accepted claim rejected")
    return claims


def _report(summary: dict[str, Any]) -> str:
    lines = ["# V2.95 Final Release Report", "", f"Final status: {summary.get('final_release_status')}", ""]
    for check in summary.get("checks") or []:
        lines.append(f"- {check['id']}: {check['status']}")
    lines.extend(["", "Final release accepted requires runtime, Route A, Route B, Full Corpus, quality, external project, dependency hygiene, restore smoke, public surface, protected legacy diff, PRD/spec review, and human approval to be accepted."])
    return "\n".join(lines)


def _false_green(summary: dict[str, Any]) -> str:
    lines = ["# V2.95 False-green Audit", "", f"Passed: {summary.get('false_green_audit', {}).get('passed')}", ""]
    for claim in summary.get("false_green_audit", {}).get("rejected_claims") or []:
        lines.append(f"- {claim}")
    return "\n".join(lines)


def public_release_finalizer_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)
