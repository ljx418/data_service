"""V2.54 Human Portal Deepening."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..agent_productization.persistence import (
    closure_artifact_refs,
    governance_artifact_refs,
    human_portal_artifact_refs,
    portal_html_path,
    portal_model_path,
    portal_svg_path,
    profile_onboarding_artifact_refs,
    read_portal_html,
    read_portal_model,
    read_portal_svg,
    read_profile_draft,
)
from ..registry import CodebaseRegistry
from .persistence import (
    human_portal_deepening_artifact_refs,
    read_chart_audit,
    read_portal_v2_html,
    read_project_story,
    read_reading_path,
    read_risk_priority,
    write_human_portal_deepening,
)
from .shared import HUMAN_AGENT_DEEPENING_SCHEMA_VERSION, base_artifact, needs_review, redaction_findings, structured_unavailable


class HumanPortalDeepeningService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_portal(self, codebase_id: str) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        generated_at = now()
        refs = human_portal_deepening_artifact_refs(codebase_id)
        inputs = _read_inputs(self.workspace, codebase_id)
        evidence_refs = _input_evidence_refs(codebase_id, inputs)
        unresolved = _input_unresolved(inputs)
        warnings = _input_warnings(inputs)
        project_story = _project_story(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            generated_at=generated_at,
            refs=refs,
            evidence_refs=evidence_refs,
            warnings=warnings,
            unresolved=unresolved,
            asset_name=asset.name,
            asset_status=asset.status,
            inputs=inputs,
        )
        risk_priority = _risk_priority(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            generated_at=generated_at,
            refs=refs,
            evidence_refs=evidence_refs,
            warnings=warnings,
            unresolved=unresolved,
            inputs=inputs,
        )
        reading_path = _reading_path(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            generated_at=generated_at,
            refs=refs,
            evidence_refs=evidence_refs,
            warnings=warnings,
            unresolved=unresolved,
            inputs=inputs,
        )
        chart_audit = _chart_audit(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            generated_at=generated_at,
            refs=refs,
            evidence_refs=evidence_refs,
            warnings=warnings,
            unresolved=unresolved,
            inputs=inputs,
        )
        html = _render_html(project_story, risk_priority, reading_path, chart_audit)
        public_probe = {
            "project_story": project_story,
            "risk_priority": risk_priority,
            "reading_path": reading_path,
            "chart_audit": chart_audit,
            "html": html,
        }
        redaction = redaction_findings(public_probe)
        if redaction:
            for artifact in (project_story, risk_priority, reading_path, chart_audit):
                artifact["unresolved"].extend(redaction)
        write_human_portal_deepening(self.workspace, codebase_id, project_story, risk_priority, reading_path, chart_audit, html)
        return _bundle(self.workspace_id, codebase_id, project_story, risk_priority, reading_path, chart_audit, html, refs)

    def read_portal(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = human_portal_deepening_artifact_refs(codebase_id)
        project_story = read_project_story(self.workspace, codebase_id)
        risk_priority = read_risk_priority(self.workspace, codebase_id)
        reading_path = read_reading_path(self.workspace, codebase_id)
        chart_audit = read_chart_audit(self.workspace, codebase_id)
        html = read_portal_v2_html(self.workspace, codebase_id)
        return _bundle(self.workspace_id, codebase_id, project_story, risk_priority, reading_path, chart_audit, html, refs)


def public_human_portal_deepening_payload(payload: dict[str, Any], *, include_html: bool = True) -> dict[str, Any]:
    return {
        "schema_version": HUMAN_AGENT_DEEPENING_SCHEMA_VERSION,
        "artifact_type": "human_portal_deepening",
        "project_story": payload.get("project_story") or {},
        "risk_priority": payload.get("risk_priority") or {},
        "reading_path": payload.get("reading_path") or {},
        "chart_audit": payload.get("chart_audit") or {},
        "html": {"content_type": "text/html", "content": payload.get("html", "") if include_html else ""},
        "summary": dict(payload.get("summary") or {}),
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
        "next_actions": list(payload.get("next_actions") or []),
    }


def _bundle(workspace_id: str, codebase_id: str, project_story: dict[str, Any], risk_priority: dict[str, Any], reading_path: dict[str, Any], chart_audit: dict[str, Any], html: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    warnings = _merge_lists(project_story.get("warnings"), risk_priority.get("warnings"), reading_path.get("warnings"), chart_audit.get("warnings"))
    unresolved = _merge_lists(project_story.get("unresolved"), risk_priority.get("unresolved"), reading_path.get("unresolved"), chart_audit.get("unresolved"))
    risks = list(risk_priority.get("risk_items") or [])
    return {
        "schema_version": HUMAN_AGENT_DEEPENING_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "project_story": project_story,
        "risk_priority": risk_priority,
        "reading_path": reading_path,
        "chart_audit": chart_audit,
        "html": html,
        "summary": {
            "risk_count": len(risks),
            "high_risk_count": len([item for item in risks if item.get("severity") == "high"]),
            "reading_path_count": len(reading_path.get("ordered_items") or []),
            "chart_count": len(chart_audit.get("charts") or []),
            "raw_mermaid_visible": bool(chart_audit.get("raw_mermaid_visible")),
            "unresolved_count": len(unresolved),
            "html_contains_portal_v2": "Human Portal V2" in html,
        },
        "artifact_refs": refs,
        "warnings": warnings,
        "unresolved": unresolved,
        "next_actions": ["knowledge_code_human_agent_deepening_portal_read"],
    }


def _read_inputs(workspace: Path, codebase_id: str) -> dict[str, Any]:
    inputs: dict[str, Any] = {}
    inputs["legacy_portal_model"] = _try_read(lambda: read_portal_model(workspace, codebase_id), "agent_productization_portal_model", human_portal_artifact_refs(codebase_id))
    inputs["legacy_portal_svg"] = _try_read(lambda: read_portal_svg(workspace, codebase_id), "agent_productization_portal_svg", human_portal_artifact_refs(codebase_id))
    inputs["legacy_portal_html"] = _try_read(lambda: read_portal_html(workspace, codebase_id), "agent_productization_portal_html", human_portal_artifact_refs(codebase_id))
    inputs["profile_draft"] = _try_read(lambda: read_profile_draft(workspace, codebase_id), "profile_draft", profile_onboarding_artifact_refs(codebase_id))
    inputs["closure_refs"] = {"status": "reference_only", "artifact_refs": closure_artifact_refs(codebase_id)}
    inputs["governance_refs"] = {"status": "reference_only", "artifact_refs": governance_artifact_refs(codebase_id)}
    inputs["portal_paths"] = {
        "model_exists": portal_model_path(workspace, codebase_id).exists(),
        "svg_exists": portal_svg_path(workspace, codebase_id).exists(),
        "html_exists": portal_html_path(workspace, codebase_id).exists(),
    }
    return inputs


def _try_read(reader, input_id: str, artifact_refs: list[dict[str, str]]) -> dict[str, Any]:
    try:
        return {"status": "ready", "input_id": input_id, "data": reader(), "artifact_refs": artifact_refs}
    except FileNotFoundError:
        return {"status": "structured_unavailable", "input_id": input_id, "artifact_refs": artifact_refs, "reason": f"{input_id} is not available"}


def _input_evidence_refs(codebase_id: str, inputs: dict[str, Any]) -> list[dict[str, str]]:
    refs = []
    for item in inputs.values():
        if isinstance(item, dict) and item.get("status") in {"ready", "reference_only"}:
            refs.extend(item.get("artifact_refs") or [])
    return refs or [{"type": "codebase", "artifact_ref": f"codebase://{codebase_id}"}]


def _input_unresolved(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for input_id, item in inputs.items():
        if isinstance(item, dict) and item.get("status") == "structured_unavailable":
            rows.append(structured_unavailable(input_id, str(item.get("reason") or "input artifact unavailable"), evidence_refs=item.get("artifact_refs") or []))
    return rows


def _input_warnings(inputs: dict[str, Any]) -> list[str]:
    return [f"{key}: unavailable" for key, item in inputs.items() if isinstance(item, dict) and item.get("status") == "structured_unavailable"]


def _project_story(*, workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], evidence_refs: list[dict[str, str]], warnings: list[str], unresolved: list[dict[str, Any]], asset_name: str, asset_status: str, inputs: dict[str, Any]) -> dict[str, Any]:
    portal = dict((inputs.get("legacy_portal_model") or {}).get("data") or {})
    sections = list(portal.get("sections") or [])
    project_summary = {
        "project_name": portal.get("project_name") or asset_name or codebase_id,
        "registry_status": asset_status,
        "accepted_baseline": "V2.46-V2.53 Agent Productization and V2.53 Acceptance Infrastructure",
        "section_count": len(sections),
        "chart_node_count": len((portal.get("chart") or {}).get("nodes") or []),
    }
    artifact = base_artifact(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        phase="V2.54",
        artifact_type="human_portal_project_story",
        generated_at=generated_at,
        artifact_refs=refs,
        evidence_refs=evidence_refs,
        warnings=warnings,
        unresolved=unresolved,
    )
    artifact.update(
        {
            "project_summary": project_summary,
            "accepted_baseline": [
                {"phase": "V2.46-V2.53", "status": "accepted_baseline", "evidence_refs": evidence_refs},
                {"phase": "V2.54", "status": "planned_until_accepted", "evidence_refs": refs},
            ],
            "current_limits": [
                "No full design-intent recovery claim.",
                "No full call graph, runtime topology, data/control flow, or type inference claim.",
                "Documentation claims are not code facts.",
            ],
            "next_actions": [
                {"action": "review_high_priority_risks", "reason": "Portal V2 prioritizes unavailable or needs-review inputs", "evidence_refs": evidence_refs},
                {"action": "open_reading_path", "reason": "Use artifact-backed reading order before broad project reading", "evidence_refs": refs},
            ],
        }
    )
    return artifact


def _risk_priority(*, workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], evidence_refs: list[dict[str, str]], warnings: list[str], unresolved: list[dict[str, Any]], inputs: dict[str, Any]) -> dict[str, Any]:
    risks: list[dict[str, Any]] = []
    if unresolved:
        for item in unresolved:
            risks.append(
                {
                    "id": f"risk_{item.get('id')}",
                    "title": f"Input unavailable: {item.get('id')}",
                    "severity": "high",
                    "evidence_refs": item.get("evidence_refs") or [],
                    "recommended_action": "Build or inspect the missing upstream artifact before treating the section as accepted.",
                    "status": item.get("status", "structured_unavailable"),
                }
            )
    portal_html = str((inputs.get("legacy_portal_html") or {}).get("data") or "")
    if "```mermaid" in portal_html or "graph TD" in portal_html:
        risks.append(
            {
                "id": "risk_raw_mermaid_visible",
                "title": "Legacy portal may expose raw Mermaid source",
                "severity": "medium",
                "evidence_refs": human_portal_artifact_refs(codebase_id),
                "recommended_action": "Use rendered Portal V2 chart display and keep raw Mermaid out of final HTML.",
                "status": "needs_review",
            }
        )
    if not risks:
        risks.append(
            {
                "id": "risk_review_acceptance_state",
                "title": "Review acceptance state before extending implementation",
                "severity": "medium",
                "evidence_refs": evidence_refs,
                "recommended_action": "Use V2.52/V2.53 acceptance artifacts as baseline evidence.",
                "status": "accepted_evidence",
            }
        )
    artifact = base_artifact(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        phase="V2.54",
        artifact_type="human_portal_risk_priority",
        generated_at=generated_at,
        artifact_refs=refs,
        evidence_refs=evidence_refs,
        warnings=warnings,
        unresolved=unresolved,
    )
    artifact["risk_items"] = risks
    return artifact


def _reading_path(*, workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], evidence_refs: list[dict[str, str]], warnings: list[str], unresolved: list[dict[str, Any]], inputs: dict[str, Any]) -> dict[str, Any]:
    ordered = []
    for index, ref in enumerate(evidence_refs[:12], start=1):
        ordered.append({"order": index, "artifact_ref": ref.get("artifact_ref"), "type": ref.get("type"), "rationale": "Evidence-backed input for Portal V2 review"})
    if not ordered:
        ordered.append({"order": 1, "artifact_ref": f"codebase://{codebase_id}", "type": "codebase", "rationale": "Fallback codebase registry reference"})
    artifact = base_artifact(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        phase="V2.54",
        artifact_type="human_portal_reading_path",
        generated_at=generated_at,
        artifact_refs=refs,
        evidence_refs=evidence_refs,
        warnings=warnings,
        unresolved=unresolved,
    )
    artifact.update(
        {
            "audience": "maintainer",
            "ordered_items": ordered,
            "omitted_items": [{"reason": "input unavailable", "items": [item["id"] for item in unresolved]}] if unresolved else [],
        }
    )
    return artifact


def _chart_audit(*, workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], evidence_refs: list[dict[str, str]], warnings: list[str], unresolved: list[dict[str, Any]], inputs: dict[str, Any]) -> dict[str, Any]:
    portal_paths = dict(inputs.get("portal_paths") or {})
    portal_html = str((inputs.get("legacy_portal_html") or {}).get("data") or "")
    raw_mermaid_visible = "```mermaid" in portal_html or "graph TD" in portal_html
    quality = "rendered" if portal_paths.get("svg_exists") and not raw_mermaid_visible else "needs_review"
    chart_unresolved = list(unresolved)
    if not portal_paths.get("svg_exists"):
        chart_unresolved.append(structured_unavailable("legacy_portal_svg", "legacy portal SVG is unavailable", evidence_refs=human_portal_artifact_refs(codebase_id)))
    if raw_mermaid_visible:
        chart_unresolved.append(needs_review("raw_mermaid_visible", "legacy portal HTML appears to contain raw Mermaid source", evidence_refs=human_portal_artifact_refs(codebase_id)))
    artifact = base_artifact(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        phase="V2.54",
        artifact_type="human_portal_chart_audit",
        generated_at=generated_at,
        artifact_refs=refs,
        evidence_refs=evidence_refs,
        warnings=warnings,
        unresolved=chart_unresolved,
    )
    artifact.update(
        {
            "charts": [
                {
                    "chart_id": "architecture_overview",
                    "source_artifact": "agent_productization://human_portal/portal_model.json",
                    "rendered_artifact": "agent_productization://human_portal/charts/architecture_overview.svg",
                    "quality_status": quality,
                    "evidence_refs": human_portal_artifact_refs(codebase_id),
                }
            ],
            "raw_mermaid_visible": False,
            "legacy_raw_mermaid_visible": raw_mermaid_visible,
        }
    )
    return artifact


def _render_html(project_story: dict[str, Any], risk_priority: dict[str, Any], reading_path: dict[str, Any], chart_audit: dict[str, Any]) -> str:
    project = escape(str((project_story.get("project_summary") or {}).get("project_name") or project_story.get("codebase_id") or "Project"))
    risks = "".join(
        f"<li><strong>{escape(str(item.get('severity')))}</strong> {escape(str(item.get('title')))} <span>{escape(str(item.get('status')))}</span></li>"
        for item in risk_priority.get("risk_items", [])
    )
    path_items = "".join(
        f"<li>{escape(str(item.get('artifact_ref')))} <em>{escape(str(item.get('rationale')))}</em></li>"
        for item in reading_path.get("ordered_items", [])
    )
    unresolved = _merge_lists(project_story.get("unresolved"), risk_priority.get("unresolved"), reading_path.get("unresolved"), chart_audit.get("unresolved"))
    unresolved_items = "".join(f"<li>{escape(str(item.get('status')))}: {escape(str(item.get('reason') or item.get('id')))}</li>" for item in unresolved)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Human Portal V2 - {project}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 32px; color: #111827; background: #f8fafc; }}
    main {{ max-width: 1120px; margin: 0 auto; }}
    section {{ background: #ffffff; border: 1px solid #cbd5e1; border-radius: 8px; padding: 20px; margin: 18px 0; }}
    h1, h2 {{ margin-top: 0; }}
    .meta {{ color: #475569; }}
    li {{ margin: 8px 0; }}
  </style>
</head>
<body>
<main>
  <h1>Human Portal V2 - {project}</h1>
  <p class="meta">Evidence-first project story, risk priority, reading path, and chart audit.</p>
  <section><h2>Project Story</h2><p>{escape(str((project_story.get('project_summary') or {}).get('accepted_baseline') or 'V2.46-V2.53 accepted baseline'))}</p></section>
  <section><h2>Risk Priority</h2><ul>{risks}</ul></section>
  <section><h2>Reading Path</h2><ol>{path_items}</ol></section>
  <section><h2>Chart Audit</h2><p>raw_mermaid_visible: {escape(str(chart_audit.get('raw_mermaid_visible')))}</p></section>
  <section><h2>Warnings and Unresolved</h2><ul>{unresolved_items}</ul></section>
</main>
</body>
</html>"""


def _merge_lists(*values: Any) -> list[Any]:
    merged: list[Any] = []
    seen: set[str] = set()
    for value in values:
        for item in list(value or []):
            key = repr(item)
            if key not in seen:
                seen.add(key)
                merged.append(item)
    return merged
