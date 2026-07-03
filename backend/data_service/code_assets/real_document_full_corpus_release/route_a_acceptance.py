"""V2.87 Route A representative material acceptance service."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    read_route_a_contract,
    read_route_a_record,
    read_route_a_redaction,
    route_a_artifact_refs,
    write_route_a,
)
from .shared import base_artifact, public_payload, redaction_findings, status_summary, unresolved_item


class RouteAAcceptanceService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_route_a(self, codebase_id: str, acceptance_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        state = acceptance_state or {}
        refs = route_a_artifact_refs(codebase_id)
        generated_at = now()
        evidence_refs = list(state.get("evidence_refs") or [])
        has_material = bool(str(state.get("sample_pack_ref") or "").strip())
        review_accepted = state.get("manual_review_state") == "accepted" and bool(evidence_refs)
        status = "accepted" if has_material and review_accepted else "needs_review"
        unresolved = []
        if status != "accepted":
            unresolved.append(
                unresolved_item(
                    "needs_review",
                    "Route A user representative real materials or manual acceptance evidence are not complete",
                    item_id="route_a_materials",
                    next_action="provide representative materials, redaction review, screenshots or headless evidence, and reviewer decision",
                )
            )
        contract = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.87",
            artifact_type="route_a_sample_pack_contract",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=evidence_refs,
            unresolved=unresolved,
            status=status,
            next_actions=["knowledge_code_real_document_full_corpus_release_route_a_read"],
        )
        contract.update(
            {
                "source_type": state.get("source_type") or ("user_representative" if has_material else "structured_unavailable"),
                "route": "Route A",
                "sample_pack_ref": state.get("sample_pack_ref") or "",
                "redaction_policy_ref": state.get("redaction_policy_ref") or "",
                "acceptance_scope": state.get("acceptance_scope") or "Route A representative real-document UX acceptance",
                "manual_review_state": state.get("manual_review_state") or "needs_review",
                "status": status,
                "summary": status_summary([{"status": status}]),
            }
        )
        redaction = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.87",
            artifact_type="route_a_redaction_review",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=evidence_refs,
            unresolved=unresolved,
            status=status,
        )
        redaction.update(
            {
                "redaction_status": "accepted" if status == "accepted" else "needs_review",
                "policy_ref": contract["redaction_policy_ref"],
                "findings": [] if status == "accepted" else [{"status": "needs_review", "finding": "redaction policy and reviewer decision are required"}],
            }
        )
        record = _record(contract, redaction)
        _apply_redaction(contract, redaction, record)
        write_route_a(self.workspace, codebase_id, contract, redaction, record)
        return self.read_route_a(codebase_id)

    def read_route_a(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = route_a_artifact_refs(codebase_id)
        contract = read_route_a_contract(self.workspace, codebase_id)
        redaction = read_route_a_redaction(self.workspace, codebase_id)
        record = read_route_a_record(self.workspace, codebase_id)
        return {
            "schema_version": "v2.86-90",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.87",
            "artifact_type": "route_a_representative_acceptance",
            "status": str(contract.get("status") or "needs_review"),
            "data": {"sample_pack_contract": contract, "redaction_review": redaction, "manual_acceptance_record": record},
            "summary": dict(contract.get("summary") or {}),
            "artifact_refs": refs,
            "evidence_refs": list(contract.get("evidence_refs") or []),
            "warnings": [],
            "unresolved": list(contract.get("unresolved") or []),
            "next_actions": ["knowledge_code_real_document_full_corpus_release_route_a_read"],
        }


def _record(contract: dict[str, Any], redaction: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V2.87 Route A Manual Acceptance Record",
            "",
            f"Status: {contract['status']}",
            f"Source type: {contract['source_type']}",
            f"Sample pack: {contract['sample_pack_ref'] or 'needs_review'}",
            f"Redaction: {redaction['redaction_status']}",
            f"Manual review: {contract['manual_review_state']}",
            "",
            "Route A cannot be replaced by Route B, mock-only, sample-only, or path-only evidence.",
        ]
    )


def _apply_redaction(*payloads: Any) -> None:
    findings: list[dict[str, Any]] = []
    for payload in payloads:
        findings.extend(redaction_findings(payload))
    for payload in payloads:
        if isinstance(payload, dict) and findings:
            payload.setdefault("unresolved", []).extend(findings)
            payload["status"] = "structured_blocker"


def public_route_a_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)
