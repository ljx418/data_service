"""Maintainer console productization artifacts for V2.79."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    console_productization_artifact_refs,
    read_action_registry,
    read_console_product_report,
    read_experience_model,
    read_panel_contract,
    read_project_preflight,
    read_readiness_gate,
    read_reconciled_matrix,
    read_release_warning_gate,
    write_console_productization,
)
from .shared import base_artifact, redaction_findings, unresolved_item, worst_status


PHASE = "V2.79"


class MaintainerConsoleProductizationService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_console_product(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = console_productization_artifact_refs(codebase_id)
        panels = _panels(self.workspace, codebase_id)
        model = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="maintainer_console_experience_model", generated_at=generated_at, artifact_refs=refs, evidence_refs=_evidence_refs(panels), next_actions=["knowledge_code_project_acceptance_hardening_console_product_read"])
        model["panels"] = panels
        model["stage_status"] = worst_status([panel["status"] for panel in panels])
        model["target_experience"] = "Maintainer can see acceptance status, real-project binding, warning gate, release readiness, and required next action from one persisted model."
        contract = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="maintainer_console_panel_contract", generated_at=generated_at, artifact_refs=refs, evidence_refs=model["evidence_refs"])
        contract["required_panel_fields"] = ["panel_id", "title", "status", "source_artifact_ref", "evidence_refs", "unresolved", "next_action"]
        contract["panels"] = [{field: panel.get(field) for field in contract["required_panel_fields"]} for panel in panels]
        actions = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="maintainer_console_action_registry", generated_at=generated_at, artifact_refs=refs, evidence_refs=model["evidence_refs"])
        actions["actions"] = _actions(panels)
        report = _report(model)
        unresolved = redaction_findings(model) + redaction_findings(contract) + redaction_findings(actions) + redaction_findings(report)
        if unresolved:
            model["unresolved"].extend(unresolved)
        write_console_productization(self.workspace, codebase_id, model, contract, actions, report)
        return _bundle(self.workspace_id, codebase_id, model, contract, actions, report, refs)

    def read_console_product(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = console_productization_artifact_refs(codebase_id)
        return _bundle(self.workspace_id, codebase_id, read_experience_model(self.workspace, codebase_id), read_panel_contract(self.workspace, codebase_id), read_action_registry(self.workspace, codebase_id), read_console_product_report(self.workspace, codebase_id), refs)


def public_console_product_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "maintainer_console_productization",
        "experience_model": payload.get("experience_model") or {},
        "panel_contract": payload.get("panel_contract") or {},
        "action_registry": payload.get("action_registry") or {},
        "maintainer_console_product_report": {"format": "markdown", "content": payload.get("maintainer_console_product_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _panels(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    specs = [
        ("acceptance_reconciliation", "验收矩阵对齐", read_reconciled_matrix, "project_acceptance_hardening://{codebase_id}/acceptance_reconciliation/reconciled_matrix.json"),
        ("external_project_binding", "真实项目绑定", read_project_preflight, "project_acceptance_hardening://{codebase_id}/external_project_binding/project_preflight.json"),
        ("warning_reduction", "CI warning 出门门禁", read_release_warning_gate, "project_acceptance_hardening://{codebase_id}/warning_reduction/release_warning_gate.json"),
        ("release_readiness", "发布就绪闭环", read_readiness_gate, "project_acceptance_hardening://{codebase_id}/release_readiness/readiness_gate.json"),
        ("human_approval", "高风险人工确认", None, "project_acceptance_hardening://human/approval"),
    ]
    panels: list[dict[str, Any]] = []
    for panel_id, title, reader, ref_template in specs:
        ref = ref_template.format(codebase_id=codebase_id)
        if reader is None:
            panels.append(_manual_panel(panel_id, title, ref))
            continue
        try:
            source = reader(workspace, codebase_id)
            status = _source_status(source)
            panels.append(
                {
                    "panel_id": panel_id,
                    "title": title,
                    "status": status,
                    "source_artifact_ref": ref,
                    "evidence_refs": list(source.get("evidence_refs") or source.get("artifact_refs") or [ref]),
                    "unresolved": list(source.get("unresolved") or []),
                    "next_action": "none" if status == "accepted" else "review panel source artifact",
                }
            )
        except FileNotFoundError:
            panels.append(
                {
                    "panel_id": panel_id,
                    "title": title,
                    "status": "needs_review",
                    "source_artifact_ref": ref,
                    "evidence_refs": [],
                    "unresolved": [unresolved_item("needs_review", "panel source artifact is not built", item_id=panel_id, next_action="build prior phase artifact")],
                    "next_action": "build prior phase artifact",
                }
            )
    return panels


def _manual_panel(panel_id: str, title: str, ref: str) -> dict[str, Any]:
    return {
        "panel_id": panel_id,
        "title": title,
        "status": "needs_review",
        "source_artifact_ref": ref,
        "evidence_refs": [],
        "unresolved": [unresolved_item("needs_review", "high-risk release approval remains a human decision", item_id=panel_id, next_action="capture human approval decision")],
        "next_action": "capture human approval decision",
    }


def _source_status(source: dict[str, Any]) -> str:
    for key in ("status", "stage_status", "readiness_status", "overall_status"):
        if source.get(key):
            return str(source[key])
    if source.get("summary", {}).get("status"):
        return str(source["summary"]["status"])
    if source.get("summary", {}).get("structured_unavailable_count"):
        return "structured_unavailable"
    return "accepted"


def _evidence_refs(panels: list[dict[str, Any]]) -> list[Any]:
    refs: list[Any] = []
    for panel in panels:
        refs.extend(panel.get("evidence_refs") or [])
    return refs


def _actions(panels: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{"panel_id": panel["panel_id"], "status": panel["status"], "action": panel["next_action"], "mcp_read_tool": "knowledge_code_project_acceptance_hardening_console_product_read"} for panel in panels]


def _report(model: dict[str, Any]) -> str:
    lines = ["# V2.79 Maintainer Console Productization Report", "", f"Stage status: {model.get('stage_status')}", ""]
    for panel in model.get("panels") or []:
        lines.append(f"- {panel['title']}: {panel['status']} -> {panel['next_action']}")
    lines.append("")
    lines.append("The console model preserves non-accepted states and does not create acceptance facts.")
    return "\n".join(lines) + "\n"


def _bundle(workspace_id: str, codebase_id: str, model: dict[str, Any], contract: dict[str, Any], actions: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.76-80",
        "artifact_type": "maintainer_console_productization",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "experience_model": model,
        "panel_contract": contract,
        "action_registry": actions,
        "maintainer_console_product_report": report,
        "summary": {"stage_status": model.get("stage_status"), "panel_count": len(model.get("panels") or [])},
        "artifact_refs": refs,
        "warnings": list(model.get("warnings") or []),
        "unresolved": list(model.get("unresolved") or []),
        "next_actions": ["knowledge_code_project_acceptance_hardening_console_product_read"],
    }
