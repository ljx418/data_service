"""Portal V3+ experience hardening for V2.64."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    portal_v3_artifact_refs,
    read_artifact_readiness,
    read_experience_model,
    read_full_project_matrix,
    read_navigation_model,
    read_portal_html,
    read_status_panels,
    write_portal_v3,
)
from .shared import base_artifact, redaction_findings


PHASE = "V2.64"


class PortalV3ExperienceService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_portal(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = portal_v3_artifact_refs(codebase_id)
        matrix = _try_read(lambda: read_full_project_matrix(self.workspace, codebase_id))
        readiness = _try_read(lambda: read_artifact_readiness(self.workspace, codebase_id))
        experience = _experience(self.workspace_id, codebase_id, generated_at, refs, matrix, readiness)
        navigation = _navigation(self.workspace_id, codebase_id, generated_at, refs)
        panels = _panels(self.workspace_id, codebase_id, generated_at, refs, matrix, experience)
        html_text = _html(experience, panels)
        unresolved = redaction_findings(experience) + redaction_findings(navigation) + redaction_findings(panels) + redaction_findings(html_text)
        if unresolved:
            experience["unresolved"].extend(unresolved)
        write_portal_v3(self.workspace, codebase_id, experience, navigation, panels, html_text)
        return _bundle(self.workspace_id, codebase_id, experience, navigation, panels, html_text, refs)

    def read_portal(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = portal_v3_artifact_refs(codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            read_experience_model(self.workspace, codebase_id),
            read_navigation_model(self.workspace, codebase_id),
            read_status_panels(self.workspace, codebase_id),
            read_portal_html(self.workspace, codebase_id),
            refs,
        )


def public_portal_v3_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "portal_v3_experience",
        "experience_model": payload.get("experience_model") or {},
        "navigation_model": payload.get("navigation_model") or {},
        "status_panels": payload.get("status_panels") or {},
        "project_portal_v3_plus_html": {"format": "html", "content": payload.get("project_portal_v3_plus_html") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _try_read(reader):
    try:
        return reader()
    except FileNotFoundError:
        return {}


def _status_from_matrix(matrix: dict[str, Any]) -> str:
    statuses = {item.get("status") for item in matrix.get("projects", [])}
    if not statuses:
        return "needs_review"
    if "structured_blocker" in statuses:
        return "structured_blocker"
    if "structured_unavailable" in statuses:
        return "structured_unavailable"
    if "needs_review" in statuses:
        return "needs_review"
    return "accepted" if statuses == {"accepted"} else "needs_review"


def _experience(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], matrix: dict[str, Any], readiness: dict[str, Any]) -> dict[str, Any]:
    payload = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="experience_model", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
    e2e_status = _status_from_matrix(matrix)
    payload.update(
        {
            "stage_status": "implementing" if e2e_status != "accepted" else "accepted",
            "external_e2e_status": e2e_status,
            "contract_status": "needs_review",
            "delivery_status": "needs_review",
            "exit_status": "accepted" if e2e_status == "accepted" else "needs_review",
            "questions_answered": [
                "当前哪些能力真的可用",
                "哪些外部项目 E2E 通过",
                "哪些风险阻止出门",
                "交付包是否清晰可审查",
                "下一步应该做什么",
            ],
            "next_actions": _next_actions(matrix, readiness),
        }
    )
    return payload


def _navigation(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    payload = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="navigation_model", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
    payload["tabs"] = ["stage_overview", "external_e2e", "contract", "delivery", "risk", "exit_status"]
    return payload


def _panels(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], matrix: dict[str, Any], experience: dict[str, Any]) -> dict[str, Any]:
    payload = base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="status_panels", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
    projects = matrix.get("projects") or []
    payload["sections"] = [
        _panel("stage_overview", "阶段总览", experience.get("stage_status"), refs, "Review phase gates"),
        _panel("external_e2e", "外部项目 E2E", experience.get("external_e2e_status"), refs, "Review unavailable projects", projects=projects),
        _panel("contract", "合同稳定性", experience.get("contract_status"), refs, "Run V2.66 contract regression"),
        _panel("delivery", "交付状态", experience.get("delivery_status"), refs, "Run V2.65 delivery manifest"),
        _panel("risk", "风险与下一步", "needs_review" if any(p.get("status") != "accepted" for p in projects) else "accepted", refs, "Resolve non-accepted statuses"),
        _panel("exit_status", "出门条件", experience.get("exit_status"), refs, "Run final acceptance audit"),
    ]
    return payload


def _panel(panel_id: str, title: str, status: str | None, refs: list[dict[str, str]], next_action: str, *, projects: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    unresolved = []
    if status != "accepted":
        unresolved.append({"kind": status or "needs_review", "reason": f"{title} is not accepted", "next_action": next_action})
    item = {
        "id": panel_id,
        "title": title,
        "status": status or "needs_review",
        "artifact_refs": refs,
        "evidence_refs": refs,
        "unresolved": unresolved,
        "next_action": next_action,
    }
    if projects is not None:
        item["projects"] = projects
    return item


def _next_actions(matrix: dict[str, Any], readiness: dict[str, Any]) -> list[str]:
    actions = []
    for row in matrix.get("projects", []):
        if row.get("status") != "accepted":
            actions.append(f"Review {row.get('project_id')} {row.get('status')}: {row.get('next_action')}")
    if not actions:
        actions.append("Run delivery and contract regression stages before final exit")
    if not readiness:
        actions.append("Build external E2E before relying on Portal status")
    return actions


def _html(experience: dict[str, Any], panels: dict[str, Any]) -> str:
    sections = "\n".join(
        f"<tr><td>{html.escape(item['title'])}</td><td>{html.escape(item['status'])}</td><td>{html.escape(item['next_action'])}</td></tr>"
        for item in panels.get("sections", [])
    )
    actions = "\n".join(f"<li>{html.escape(action)}</li>" for action in experience.get("next_actions", []))
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>V2.64 Portal V3+</title></head>
<body>
<h1>维护者首页</h1>
<p>当前页面只展示 persisted artifacts；未验收状态不会被隐藏。</p>
<table><thead><tr><th>面板</th><th>状态</th><th>下一步</th></tr></thead><tbody>{sections}</tbody></table>
<h2>下一步动作</h2>
<ul>{actions}</ul>
</body>
</html>
"""


def _bundle(workspace_id: str, codebase_id: str, experience: dict[str, Any], navigation: dict[str, Any], panels: dict[str, Any], html_text: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.63-66",
        "artifact_type": "portal_v3_experience",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "experience_model": experience,
        "navigation_model": navigation,
        "status_panels": panels,
        "project_portal_v3_plus_html": html_text,
        "summary": {
            "panel_count": len(panels.get("sections") or []),
            "raw_mermaid_visible": "```mermaid" in html_text,
            "non_accepted_panel_count": sum(1 for item in panels.get("sections", []) if item.get("status") != "accepted"),
        },
        "artifact_refs": refs,
        "warnings": list(experience.get("warnings") or []),
        "unresolved": list(experience.get("unresolved") or []),
        "next_actions": ["knowledge_code_external_e2e_portal_delivery_portal_read"],
    }
