"""Interactive maintainer console artifacts for V2.74."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..external_e2e_portal_delivery.persistence import read_maintainer_dashboard_panels
from ..registry import CodebaseRegistry
from .persistence import (
    interactive_console_artifact_refs,
    read_acceptance_state,
    read_ci_matrix,
    read_console_model,
    read_console_status_panels,
    read_maintainer_console_html,
    read_navigation_model,
    read_project_binding_closure,
    read_release_manifest,
    write_interactive_console,
)
from .shared import base_artifact, redaction_findings, worst_status


PHASE = "V2.74"


class InteractiveMaintainerConsoleService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_interactive_console(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = interactive_console_artifact_refs(codebase_id)
        sources = {
            "external_closure": _try_read(lambda: read_project_binding_closure(self.workspace, codebase_id)),
            "ci_governance": _try_read(lambda: read_ci_matrix(self.workspace, codebase_id)),
            "agent_memory": _try_read(lambda: read_acceptance_state(self.workspace, codebase_id)),
            "maintainer_dashboard": _try_read(lambda: read_maintainer_dashboard_panels(self.workspace, codebase_id)),
            "release_restore": _try_read(lambda: read_release_manifest(self.workspace, codebase_id)),
        }
        evidence_refs = _evidence_refs(sources)
        panels = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="status_panels", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs)
        panels["sections"] = [_panel(name, source) for name, source in sources.items()]
        panels["summary"] = {"panel_count": len(panels["sections"]), "non_accepted_panel_count": sum(1 for item in panels["sections"] if item["status"] != "accepted")}
        navigation = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="navigation_model", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs)
        navigation["items"] = [{"panel_id": item["id"], "label": item["title"], "status": item["status"]} for item in panels["sections"]]
        model = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="console_model", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs, next_actions=["knowledge_code_agent_memory_release_console_read"])
        model["stage_status"] = worst_status([item["status"] for item in panels["sections"]])
        model["user_visible_goal"] = "一页看到状态、风险、证据、下一步和出门条件"
        model["next_actions"] = [item["next_action"] for item in panels["sections"] if item["status"] != "accepted"] or ["run final acceptance audit"]
        html_text = _html(model, panels)
        unresolved = redaction_findings(model) + redaction_findings(navigation) + redaction_findings(panels) + redaction_findings(html_text)
        if unresolved:
            model["unresolved"].extend(unresolved)
        write_interactive_console(self.workspace, codebase_id, model, navigation, panels, html_text)
        return _bundle(self.workspace_id, codebase_id, model, navigation, panels, html_text, refs)

    def read_interactive_console(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = interactive_console_artifact_refs(codebase_id)
        return _bundle(self.workspace_id, codebase_id, read_console_model(self.workspace, codebase_id), read_navigation_model(self.workspace, codebase_id), read_console_status_panels(self.workspace, codebase_id), read_maintainer_console_html(self.workspace, codebase_id), refs)


def public_interactive_console_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "interactive_maintainer_console",
        "console_model": payload.get("console_model") or {},
        "navigation_model": payload.get("navigation_model") or {},
        "status_panels": payload.get("status_panels") or {},
        "maintainer_console_html": {"format": "html", "content": payload.get("maintainer_console_html") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _try_read(reader) -> dict[str, Any]:
    try:
        return reader()
    except FileNotFoundError:
        return {}


def _evidence_refs(sources: dict[str, dict[str, Any]]) -> list[Any]:
    refs: list[Any] = []
    for source in sources.values():
        refs.extend(source.get("artifact_refs") or [])
        refs.extend(source.get("evidence_refs") or [])
    return refs


def _source_status(source: dict[str, Any]) -> str:
    if not source:
        return "needs_review"
    if source.get("status") in {"accepted", "needs_review", "structured_unavailable", "structured_blocker"}:
        return str(source["status"])
    if source.get("overall_status"):
        return str(source["overall_status"])
    if source.get("summary", {}).get("unavailable_accepted_count", 0) == 0 and source.get("summary", {}).get("accepted_count", 0):
        return "structured_unavailable" if source.get("summary", {}).get("structured_unavailable_count", 0) else "accepted"
    if source.get("sections"):
        return worst_status([str(item.get("status") or "needs_review") for item in source["sections"]])
    return "needs_review"


def _panel(name: str, source: dict[str, Any]) -> dict[str, Any]:
    status = _source_status(source)
    title = name.replace("_", " ").title()
    unresolved = [] if status == "accepted" else [{"kind": status, "reason": f"{title} is {status}", "next_action": "build or review source artifact"}]
    return {
        "id": name,
        "title": title,
        "status": status,
        "artifact_refs": source.get("artifact_refs") or [],
        "evidence_refs": source.get("evidence_refs") or source.get("artifact_refs") or [],
        "unresolved": unresolved,
        "next_action": "none" if status == "accepted" else "build or review source artifact",
    }


def _html(model: dict[str, Any], panels: dict[str, Any]) -> str:
    rows = "\n".join(f"<tr><td>{html.escape(item['title'])}</td><td>{html.escape(item['status'])}</td><td>{html.escape(item['next_action'])}</td></tr>" for item in panels.get("sections", []))
    actions = "\n".join(f"<li>{html.escape(action)}</li>" for action in model.get("next_actions", []))
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>V2.74 维护者控制台</title></head>
<body>
<h1>V2.74 交互式维护者控制台</h1>
<p>状态来自 persisted artifacts；needs_review、structured_unavailable、structured_blocker 不会被隐藏。</p>
<table><thead><tr><th>面板</th><th>状态</th><th>下一步</th></tr></thead><tbody>{rows}</tbody></table>
<h2>下一步</h2><ul>{actions}</ul>
</body></html>"""


def _bundle(workspace_id: str, codebase_id: str, model: dict[str, Any], navigation: dict[str, Any], panels: dict[str, Any], html_text: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.71-75",
        "artifact_type": "interactive_maintainer_console",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "console_model": model,
        "navigation_model": navigation,
        "status_panels": panels,
        "maintainer_console_html": html_text,
        "summary": {"panel_count": panels.get("summary", {}).get("panel_count", 0), "stage_status": model.get("stage_status")},
        "artifact_refs": refs,
        "warnings": list(model.get("warnings") or []),
        "unresolved": list(model.get("unresolved") or []),
        "next_actions": ["knowledge_code_agent_memory_release_console_read"],
    }

