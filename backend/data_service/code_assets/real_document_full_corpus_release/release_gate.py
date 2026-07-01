"""V2.90 release gate and restore hygiene service."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..real_document_acceptance.persistence import read_import_run, read_release_closure_rerun
from ..registry import CodebaseRegistry
from .persistence import (
    read_full_corpus_run,
    read_human_quality_review,
    read_path_manifest,
    read_project_e2e_records,
    read_release_gate_summary,
    read_release_readiness_report,
    read_route_a_contract,
    release_gate_artifact_refs,
    write_release_gate,
)
from .shared import base_artifact, public_payload, redaction_findings, status_summary, unresolved_item, worst_status


class ReleaseGateRestoreHygieneService:
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
            _read_status("route_a", lambda: read_route_a_contract(self.workspace, codebase_id), missing="needs_review"),
            _read_status("route_b", lambda: read_import_run(self.workspace, codebase_id), missing="needs_review"),
            _read_status("full_corpus", lambda: read_full_corpus_run(self.workspace, codebase_id), missing="needs_review"),
            _read_status("quality_review", lambda: read_human_quality_review(self.workspace, codebase_id), missing="needs_review"),
            _read_status("external_project", lambda: read_project_e2e_records(self.workspace, codebase_id), missing="structured_unavailable"),
            _state_status("human_approval", state.get("human_approval_state"), required_evidence=True),
            _state_status("restore_smoke", state.get("restore_smoke_state"), required_evidence=False),
            _state_status("dependency_hygiene", state.get("dependency_hygiene_state"), required_evidence=False),
        ]
        final_status = "accepted" if all(check["status"] == "accepted" for check in checks) else worst_status([check["status"] for check in checks])
        unresolved = [item for check in checks for item in check.get("unresolved") or []]
        summary = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.90",
            artifact_type="release_gate_summary",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[ref for check in checks for ref in check.get("evidence_refs") or []],
            unresolved=unresolved,
            status=final_status,
            next_actions=["knowledge_code_real_document_full_corpus_release_release_gate_read"],
        )
        summary.update(
            {
                "route_a_status": _check_status(checks, "route_a"),
                "route_b_status": _check_status(checks, "route_b"),
                "full_corpus_status": _check_status(checks, "full_corpus"),
                "quality_review_status": _check_status(checks, "quality_review"),
                "external_project_status": _check_status(checks, "external_project"),
                "human_approval_status": _check_status(checks, "human_approval"),
                "restore_smoke_status": _check_status(checks, "restore_smoke"),
                "dependency_hygiene_status": _check_status(checks, "dependency_hygiene"),
                "final_release_status": final_status,
                "blocking_reasons": [item["reason"] for item in unresolved],
                "checks": checks,
                "summary": status_summary(checks),
            }
        )
        report = _report(summary)
        _apply_redaction(summary, report)
        write_release_gate(self.workspace, codebase_id, summary, report)
        return self.read_release_gate(codebase_id)

    def read_release_gate(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = release_gate_artifact_refs(codebase_id)
        summary = read_release_gate_summary(self.workspace, codebase_id)
        report = read_release_readiness_report(self.workspace, codebase_id)
        return {
            "schema_version": "v2.86-90",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.90",
            "artifact_type": "release_gate_restore_hygiene",
            "status": str(summary.get("status") or "needs_review"),
            "data": {"release_gate_summary": summary, "release_readiness_report": report},
            "summary": dict(summary.get("summary") or {}),
            "artifact_refs": refs,
            "evidence_refs": list(summary.get("evidence_refs") or []),
            "warnings": [],
            "unresolved": list(summary.get("unresolved") or []),
            "next_actions": ["knowledge_code_real_document_full_corpus_release_release_gate_read"],
        }


def _read_status(check_id: str, reader, *, missing: str) -> dict[str, Any]:
    try:
        payload = reader()
        status = str(payload.get("final_release_status") or payload.get("status") or payload.get("review_status") or "needs_review")
        return {"id": check_id, "status": status, "evidence_refs": list(payload.get("evidence_refs") or []), "unresolved": list(payload.get("unresolved") or [])}
    except FileNotFoundError:
        return {
            "id": check_id,
            "status": missing,
            "evidence_refs": [],
            "unresolved": [unresolved_item(missing, f"{check_id} artifact is missing", item_id=check_id, next_action=f"build {check_id} artifact")],
        }


def _state_status(check_id: str, state: Any, *, required_evidence: bool) -> dict[str, Any]:
    body = state if isinstance(state, dict) else {}
    evidence_refs = list(body.get("evidence_refs") or [])
    status = str(body.get("status") or "needs_review")
    if status == "accepted" and required_evidence and not evidence_refs:
        status = "needs_review"
    unresolved = []
    if status != "accepted":
        unresolved.append(unresolved_item("needs_review", f"{check_id} is not accepted", item_id=check_id, next_action=f"provide {check_id} evidence"))
    return {"id": check_id, "status": status if status in {"accepted", "needs_review", "structured_unavailable", "structured_blocker", "failed"} else "needs_review", "evidence_refs": evidence_refs, "unresolved": unresolved}


def _check_status(checks: list[dict[str, Any]], check_id: str) -> str:
    for check in checks:
        if check["id"] == check_id:
            return str(check["status"])
    return "needs_review"


def _report(summary: dict[str, Any]) -> str:
    lines = ["# V2.90 Release Readiness Report", "", f"Final status: {summary['final_release_status']}", ""]
    for check in summary["checks"]:
        lines.append(f"- {check['id']}: {check['status']}")
    lines.extend(["", "Final release accepted is blocked unless Route A, Route B, full corpus, quality review, external project closure, restore/smoke, dependency hygiene, and human approval are accepted."])
    return "\n".join(lines)


def _apply_redaction(*payloads: Any) -> None:
    findings: list[dict[str, Any]] = []
    for payload in payloads:
        findings.extend(redaction_findings(payload))
    for payload in payloads:
        if isinstance(payload, dict) and findings:
            payload.setdefault("unresolved", []).extend(findings)
            payload["status"] = "structured_blocker"
            payload["final_release_status"] = "structured_blocker"


def public_release_gate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)
