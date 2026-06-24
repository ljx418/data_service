"""Public surface contract regression for V2.66."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import contract_regression_artifact_refs, read_compatibility_report, read_contract_baseline, read_contract_diff, read_regression_diagnosis, write_contract_regression
from .shared import base_artifact, redaction_findings


PHASE = "V2.66"
CAPABILITIES = ["e2e", "portal", "delivery", "contract"]


class PublicSurfaceContractRegressionService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_contract(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = contract_regression_artifact_refs(codebase_id)
        baseline = _baseline(self.workspace_id, codebase_id, generated_at, refs)
        diff = _diff(self.workspace_id, codebase_id, generated_at, refs, baseline)
        compatibility = _compatibility(self.workspace_id, codebase_id, generated_at, refs, diff)
        diagnosis = _diagnosis(compatibility)
        unresolved = redaction_findings(baseline) + redaction_findings(diff) + redaction_findings(compatibility) + redaction_findings(diagnosis)
        if unresolved:
            compatibility["unresolved"].extend(unresolved)
        write_contract_regression(self.workspace, codebase_id, baseline, diff, compatibility, diagnosis)
        return _bundle(self.workspace_id, codebase_id, baseline, diff, compatibility, diagnosis, refs)

    def read_contract(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = contract_regression_artifact_refs(codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            read_contract_baseline(self.workspace, codebase_id),
            read_contract_diff(self.workspace, codebase_id),
            read_compatibility_report(self.workspace, codebase_id),
            read_regression_diagnosis(self.workspace, codebase_id),
            refs,
        )


def public_contract_regression_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "public_surface_contract_regression",
        "contract_baseline": payload.get("contract_baseline") or {},
        "contract_diff": payload.get("contract_diff") or {},
        "compatibility_report": payload.get("compatibility_report") or {},
        "regression_diagnosis": {"format": "markdown", "content": payload.get("regression_diagnosis") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _baseline(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    payload = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="contract_baseline", generated_at=generated_at, artifact_refs=refs, evidence_refs=_evidence_refs())
    payload["source"] = "adapter_registry_inspection"
    payload["surfaces"] = _current_surfaces()
    return payload


def _diff(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], baseline: dict[str, Any]) -> dict[str, Any]:
    payload = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="contract_diff", generated_at=generated_at, artifact_refs=refs, evidence_refs=baseline.get("evidence_refs", []))
    surfaces = baseline.get("surfaces") or {}
    items = []
    for capability in CAPABILITIES:
        for surface in ["mcp", "cli", "http", "artifact_schema"]:
            present = _capability_present(surfaces, surface, capability)
            items.append(
                {
                    "surface": surface,
                    "item": capability,
                    "change_type": "compatible_addition" if present else "needs_review",
                    "compatibility": "compatible" if present else "needs_review",
                    "baseline_ref": "adapter_registry_inspection",
                    "current_ref": "adapter_registry_inspection",
                    "diagnosis": "surface present" if present else "surface missing or not discoverable",
                    "next_action": "none" if present else "review public surface registration",
                }
            )
    payload["items"] = items
    return payload


def _compatibility(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], diff: dict[str, Any]) -> dict[str, Any]:
    payload = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="compatibility_report", generated_at=generated_at, artifact_refs=refs, evidence_refs=diff.get("evidence_refs", []))
    items = list(diff.get("items") or [])
    payload["items"] = items
    payload["summary"] = {
        "item_count": len(items),
        "compatible_count": sum(1 for item in items if item.get("compatibility") == "compatible"),
        "breaking_count": sum(1 for item in items if item.get("compatibility") == "breaking"),
        "needs_review_count": sum(1 for item in items if item.get("compatibility") == "needs_review"),
    }
    for item in items:
        if item.get("compatibility") == "breaking":
            payload["unresolved"].append({"kind": "structured_blocker", "reason": item.get("diagnosis"), "next_action": item.get("next_action")})
        if item.get("compatibility") == "needs_review":
            payload["unresolved"].append({"kind": "needs_review", "reason": item.get("diagnosis"), "next_action": item.get("next_action")})
    return payload


def _current_surfaces() -> dict[str, list[str]]:
    return {
        "mcp": sorted(_mcp_tools()),
        "cli": sorted(_cli_commands()),
        "http": sorted(_http_routes()),
        "artifact_schema": ["e2e", "portal", "delivery", "contract"],
    }


def _mcp_tools() -> set[str]:
    try:
        module = importlib.import_module("data_service.mcp_code_external_e2e_portal_delivery_tools")
        return set(getattr(module, "EXTERNAL_E2E_PORTAL_DELIVERY_TOOL_NAMES"))
    except Exception:
        return set()


def _cli_commands() -> set[str]:
    try:
        module = importlib.import_module("data_service.cli_code_external_e2e_portal_delivery")
        return {f"external-e2e-portal-delivery {name}" for name in getattr(module, "EXTERNAL_E2E_PORTAL_DELIVERY_COMMAND_TO_TOOL", {})}
    except Exception:
        return set()


def _http_routes() -> set[str]:
    try:
        module = importlib.import_module("app.main")
        paths = set()
        for route in getattr(module, "app").routes:
            path = getattr(route, "path", "")
            if "external-e2e-portal-delivery" in path:
                for method in sorted(getattr(route, "methods", []) or []):
                    if method not in {"HEAD", "OPTIONS"}:
                        paths.add(f"{method} {path}")
        return paths
    except Exception:
        return set()


def _capability_present(surfaces: dict[str, list[str]], surface: str, capability: str) -> bool:
    haystack = " ".join(surfaces.get(surface) or [])
    if surface == "artifact_schema":
        return capability in surfaces.get(surface, [])
    return capability in haystack


def _evidence_refs() -> list[dict[str, str]]:
    return [
        {"type": "mcp_registry", "artifact_ref": "backend/data_service/mcp_code_tools.py"},
        {"type": "cli_registry", "artifact_ref": "backend/data_service/cli_code.py"},
        {"type": "http_registry", "artifact_ref": "backend/app/api/__init__.py"},
    ]


def _diagnosis(compatibility: dict[str, Any]) -> str:
    lines = ["# Public Surface Contract Regression Diagnosis", ""]
    for item in compatibility.get("items", []):
        lines.append(f"- {item['surface']} {item['item']}: {item['compatibility']} ({item['diagnosis']})")
    lines.append("")
    lines.append("Breaking or needs_review items must not be accepted silently.")
    return "\n".join(lines) + "\n"


def _bundle(workspace_id: str, codebase_id: str, baseline: dict[str, Any], diff: dict[str, Any], compatibility: dict[str, Any], diagnosis: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.63-66",
        "artifact_type": "public_surface_contract_regression",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "contract_baseline": baseline,
        "contract_diff": diff,
        "compatibility_report": compatibility,
        "regression_diagnosis": diagnosis,
        "summary": dict(compatibility.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(compatibility.get("warnings") or []),
        "unresolved": list(compatibility.get("unresolved") or []),
        "next_actions": ["knowledge_code_external_e2e_portal_delivery_contract_read"],
    }
