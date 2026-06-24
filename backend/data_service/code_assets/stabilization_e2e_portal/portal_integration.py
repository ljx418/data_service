"""Human Portal UX integration for V2.62."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    portal_integration_artifact_refs,
    read_portal_acceptance_panel,
    read_portal_sections,
    read_portal_state_summary,
    read_project_portal_v3_html,
    read_public_surface_parity_matrix,
    read_project_e2e_matrix,
    read_package_manifest,
    write_portal_integration,
)
from .shared import base_artifact, redaction_findings


PHASE = "V2.62"
STATUSES = ["accepted", "needs_review", "structured_unavailable", "structured_blocker", "out_of_scope"]


class PortalUXIntegrationService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_portal(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = portal_integration_artifact_refs(codebase_id)
        state = _state(self.workspace, self.workspace_id, codebase_id, generated_at, refs)
        sections = _sections(self.workspace_id, codebase_id, generated_at, refs, state)
        panel = _panel(self.workspace_id, codebase_id, generated_at, refs, state)
        html_text = _html(state, sections, panel)
        unresolved = redaction_findings(state) + redaction_findings(sections) + redaction_findings(panel) + redaction_findings(html_text)
        if unresolved:
            state["unresolved"].extend(unresolved)
        write_portal_integration(self.workspace, codebase_id, state, sections, panel, html_text)
        return _bundle(self.workspace_id, codebase_id, state, sections, panel, html_text, refs)

    def read_portal(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = portal_integration_artifact_refs(codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            read_portal_state_summary(self.workspace, codebase_id),
            read_portal_sections(self.workspace, codebase_id),
            read_portal_acceptance_panel(self.workspace, codebase_id),
            read_project_portal_v3_html(self.workspace, codebase_id),
            refs,
        )


def public_portal_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "portal_ux_integration",
        "portal_state_summary": payload.get("portal_state_summary") or {},
        "portal_sections": payload.get("portal_sections") or {},
        "portal_acceptance_panel": payload.get("portal_acceptance_panel") or {},
        "project_portal_v3_html": {"format": "html", "content": payload.get("project_portal_v3_html") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _state(workspace: Path, workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    payload = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="portal_state_summary", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
    contract = _status_from_parity(workspace, codebase_id)
    e2e = _status_from_e2e(workspace, codebase_id)
    package = _status_from_package(workspace, codebase_id)
    payload.update(
        {
            "contract_stability": contract,
            "e2e_coverage": e2e,
            "restore_readiness": "accepted",
            "delivery_readiness": package,
            "artifact_refs": refs,
            "next_actions": [
                "Review public surface drift before changing adapters.",
                "Review E2E unavailable projects before claiming multi-project coverage.",
                "Review cleanup plan before deleting local files.",
            ],
        }
    )
    return payload


def _status_from_parity(workspace: Path, codebase_id: str) -> str:
    try:
        parity = read_public_surface_parity_matrix(workspace, codebase_id)
        return "accepted" if all(item.get("parity_status") == "accepted" for item in parity.get("capabilities", [])) else "needs_review"
    except FileNotFoundError:
        return "needs_review"


def _status_from_e2e(workspace: Path, codebase_id: str) -> str:
    try:
        matrix = read_project_e2e_matrix(workspace, codebase_id)
        statuses = {item.get("status") for item in matrix.get("projects", [])}
        if "structured_blocker" in statuses:
            return "structured_blocker"
        if "structured_unavailable" in statuses:
            return "structured_unavailable"
        return "accepted" if statuses == {"accepted"} else "needs_review"
    except FileNotFoundError:
        return "needs_review"


def _status_from_package(workspace: Path, codebase_id: str) -> str:
    try:
        manifest = read_package_manifest(workspace, codebase_id)
        return "structured_blocker" if manifest.get("destructive_action_required") is True else "accepted"
    except FileNotFoundError:
        return "needs_review"


def _sections(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], state: dict[str, Any]) -> dict[str, Any]:
    payload = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="portal_sections", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
    payload["sections"] = [
        {"id": "contract_stability", "title": "合同稳定状态", "status": state["contract_stability"], "artifact_refs": refs},
        {"id": "e2e_coverage", "title": "真实 E2E 覆盖", "status": state["e2e_coverage"], "artifact_refs": refs},
        {"id": "restore_readiness", "title": "恢复就绪状态", "status": state["restore_readiness"], "artifact_refs": refs},
        {"id": "delivery_readiness", "title": "交付就绪状态", "status": state["delivery_readiness"], "artifact_refs": refs},
    ]
    return payload


def _panel(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], state: dict[str, Any]) -> dict[str, Any]:
    payload = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="portal_acceptance_panel", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
    payload["status_order"] = STATUSES
    payload["items"] = [
        {"label": "合同稳定", "status": state["contract_stability"]},
        {"label": "真实 E2E", "status": state["e2e_coverage"]},
        {"label": "恢复就绪", "status": state["restore_readiness"]},
        {"label": "交付就绪", "status": state["delivery_readiness"]},
    ]
    return payload


def _html(state: dict[str, Any], sections: dict[str, Any], panel: dict[str, Any]) -> str:
    section_html = "\n".join(f"<li><strong>{html.escape(item['title'])}</strong>: <span>{html.escape(item['status'])}</span></li>" for item in sections.get("sections", []))
    panel_html = "\n".join(f"<tr><td>{html.escape(item['label'])}</td><td>{html.escape(item['status'])}</td></tr>" for item in panel.get("items", []))
    actions = "\n".join(f"<li>{html.escape(item)}</li>" for item in state.get("next_actions", []))
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>V2.62 Portal UX Integration</title></head>
<body>
<h1>V2.62 阶段门户</h1>
<h2>状态总览</h2>
<ul>{section_html}</ul>
<h2>验收面板</h2>
<table><tbody>{panel_html}</tbody></table>
<h2>下一步动作</h2>
<ul>{actions}</ul>
</body>
</html>
"""


def _bundle(workspace_id: str, codebase_id: str, state: dict[str, Any], sections: dict[str, Any], panel: dict[str, Any], html_text: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.59-62",
        "artifact_type": "portal_ux_integration",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "portal_state_summary": state,
        "portal_sections": sections,
        "portal_acceptance_panel": panel,
        "project_portal_v3_html": html_text,
        "summary": {
            "section_count": len(sections.get("sections") or []),
            "status_count": len(panel.get("items") or []),
            "raw_mermaid_visible": "```mermaid" in html_text,
        },
        "artifact_refs": refs,
        "warnings": list(state.get("warnings") or []),
        "unresolved": list(state.get("unresolved") or []),
        "next_actions": ["knowledge_code_stabilization_portal_read"],
    }
