"""Human-readable architecture portal for V2.48 Agent Productization."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .mcp_usage import AGENT_PRODUCTIZATION_SCHEMA_VERSION
from .persistence import (
    human_portal_artifact_refs,
    mcp_productization_artifact_refs,
    profile_onboarding_artifact_refs,
    read_mcp_agent_workflows,
    read_mcp_usage_guide,
    read_no_hardcode_audit,
    read_portal_html,
    read_portal_model,
    read_portal_svg,
    read_profile_draft,
    read_taxonomy_suggestions,
    write_human_portal,
)


class AgentHumanPortalService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_portal(self, codebase_id: str) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        refs = human_portal_artifact_refs(codebase_id)
        mcp = _read_mcp_bundle(self.workspace, codebase_id)
        profile = _read_profile_bundle(self.workspace, codebase_id)
        model = _portal_model(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            project_name=asset.name,
            asset_status=asset.status,
            mcp=mcp,
            profile=profile,
            refs=refs,
        )
        svg = _render_svg(model)
        html = _render_html(model, svg)
        write_human_portal(self.workspace, codebase_id, model, svg, html)
        return _bundle(self.workspace_id, codebase_id, model, svg, html, refs)

    def read_portal(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = human_portal_artifact_refs(codebase_id)
        model = read_portal_model(self.workspace, codebase_id)
        svg = read_portal_svg(self.workspace, codebase_id)
        html = read_portal_html(self.workspace, codebase_id)
        return _bundle(self.workspace_id, codebase_id, model, svg, html, refs)


def public_human_portal_payload(payload: dict[str, Any], *, include_html: bool = True) -> dict[str, Any]:
    model = dict(payload.get("portal_model") or {})
    html = payload.get("html", "") if include_html else ""
    svg = payload.get("svg", "") if include_html else ""
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "artifact_type": "human_architecture_portal",
        "portal_model": model,
        "html": {"content_type": "text/html", "content": html},
        "svg": {"content_type": "image/svg+xml", "content": svg},
        "summary": dict(payload.get("summary") or {}),
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _bundle(workspace_id: str, codebase_id: str, model: dict[str, Any], svg: str, html: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    unresolved = list(model.get("blockers") or [])
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "portal_model": model,
        "svg": svg,
        "html": html,
        "summary": {
            "section_count": len(model.get("sections") or []),
            "chart_node_count": len(model.get("chart", {}).get("nodes", []) or []),
            "blocker_count": len(unresolved),
            "html_contains_svg": "<svg" in html,
            "contains_mermaid_source": "```mermaid" in html or "graph TD" in html,
        },
        "artifact_refs": refs,
        "warnings": [],
        "unresolved": unresolved,
        "next_actions": ["knowledge_code_agent_productization_portal_read"],
    }


def _read_mcp_bundle(workspace: Path, codebase_id: str) -> dict[str, Any]:
    try:
        guide = read_mcp_usage_guide(workspace, codebase_id)
        workflows = read_mcp_agent_workflows(workspace, codebase_id)
    except FileNotFoundError:
        return {
            "status": "structured_blocker",
            "blocker": {"code": "MCP_PRODUCTIZATION_NOT_BUILT", "reason": "build Phase 123 MCP usage artifacts first"},
            "artifact_refs": mcp_productization_artifact_refs(codebase_id),
        }
    return {
        "status": "ready",
        "usage_guide": guide,
        "workflows": workflows,
        "artifact_refs": mcp_productization_artifact_refs(codebase_id),
    }


def _read_profile_bundle(workspace: Path, codebase_id: str) -> dict[str, Any]:
    try:
        profile = read_profile_draft(workspace, codebase_id)
        taxonomy = read_taxonomy_suggestions(workspace, codebase_id)
        audit = read_no_hardcode_audit(workspace, codebase_id)
    except FileNotFoundError:
        return {
            "status": "structured_blocker",
            "blocker": {"code": "PROJECT_PROFILE_ONBOARDING_NOT_BUILT", "reason": "build Phase 124 profile onboarding artifacts first"},
            "artifact_refs": profile_onboarding_artifact_refs(codebase_id),
        }
    return {
        "status": "ready",
        "profile": profile,
        "taxonomy": taxonomy,
        "no_hardcode_audit": audit,
        "artifact_refs": profile_onboarding_artifact_refs(codebase_id),
    }


def _portal_model(
    *,
    workspace_id: str,
    codebase_id: str,
    project_name: str,
    asset_status: str,
    mcp: dict[str, Any],
    profile: dict[str, Any],
    refs: list[dict[str, str]],
) -> dict[str, Any]:
    blockers = []
    if mcp.get("status") != "ready":
        blockers.append(mcp.get("blocker") or {"code": "MCP_PRODUCTIZATION_NOT_BUILT"})
    if profile.get("status") != "ready":
        blockers.append(profile.get("blocker") or {"code": "PROJECT_PROFILE_ONBOARDING_NOT_BUILT"})
    workflows = list((mcp.get("workflows") or {}).get("workflows") or [])
    profile_draft = dict(profile.get("profile") or {})
    taxonomy = dict(profile.get("taxonomy") or {})
    audit = dict(profile.get("no_hardcode_audit") or {})
    sections = [
        {
            "section_id": "project_summary",
            "title": "Project Summary",
            "status": "ready",
            "cards": [
                {"label": "Project", "value": project_name or codebase_id, "artifact_refs": refs},
                {"label": "Registry status", "value": asset_status, "artifact_refs": refs},
            ],
        },
        {
            "section_id": "agent_workflows",
            "title": "Agent Workflows",
            "status": mcp.get("status"),
            "cards": [{"label": item.get("title"), "value": item.get("workflow_id"), "artifact_refs": mcp.get("artifact_refs", [])} for item in workflows],
        },
        {
            "section_id": "profile_onboarding",
            "title": "Profile Onboarding",
            "status": profile.get("status"),
            "cards": [
                {"label": "Profile status", "value": profile_draft.get("profile_status", profile.get("status")), "artifact_refs": profile.get("artifact_refs", [])},
                {"label": "Doc assets", "value": str(len(profile_draft.get("doc_assets") or [])), "artifact_refs": profile.get("artifact_refs", [])},
                {"label": "Taxonomy suggestions", "value": str(len(taxonomy.get("suggestions") or [])), "artifact_refs": profile.get("artifact_refs", [])},
                {"label": "No-hardcode", "value": audit.get("status", "unknown"), "artifact_refs": profile.get("artifact_refs", [])},
            ],
        },
    ]
    nodes = [
        {"node_id": "registry", "label": "Codebase Registry", "status": "ready", "artifact_refs": refs},
        {"node_id": "mcp", "label": "MCP Usage Bundle", "status": mcp.get("status"), "artifact_refs": mcp.get("artifact_refs", [])},
        {"node_id": "profile", "label": "Profile Onboarding", "status": profile.get("status"), "artifact_refs": profile.get("artifact_refs", [])},
        {"node_id": "portal", "label": "Human Portal", "status": "ready", "artifact_refs": refs},
    ]
    edges = [
        {"from": "registry", "to": "mcp", "label": "feeds usage guide"},
        {"from": "registry", "to": "profile", "label": "feeds profile draft"},
        {"from": "mcp", "to": "portal", "label": "renders workflows"},
        {"from": "profile", "to": "portal", "label": "renders profile"},
    ]
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "artifact_type": "human_architecture_portal_model",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "created_at": now(),
        "project_name": project_name or codebase_id,
        "sections": sections,
        "chart": {"chart_id": "architecture_overview", "nodes": nodes, "edges": edges},
        "recommended_next_steps": _recommended_next_steps(blockers),
        "blockers": blockers,
        "artifact_refs": refs,
    }


def _recommended_next_steps(blockers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not blockers:
        return [
            {"action": "open_portal", "reason": "Human portal is ready for project reading", "evidence_refs": ["agent_productization://human_portal"]},
            {"action": "prepare_task_context", "reason": "Use task navigation before broad code reading", "needs_review": True},
        ]
    return [{"action": "resolve_blocker", "reason": blocker.get("reason", blocker.get("code", "blocked")), "needs_review": True} for blocker in blockers]


def _render_svg(model: dict[str, Any]) -> str:
    nodes = list(model.get("chart", {}).get("nodes") or [])
    edges = list(model.get("chart", {}).get("edges") or [])
    positions = {node["node_id"]: (80 + index * 210, 90) for index, node in enumerate(nodes)}
    width = max(860, 180 + len(nodes) * 210)
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="260" viewBox="0 0 {width} 260" role="img" aria-label="Architecture overview">',
        '<rect x="0" y="0" width="100%" height="100%" fill="#f8fafc"/>',
        '<text x="32" y="36" font-family="Arial" font-size="20" font-weight="700" fill="#0f172a">Human Architecture Portal</text>',
    ]
    for edge in edges:
        start = positions.get(edge.get("from"))
        end = positions.get(edge.get("to"))
        if not start or not end:
            continue
        x1, y1 = start
        x2, y2 = end
        lines.append(f'<line x1="{x1 + 150}" y1="{y1 + 35}" x2="{x2}" y2="{y2 + 35}" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>')
        lines.append(f'<text x="{(x1 + x2) / 2 + 40:.0f}" y="{y1 + 28}" font-family="Arial" font-size="11" fill="#475569">{escape(str(edge.get("label") or ""))}</text>')
    lines.append('<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#64748b"/></marker></defs>')
    for node in nodes:
        x, y = positions[node["node_id"]]
        status = str(node.get("status") or "unknown")
        color = "#dcfce7" if status == "ready" else "#fef3c7"
        border = "#16a34a" if status == "ready" else "#d97706"
        lines.append(f'<rect x="{x}" y="{y}" width="150" height="70" rx="8" fill="{color}" stroke="{border}" stroke-width="2"/>')
        lines.append(f'<text x="{x + 12}" y="{y + 30}" font-family="Arial" font-size="13" font-weight="700" fill="#111827">{escape(str(node.get("label") or ""))}</text>')
        lines.append(f'<text x="{x + 12}" y="{y + 52}" font-family="Arial" font-size="12" fill="#334155">status: {escape(status)}</text>')
    lines.append("</svg>")
    return "\n".join(lines)


def _render_html(model: dict[str, Any], svg: str) -> str:
    project = escape(str(model.get("project_name") or model.get("codebase_id") or "Project"))
    section_html = []
    for section in model.get("sections", []):
        cards = []
        for card in section.get("cards", []):
            cards.append(
                "<div class=\"card\">"
                f"<strong>{escape(str(card.get('label') or ''))}</strong>"
                f"<span>{escape(str(card.get('value') or ''))}</span>"
                "</div>"
            )
        section_html.append(
            "<section>"
            f"<h2>{escape(str(section.get('title') or 'Section'))}</h2>"
            f"<p class=\"status\">status: {escape(str(section.get('status') or 'unknown'))}</p>"
            f"<div class=\"grid\">{''.join(cards)}</div>"
            "</section>"
        )
    blockers = "".join(f"<li><code>{escape(str(item.get('code') or 'BLOCKED'))}</code> {escape(str(item.get('reason') or ''))}</li>" for item in model.get("blockers", []))
    if not blockers:
        blockers = "<li>No blockers recorded for rendered portal inputs.</li>"
    steps = "".join(f"<li>{escape(str(item.get('action') or 'next'))}: {escape(str(item.get('reason') or ''))}</li>" for item in model.get("recommended_next_steps", []))
    return "\n".join(
        [
            "<!doctype html>",
            "<html lang=\"zh-CN\">",
            "<head>",
            "<meta charset=\"utf-8\"/>",
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>",
            f"<title>{project} - Human Architecture Portal</title>",
            "<style>",
            "body{font-family:Arial,'PingFang SC',sans-serif;margin:0;background:#f8fafc;color:#0f172a;}main{max-width:1180px;margin:0 auto;padding:32px;}header{padding:28px 0 12px;}h1{font-size:32px;margin:0 0 8px;}h2{font-size:20px;margin:0 0 8px;}section{background:white;border:1px solid #e2e8f0;border-radius:10px;padding:18px;margin:18px 0;} .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}.card{border:1px solid #e5e7eb;border-radius:8px;padding:12px;background:#fff}.card strong{display:block;font-size:12px;color:#475569}.card span{display:block;margin-top:8px;font-size:16px}.status{color:#475569}.chart{overflow:auto;background:white;border:1px solid #e2e8f0;border-radius:10px;padding:12px}code{background:#f1f5f9;padding:2px 5px;border-radius:4px}",
            "</style>",
            "</head>",
            "<body><main>",
            "<header>",
            f"<h1>{project}</h1>",
            "<p>人类项目理解入口：展示 Agent 工作流、profile 草稿、证据状态、结构化 blocker 和下一步阅读路径。</p>",
            "</header>",
            "<div class=\"chart\">",
            svg,
            "</div>",
            *section_html,
            "<section><h2>Needs Review / Blockers</h2><ul>",
            blockers,
            "</ul></section>",
            "<section><h2>Recommended Next Steps</h2><ul>",
            steps,
            "</ul></section>",
            "</main></body></html>",
        ]
    )
