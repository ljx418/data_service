"""V2.92 Route A representative material closure service."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    read_manual_acceptance_record,
    read_material_manifest,
    read_redaction_decision,
    route_a_closure_artifact_refs,
    write_route_a_closure,
)
from .shared import apply_redaction_guard, base_artifact, public_payload, status_summary, unresolved_item


class RouteAMaterialIntakeReview:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_route_a_closure(self, codebase_id: str, material_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        state = material_state or {}
        generated_at = now()
        refs = route_a_closure_artifact_refs(codebase_id)
        materials = _materials(state)
        evidence_refs = list(state.get("evidence_refs") or [])
        redaction_state = dict(state.get("redaction") or {})
        manual = dict(state.get("manual_review") or {})
        redaction_status = str(redaction_state.get("status") or "needs_review")
        manual_decision = str(manual.get("decision") or "needs_review")
        accepted = bool(materials) and redaction_status == "accepted" and manual_decision == "accepted" and bool(evidence_refs)
        status = "accepted" if accepted else "needs_review"
        unresolved = []
        if not materials:
            unresolved.append(unresolved_item("needs_review", "Route A representative real materials are missing", item_id="route_a_materials", next_action="provide user representative real material refs or material directory"))
        if redaction_status != "accepted":
            unresolved.append(unresolved_item("needs_review", "Route A redaction review is not accepted", item_id="route_a_redaction", next_action="record redaction decision"))
        if manual_decision != "accepted" or not evidence_refs:
            unresolved.append(unresolved_item("needs_review", "Route A manual review or screenshot/headless evidence is missing", item_id="route_a_manual_review", next_action="record manual reviewer decision and evidence refs"))
        manifest = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.92",
            artifact_type="route_a_material_manifest",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=evidence_refs,
            unresolved=unresolved,
            status=status,
            next_actions=["knowledge_code_real_acceptance_closure_route_a_closure_read"],
        )
        manifest.update({"materials": materials, "manual_review": {"reviewer": str(manual.get("reviewer") or ""), "decision": manual_decision, "decision_at": str(manual.get("decision_at") or generated_at), "evidence_refs": evidence_refs}, "summary": status_summary([{"status": status}])})
        redaction = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.92",
            artifact_type="route_a_redaction_decision",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=evidence_refs,
            unresolved=unresolved,
            status=status,
        )
        redaction.update({"redaction_status": redaction_status, "policy_ref": str(redaction_state.get("policy_ref") or ""), "findings": list(redaction_state.get("findings") or ([] if redaction_status == "accepted" else [{"status": "needs_review", "finding": "redaction policy is required"}]))})
        record = _record(manifest, redaction)
        apply_redaction_guard(manifest, redaction, record)
        write_route_a_closure(self.workspace, codebase_id, manifest, redaction, record)
        return self.read_route_a_closure(codebase_id)

    def read_route_a_closure(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = route_a_closure_artifact_refs(codebase_id)
        manifest = read_material_manifest(self.workspace, codebase_id)
        redaction = read_redaction_decision(self.workspace, codebase_id)
        record = read_manual_acceptance_record(self.workspace, codebase_id)
        return {
            "schema_version": "v2.91-95",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.92",
            "artifact_type": "route_a_material_closure",
            "status": str(manifest.get("status") or "needs_review"),
            "data": {"material_manifest": manifest, "redaction_decision": redaction, "manual_acceptance_record": record},
            "summary": dict(manifest.get("summary") or {}),
            "artifact_refs": refs,
            "evidence_refs": list(manifest.get("evidence_refs") or []),
            "warnings": [],
            "unresolved": list(manifest.get("unresolved") or []),
            "next_actions": ["knowledge_code_real_acceptance_closure_route_a_closure_read"],
        }


def _materials(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(state.get("materials") or [], start=1):
        if not isinstance(item, dict):
            continue
        source_ref = str(item.get("source_ref") or "").strip()
        if not source_ref:
            continue
        rows.append({"material_id": str(item.get("material_id") or f"material_{idx}"), "source_type": str(item.get("source_type") or "document"), "source_ref": source_ref, "redaction_status": str(item.get("redaction_status") or "needs_review"), "evidence_refs": list(item.get("evidence_refs") or [])})
    return rows


def _record(manifest: dict[str, Any], redaction: dict[str, Any]) -> str:
    manual = manifest.get("manual_review") or {}
    return "\n".join(
        [
            "# V2.92 Route A Manual Acceptance Record",
            "",
            f"Status: {manifest.get('status')}",
            f"Material count: {len(manifest.get('materials') or [])}",
            f"Redaction: {redaction.get('redaction_status')}",
            f"Manual decision: {manual.get('decision')}",
            "",
            "Route A cannot be replaced by Route B, Full Corpus, mock-only, sample-only, or path-only evidence.",
        ]
    )


def public_route_a_closure_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)
