"""V2.97 Route A evidence automation service."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    read_evidence_capture_manifest,
    read_manual_confirmation_queue,
    read_material_scan,
    read_redaction_audit,
    route_a_evidence_artifact_refs,
    write_route_a_evidence,
)
from .shared import apply_redaction_guard, base_artifact, public_payload, status_summary, unresolved_item


class RouteAEvidenceAutomator:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_route_a_evidence(self, codebase_id: str, material_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        state = material_state or {}
        generated_at = now()
        refs = route_a_evidence_artifact_refs(codebase_id)
        materials = _materials(state)
        redaction = dict(state.get("redaction") or {})
        capture = dict(state.get("evidence_capture") or {})
        manual = dict(state.get("manual_confirmation") or {})
        evidence_refs = _dedupe([ref for row in materials for ref in row.get("evidence_refs", [])] + list(capture.get("evidence_refs") or []) + list(manual.get("evidence_refs") or []) + list(state.get("evidence_refs") or []))
        redaction_status = str(redaction.get("status") or "needs_review")
        capture_status = str(capture.get("status") or ("accepted" if capture.get("evidence_refs") else "needs_review"))
        manual_status = str(manual.get("decision") or "needs_review")
        status = "accepted" if materials and redaction_status == "accepted" and capture_status == "accepted" and manual_status == "accepted" and evidence_refs else "needs_review"
        unresolved = []
        if not materials:
            unresolved.append(unresolved_item("needs_review", "Route A representative real materials are missing", item_id="route_a_materials", next_action="provide real user representative material refs"))
        if redaction_status != "accepted":
            unresolved.append(unresolved_item("needs_review", "Route A redaction audit is not accepted", item_id="route_a_redaction", next_action="provide redaction policy and accepted redaction review"))
        if capture_status != "accepted" or not evidence_refs:
            unresolved.append(unresolved_item("needs_review", "Route A screenshot/headless evidence is missing", item_id="route_a_capture", next_action="provide screenshot or headless evidence refs"))
        if manual_status != "accepted":
            unresolved.append(unresolved_item("needs_review", "Route A manual confirmation is not accepted", item_id="route_a_manual_confirmation", next_action="record reviewer confirmation"))
        scan = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase="V2.97", artifact_type="route_a_material_scan", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs, unresolved=unresolved, status=status, next_actions=["knowledge_code_automated_evidence_closure_route_a_evidence_read"])
        scan.update({"materials": materials, "data": {"materials": materials}, "summary": status_summary([{"status": status}])})
        redaction_artifact = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase="V2.97", artifact_type="route_a_redaction_audit", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs, unresolved=unresolved, status=status)
        redaction_artifact.update({"data": {"redaction_status": redaction_status, "policy_ref": str(redaction.get("policy_ref") or ""), "risk": str(redaction.get("risk") or "needs_review"), "findings": list(redaction.get("findings") or [])}})
        capture_artifact = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase="V2.97", artifact_type="route_a_evidence_capture_manifest", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs, unresolved=unresolved, status=status)
        capture_artifact.update({"data": {"capture_status": capture_status, "evidence_refs": evidence_refs, "capture_method": str(capture.get("method") or "headless_or_screenshot_refs")}})
        queue = _queue(status, materials, redaction_status, capture_status, manual_status)
        apply_redaction_guard(scan, redaction_artifact, capture_artifact, queue)
        write_route_a_evidence(self.workspace, codebase_id, scan, redaction_artifact, capture_artifact, queue)
        return self.read_route_a_evidence(codebase_id)

    def read_route_a_evidence(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        scan = read_material_scan(self.workspace, codebase_id)
        redaction = read_redaction_audit(self.workspace, codebase_id)
        capture = read_evidence_capture_manifest(self.workspace, codebase_id)
        queue = read_manual_confirmation_queue(self.workspace, codebase_id)
        return {
            "schema_version": "v2.96-100",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.97",
            "artifact_type": "route_a_evidence",
            "status": str(scan.get("status") or "needs_review"),
            "data": {"material_scan": scan, "redaction_audit": redaction, "evidence_capture_manifest": capture, "manual_confirmation_queue": queue},
            "summary": dict(scan.get("summary") or {}),
            "artifact_refs": route_a_evidence_artifact_refs(codebase_id),
            "evidence_refs": list(scan.get("evidence_refs") or []),
            "warnings": list(scan.get("warnings") or []),
            "unresolved": list(scan.get("unresolved") or []),
            "next_actions": ["knowledge_code_automated_evidence_closure_route_a_evidence_read"],
        }


def _materials(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for idx, item in enumerate(state.get("materials") or [], start=1):
        if not isinstance(item, dict):
            continue
        source_ref = str(item.get("source_ref") or "").strip()
        if not source_ref:
            continue
        rows.append({"material_id": str(item.get("material_id") or f"route_a_material_{idx}"), "source_type": str(item.get("source_type") or "document"), "source_ref": source_ref, "redaction_status": str(item.get("redaction_status") or "needs_review"), "evidence_refs": list(item.get("evidence_refs") or [])})
    return rows


def _dedupe(items: list[Any]) -> list[Any]:
    seen = set()
    result = []
    for item in items:
        key = json_key(item)
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def json_key(item: Any) -> str:
    return repr(item)


def _queue(status: str, materials: list[dict[str, Any]], redaction: str, capture: str, manual: str) -> str:
    lines = ["# V2.97 Route A Manual Confirmation Queue", "", f"Status: {status}", f"Material count: {len(materials)}", f"Redaction: {redaction}", f"Evidence capture: {capture}", f"Manual confirmation: {manual}", "", "Route B, Full Corpus, mock-only, sample-only, and path-only evidence cannot replace Route A representative material acceptance."]
    return "\n".join(lines)


def public_route_a_evidence_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)

