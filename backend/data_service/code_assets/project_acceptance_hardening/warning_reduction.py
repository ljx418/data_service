"""CI warning reduction release gate artifacts for V2.78."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..agent_memory_release.persistence import read_warning_budget
from ..registry import CodebaseRegistry
from .persistence import (
    read_reduction_plan,
    read_release_warning_gate,
    read_warning_inventory,
    read_warning_reduction_report,
    warning_reduction_artifact_refs,
    write_warning_reduction,
)
from .shared import FAILURE_CATEGORIES, base_artifact, redaction_findings, unresolved_item


PHASE = "V2.78"


class CIWarningReductionService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_warning_reduction(self, codebase_id: str, command_results: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = warning_reduction_artifact_refs(codebase_id)
        results = _merged_results(self.workspace, codebase_id, command_results or {})
        warnings = _warning_items(results)
        observed = int(results.get("observed_warning_count", len(warnings)))
        budget = int(results.get("warning_budget", 300))
        gate_status = "accepted" if observed <= budget and all(item["status"] == "accepted" for item in warnings) else "structured_blocker"
        inventory = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="warning_inventory", generated_at=generated_at, artifact_refs=refs, evidence_refs=_evidence_refs(warnings), next_actions=["knowledge_code_project_acceptance_hardening_warning_reduction_read"])
        inventory["items"] = warnings
        inventory["summary"] = {"observed_warning_count": observed, "warning_budget": budget, "over_budget": observed > budget}
        plan = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="warning_reduction_plan", generated_at=generated_at, artifact_refs=refs, evidence_refs=inventory["evidence_refs"])
        plan["items"] = [_plan_item(item) for item in warnings]
        gate = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="release_warning_gate", generated_at=generated_at, artifact_refs=refs, evidence_refs=inventory["evidence_refs"])
        gate.update({"status": gate_status, "observed_warning_count": observed, "warning_budget": budget, "blocking_warning_count": sum(1 for item in warnings if item["status"] != "accepted"), "next_action": "none" if gate_status == "accepted" else "reduce warnings before release"})
        if gate_status != "accepted":
            gate["unresolved"].append(unresolved_item("structured_blocker", "warning budget or warning ownership gate is not satisfied", item_id="warning_gate", next_action="reduce warnings before release"))
        report = _report(inventory, gate)
        unresolved = redaction_findings(inventory) + redaction_findings(plan) + redaction_findings(gate) + redaction_findings(report)
        if unresolved:
            gate["unresolved"].extend(unresolved)
            gate["status"] = "structured_blocker"
        write_warning_reduction(self.workspace, codebase_id, inventory, plan, gate, report)
        return _bundle(self.workspace_id, codebase_id, inventory, plan, gate, report, refs)

    def read_warning_reduction(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = warning_reduction_artifact_refs(codebase_id)
        return _bundle(self.workspace_id, codebase_id, read_warning_inventory(self.workspace, codebase_id), read_reduction_plan(self.workspace, codebase_id), read_release_warning_gate(self.workspace, codebase_id), read_warning_reduction_report(self.workspace, codebase_id), refs)


def public_warning_reduction_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "ci_warning_reduction",
        "warning_inventory": payload.get("warning_inventory") or {},
        "reduction_plan": payload.get("reduction_plan") or {},
        "release_warning_gate": payload.get("release_warning_gate") or {},
        "warning_reduction_report": {"format": "markdown", "content": payload.get("warning_reduction_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _merged_results(workspace: Path, codebase_id: str, command_results: dict[str, Any]) -> dict[str, Any]:
    merged = dict(command_results)
    if "observed_warning_count" not in merged or "warning_budget" not in merged:
        try:
            upstream = read_warning_budget(workspace, codebase_id)
            merged.setdefault("observed_warning_count", upstream.get("observed_warning_count"))
            merged.setdefault("warning_budget", upstream.get("warning_budget"))
        except FileNotFoundError:
            pass
    merged.setdefault("observed_warning_count", 0)
    merged.setdefault("warning_budget", 300)
    return merged


def _warning_items(results: dict[str, Any]) -> list[dict[str, Any]]:
    raw_items = list(results.get("warnings") or [])
    if not raw_items and int(results.get("observed_warning_count", 0)) > int(results.get("warning_budget", 0)):
        raw_items = [{"id": "warning_budget_overflow", "count": int(results["observed_warning_count"]) - int(results["warning_budget"]), "category": results.get("failure_category") or "needs_review", "owner": results.get("owner") or ""}]
    items: list[dict[str, Any]] = []
    for index, item in enumerate(raw_items):
        category = str(item.get("category") or item.get("failure_category") or "needs_review")
        if category not in FAILURE_CATEGORIES:
            category = "needs_review"
        owner = str(item.get("owner") or "")
        status = "accepted" if owner and int(item.get("count", 1)) == 0 else "needs_review"
        items.append(
            {
                "id": str(item.get("id") or f"warning_{index}"),
                "status": status,
                "category": category,
                "owner": owner or "needs_review",
                "count": int(item.get("count", 1)),
                "evidence_refs": list(item.get("evidence_refs") or []),
                "unresolved": [] if status == "accepted" else [unresolved_item("needs_review", "warning requires owner or reduction evidence", item_id=str(item.get("id") or f"warning_{index}"))],
                "next_action": "none" if status == "accepted" else "assign owner and reduce warning",
            }
        )
    return items


def _plan_item(item: dict[str, Any]) -> dict[str, Any]:
    return {"id": item["id"], "status": item["status"], "category": item["category"], "owner": item["owner"], "action": "none" if item["status"] == "accepted" else "reduce or explicitly waive with evidence", "safe_to_ignore": False}


def _evidence_refs(items: list[dict[str, Any]]) -> list[Any]:
    refs: list[Any] = []
    for item in items:
        refs.extend(item.get("evidence_refs") or [])
    return refs


def _report(inventory: dict[str, Any], gate: dict[str, Any]) -> str:
    return "\n".join([
        "# V2.78 CI Warning Reduction Report",
        "",
        f"Observed warnings: {gate['observed_warning_count']}",
        f"Warning budget: {gate['warning_budget']}",
        f"Gate status: {gate['status']}",
        "",
        "Over-budget or unowned warning records block release acceptance.",
    ]) + "\n"


def _bundle(workspace_id: str, codebase_id: str, inventory: dict[str, Any], plan: dict[str, Any], gate: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.76-80",
        "artifact_type": "ci_warning_reduction",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "warning_inventory": inventory,
        "reduction_plan": plan,
        "release_warning_gate": gate,
        "warning_reduction_report": report,
        "summary": {"status": gate.get("status"), "observed_warning_count": gate.get("observed_warning_count"), "warning_budget": gate.get("warning_budget")},
        "artifact_refs": refs,
        "warnings": list(gate.get("warnings") or []),
        "unresolved": list(gate.get("unresolved") or []),
        "next_actions": ["knowledge_code_project_acceptance_hardening_warning_reduction_read"],
    }
