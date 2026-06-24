"""Maintainer home and status dashboard for V2.70."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    maintainer_dashboard_artifact_refs,
    read_delivery_review_manifest,
    read_maintainer_dashboard_html,
    read_maintainer_dashboard_model,
    read_maintainer_dashboard_panels,
    read_path_binding_matrix,
    read_surface_baseline_diff,
    read_full_project_matrix,
    read_status_panels,
    write_maintainer_dashboard,
)
from .shared import base_artifact, redaction_findings


PHASE = "V2.70"


class MaintainerHomeStatusDashboardService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_dashboard(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = maintainer_dashboard_artifact_refs(codebase_id)
        sources = _sources(self.workspace, codebase_id)
        model = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="maintainer_home_model",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=_evidence_refs(sources),
            next_actions=["knowledge_code_external_e2e_portal_delivery_dashboard_read"],
        )
        panels = _panels(self.workspace_id, codebase_id, generated_at, refs, sources)
        model["stage_status"] = _overall_status(panels)
        model["questions_answered"] = [
            "哪些外部项目已经具备真实路径或 E2E 证据",
            "当前工作树交付包是否可审查",
            "public surface baseline 是否来自真实 registry",
            "出门前还剩哪些非 accepted 状态",
        ]
        model["next_actions"] = _next_actions(panels)
        html_text = _html(model, panels)
        unresolved = redaction_findings(model) + redaction_findings(panels) + redaction_findings(html_text)
        if unresolved:
            model["unresolved"].extend(unresolved)
        write_maintainer_dashboard(self.workspace, codebase_id, model, panels, html_text)
        return _bundle(self.workspace_id, codebase_id, model, panels, html_text, refs)

    def read_dashboard(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = maintainer_dashboard_artifact_refs(codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            read_maintainer_dashboard_model(self.workspace, codebase_id),
            read_maintainer_dashboard_panels(self.workspace, codebase_id),
            read_maintainer_dashboard_html(self.workspace, codebase_id),
            refs,
        )


def public_dashboard_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "maintainer_home_status_dashboard",
        "maintainer_home_model": payload.get("maintainer_home_model") or {},
        "maintainer_status_panels": payload.get("maintainer_status_panels") or {},
        "maintainer_home_html": {"format": "html", "content": payload.get("maintainer_home_html") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _sources(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return {
        "external_e2e": _try_read(lambda: read_full_project_matrix(workspace, codebase_id)),
        "path_binding": _try_read(lambda: read_path_binding_matrix(workspace, codebase_id)),
        "worktree_delivery": _try_read(lambda: read_delivery_review_manifest(workspace, codebase_id)),
        "surface_baseline": _try_read(lambda: read_surface_baseline_diff(workspace, codebase_id)),
        "portal_v3": _try_read(lambda: read_status_panels(workspace, codebase_id)),
    }


def _try_read(reader):
    try:
        return reader()
    except FileNotFoundError:
        return {}


def _evidence_refs(sources: dict[str, Any]) -> list[dict[str, str]]:
    refs = []
    for source in sources.values():
        refs.extend(source.get("artifact_refs") or [])
    return refs


def _panels(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], sources: dict[str, Any]) -> dict[str, Any]:
    payload = base_artifact(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        phase=PHASE,
        artifact_type="maintainer_status_panels",
        generated_at=generated_at,
        artifact_refs=refs,
        evidence_refs=_evidence_refs(sources),
    )
    payload["sections"] = [
        _panel("path_binding", "外部项目路径绑定", _status_from_projects(sources["path_binding"].get("projects") or []), sources["path_binding"], "提供真实外部项目路径并重新构建"),
        _panel("external_e2e", "真实项目 E2E", _status_from_projects(sources["external_e2e"].get("projects") or []), sources["external_e2e"], "运行外部项目 E2E"),
        _panel("worktree_delivery", "工作树交付清单", _status_from_gate(sources["worktree_delivery"].get("exit_gate") or {}), sources["worktree_delivery"], "复核 manual_review 和 local_temp 项"),
        _panel("surface_baseline", "Public Surface Baseline", _status_from_summary(sources["surface_baseline"].get("summary") or {}), sources["surface_baseline"], "复核 needs_review 或 breaking surface"),
        _panel("portal_v3", "Portal V3 继承状态", _status_from_sections(sources["portal_v3"].get("sections") or []), sources["portal_v3"], "构建或复核 Portal V3"),
    ]
    payload["summary"] = {
        "panel_count": len(payload["sections"]),
        "accepted_panel_count": sum(1 for item in payload["sections"] if item["status"] == "accepted"),
        "non_accepted_panel_count": sum(1 for item in payload["sections"] if item["status"] != "accepted"),
    }
    return payload


def _panel(panel_id: str, title: str, status: str, source: dict[str, Any], next_action: str) -> dict[str, Any]:
    unresolved = []
    if status != "accepted":
        unresolved.append({"kind": status, "reason": f"{title} is {status}", "next_action": next_action})
    return {
        "id": panel_id,
        "title": title,
        "status": status,
        "artifact_refs": source.get("artifact_refs") or [],
        "evidence_refs": source.get("evidence_refs") or source.get("artifact_refs") or [],
        "unresolved": unresolved,
        "next_action": next_action if status != "accepted" else "none",
    }


def _status_from_projects(projects: list[dict[str, Any]]) -> str:
    statuses = {item.get("status") for item in projects}
    if not statuses:
        return "needs_review"
    if "structured_blocker" in statuses:
        return "structured_blocker"
    if "structured_unavailable" in statuses:
        return "structured_unavailable"
    if "needs_review" in statuses:
        return "needs_review"
    return "accepted" if statuses == {"accepted"} else "needs_review"


def _status_from_gate(gate: dict[str, Any]) -> str:
    return str(gate.get("status") or "needs_review")


def _status_from_summary(summary: dict[str, Any]) -> str:
    if summary.get("breaking_count"):
        return "structured_blocker"
    if summary.get("needs_review_count"):
        return "needs_review"
    return "accepted" if summary.get("compatible_count") else "needs_review"


def _status_from_sections(sections: list[dict[str, Any]]) -> str:
    if not sections:
        return "needs_review"
    return "accepted" if all(item.get("status") == "accepted" for item in sections) else "needs_review"


def _overall_status(panels: dict[str, Any]) -> str:
    statuses = {item.get("status") for item in panels.get("sections", [])}
    if "structured_blocker" in statuses:
        return "structured_blocker"
    if "structured_unavailable" in statuses:
        return "structured_unavailable"
    if "needs_review" in statuses:
        return "needs_review"
    return "accepted" if statuses == {"accepted"} else "needs_review"


def _next_actions(panels: dict[str, Any]) -> list[str]:
    actions = [item["next_action"] for item in panels.get("sections", []) if item.get("status") != "accepted"]
    return actions or ["run final acceptance audit"]


def _html(model: dict[str, Any], panels: dict[str, Any]) -> str:
    rows = "\n".join(
        f"<tr><td>{html.escape(item['title'])}</td><td>{html.escape(item['status'])}</td><td>{html.escape(item['next_action'])}</td></tr>"
        for item in panels.get("sections", [])
    )
    actions = "\n".join(f"<li>{html.escape(action)}</li>" for action in model.get("next_actions", []))
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>V2.70 维护者首页</title></head>
<body>
<h1>维护者首页与状态面板</h1>
<p>状态来自 persisted artifacts；非 accepted 状态不会被隐藏。</p>
<table><thead><tr><th>面板</th><th>状态</th><th>下一步</th></tr></thead><tbody>{rows}</tbody></table>
<h2>下一步</h2>
<ul>{actions}</ul>
</body>
</html>
"""


def _bundle(workspace_id: str, codebase_id: str, model: dict[str, Any], panels: dict[str, Any], html_text: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.63-70",
        "artifact_type": "maintainer_home_status_dashboard",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "maintainer_home_model": model,
        "maintainer_status_panels": panels,
        "maintainer_home_html": html_text,
        "summary": dict(panels.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(model.get("warnings") or []),
        "unresolved": list(model.get("unresolved") or []),
        "next_actions": ["knowledge_code_external_e2e_portal_delivery_dashboard_read"],
    }
