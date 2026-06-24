"""Versioned public surface baseline for V2.69."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .contract_regression import _current_surfaces, _evidence_refs
from .persistence import (
    read_surface_baseline_diff,
    read_surface_baseline_report,
    read_surface_baseline_version,
    surface_baseline_artifact_refs,
    write_surface_baseline,
)
from .shared import base_artifact, redaction_findings


PHASE = "V2.69"


class VersionedPublicSurfaceBaselineService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_surface_baseline(self, codebase_id: str, baseline_label: str = "v2.67-70") -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = surface_baseline_artifact_refs(codebase_id)
        baseline = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="surface_baseline_version",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=_evidence_refs(),
            next_actions=["knowledge_code_external_e2e_portal_delivery_surface_baseline_read"],
        )
        baseline["baseline_label"] = baseline_label
        baseline["source"] = "adapter_registry_inspection"
        baseline["surfaces"] = _current_surfaces()
        diff = _diff(self.workspace_id, codebase_id, generated_at, refs, baseline)
        report = _report(diff)
        unresolved = redaction_findings(baseline) + redaction_findings(diff) + redaction_findings(report)
        if unresolved:
            diff["unresolved"].extend(unresolved)
        write_surface_baseline(self.workspace, codebase_id, baseline, diff, report)
        return _bundle(self.workspace_id, codebase_id, baseline, diff, report, refs)

    def read_surface_baseline(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = surface_baseline_artifact_refs(codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            read_surface_baseline_version(self.workspace, codebase_id),
            read_surface_baseline_diff(self.workspace, codebase_id),
            read_surface_baseline_report(self.workspace, codebase_id),
            refs,
        )


def public_surface_baseline_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "versioned_public_surface_baseline",
        "surface_baseline_version": payload.get("surface_baseline_version") or {},
        "surface_baseline_diff": payload.get("surface_baseline_diff") or {},
        "surface_baseline_report": {"format": "markdown", "content": payload.get("surface_baseline_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _diff(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], baseline: dict[str, Any]) -> dict[str, Any]:
    payload = base_artifact(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        phase=PHASE,
        artifact_type="surface_baseline_diff",
        generated_at=generated_at,
        artifact_refs=refs,
        evidence_refs=baseline.get("evidence_refs", []),
    )
    items = []
    surfaces = baseline.get("surfaces") or {}
    for surface, values in sorted(surfaces.items()):
        status = "accepted" if values else "needs_review"
        items.append(
            {
                "surface": surface,
                "status": status,
                "item_count": len(values or []),
                "change_type": "versioned_baseline_recorded" if status == "accepted" else "surface_unavailable",
                "compatibility": "compatible" if status == "accepted" else "needs_review",
                "evidence_refs": baseline.get("evidence_refs", []),
                "next_action": "none" if status == "accepted" else "review adapter registration",
            }
        )
    payload["items"] = items
    payload["summary"] = {
        "surface_count": len(items),
        "compatible_count": sum(1 for item in items if item["compatibility"] == "compatible"),
        "breaking_count": sum(1 for item in items if item["compatibility"] == "breaking"),
        "needs_review_count": sum(1 for item in items if item["compatibility"] == "needs_review"),
    }
    for item in items:
        if item["compatibility"] != "compatible":
            payload["unresolved"].append({"kind": "needs_review", "reason": f"{item['surface']} has no current registry entries", "next_action": item["next_action"]})
    return payload


def _report(diff: dict[str, Any]) -> str:
    lines = ["# Versioned Public Surface Baseline Report", ""]
    for item in diff.get("items", []):
        lines.append(f"- {item['surface']}: {item['compatibility']} ({item['item_count']} entries)")
    lines.append("")
    lines.append("This baseline is generated from real adapter and registry inspection.")
    return "\n".join(lines) + "\n"


def _bundle(workspace_id: str, codebase_id: str, baseline: dict[str, Any], diff: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.63-70",
        "artifact_type": "versioned_public_surface_baseline",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "surface_baseline_version": baseline,
        "surface_baseline_diff": diff,
        "surface_baseline_report": report,
        "summary": dict(diff.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(diff.get("warnings") or []),
        "unresolved": list(diff.get("unresolved") or []),
        "next_actions": ["knowledge_code_external_e2e_portal_delivery_surface_baseline_read"],
    }
