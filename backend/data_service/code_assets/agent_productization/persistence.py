"""Persistence helpers for V2.46 Agent Productization artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir
from ..artifacts import read_jsonl, write_jsonl


def agent_productization_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "agent_productization"


def mcp_usage_guide_path(workspace: Path, codebase_id: str) -> Path:
    return agent_productization_dir(workspace, codebase_id) / "mcp_usage_guide.json"


def mcp_tool_catalog_readable_path(workspace: Path, codebase_id: str) -> Path:
    return agent_productization_dir(workspace, codebase_id) / "mcp_tool_catalog_readable.json"


def mcp_agent_workflows_path(workspace: Path, codebase_id: str) -> Path:
    return agent_productization_dir(workspace, codebase_id) / "mcp_agent_workflows.json"


def codex_mcp_usage_guide_path(workspace: Path, codebase_id: str) -> Path:
    return agent_productization_dir(workspace, codebase_id) / "docs" / "generated" / "codex_mcp_usage_guide.md"


def profile_onboarding_dir(workspace: Path, codebase_id: str) -> Path:
    return agent_productization_dir(workspace, codebase_id) / "profile_onboarding"


def profile_draft_path(workspace: Path, codebase_id: str) -> Path:
    return profile_onboarding_dir(workspace, codebase_id) / "profile_draft.json"


def taxonomy_suggestions_path(workspace: Path, codebase_id: str) -> Path:
    return profile_onboarding_dir(workspace, codebase_id) / "taxonomy_suggestions.json"


def authority_rule_suggestions_path(workspace: Path, codebase_id: str) -> Path:
    return profile_onboarding_dir(workspace, codebase_id) / "authority_rule_suggestions.json"


def path_pattern_suggestions_path(workspace: Path, codebase_id: str) -> Path:
    return profile_onboarding_dir(workspace, codebase_id) / "path_pattern_suggestions.json"


def no_hardcode_audit_path(workspace: Path, codebase_id: str) -> Path:
    return profile_onboarding_dir(workspace, codebase_id) / "no_hardcode_audit.json"


def human_portal_dir(workspace: Path, codebase_id: str) -> Path:
    return agent_productization_dir(workspace, codebase_id) / "human_portal"


def portal_model_path(workspace: Path, codebase_id: str) -> Path:
    return human_portal_dir(workspace, codebase_id) / "portal_model.json"


def portal_svg_path(workspace: Path, codebase_id: str) -> Path:
    return human_portal_dir(workspace, codebase_id) / "charts" / "architecture_overview.svg"


def portal_html_path(workspace: Path, codebase_id: str) -> Path:
    return human_portal_dir(workspace, codebase_id) / "project_architecture_portal.html"


def task_navigation_dir(workspace: Path, codebase_id: str, task_id: str) -> Path:
    return agent_productization_dir(workspace, codebase_id) / "task_navigation" / task_id


def governance_dir(workspace: Path, codebase_id: str) -> Path:
    return agent_productization_dir(workspace, codebase_id) / "governance"


def governance_feedback_path(workspace: Path, codebase_id: str) -> Path:
    return governance_dir(workspace, codebase_id) / "feedback.jsonl"


def governance_rules_path(workspace: Path, codebase_id: str) -> Path:
    return governance_dir(workspace, codebase_id) / "rules.jsonl"


def governance_overlay_path(workspace: Path, codebase_id: str) -> Path:
    return governance_dir(workspace, codebase_id) / "applied_overlay.json"


def playbooks_dir(workspace: Path, codebase_id: str) -> Path:
    return agent_productization_dir(workspace, codebase_id) / "playbooks"


def playbook_json_path(workspace: Path, codebase_id: str, role: str) -> Path:
    return playbooks_dir(workspace, codebase_id) / f"{role}.json"


def playbook_markdown_path(workspace: Path, codebase_id: str, role: str) -> Path:
    return playbooks_dir(workspace, codebase_id) / f"{role}.md"


def closure_dir(workspace: Path, codebase_id: str) -> Path:
    return agent_productization_dir(workspace, codebase_id) / "closure"


def real_repo_matrix_path(workspace: Path, codebase_id: str) -> Path:
    return closure_dir(workspace, codebase_id) / "real_repo_matrix.json"


def public_contract_parity_path(workspace: Path, codebase_id: str) -> Path:
    return closure_dir(workspace, codebase_id) / "public_contract_parity.json"


def redaction_audit_path(workspace: Path, codebase_id: str) -> Path:
    return closure_dir(workspace, codebase_id) / "redaction_audit.json"


def closure_audit_report_path(workspace: Path, codebase_id: str) -> Path:
    return closure_dir(workspace, codebase_id) / "closure_audit_report.md"


def task_reading_order_path(workspace: Path, codebase_id: str, task_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id, task_id) / "reading_order.json"


def task_impact_path(workspace: Path, codebase_id: str, task_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id, task_id) / "task_impact.json"


def suggested_tests_path(workspace: Path, codebase_id: str, task_id: str) -> Path:
    return task_navigation_dir(workspace, codebase_id, task_id) / "suggested_tests.json"


def mcp_productization_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "mcp_usage_guide", "artifact_ref": f"agent_productization://{codebase_id}/mcp_usage_guide.json"},
        {"type": "mcp_tool_catalog_readable", "artifact_ref": f"agent_productization://{codebase_id}/mcp_tool_catalog_readable.json"},
        {"type": "mcp_agent_workflows", "artifact_ref": f"agent_productization://{codebase_id}/mcp_agent_workflows.json"},
        {"type": "codex_mcp_usage_guide", "artifact_ref": f"agent_productization://{codebase_id}/docs/generated/codex_mcp_usage_guide.md"},
    ]


def profile_onboarding_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "profile_draft", "artifact_ref": f"agent_productization://{codebase_id}/profile_onboarding/profile_draft.json"},
        {"type": "taxonomy_suggestions", "artifact_ref": f"agent_productization://{codebase_id}/profile_onboarding/taxonomy_suggestions.json"},
        {"type": "authority_rule_suggestions", "artifact_ref": f"agent_productization://{codebase_id}/profile_onboarding/authority_rule_suggestions.json"},
        {"type": "path_pattern_suggestions", "artifact_ref": f"agent_productization://{codebase_id}/profile_onboarding/path_pattern_suggestions.json"},
        {"type": "no_hardcode_audit", "artifact_ref": f"agent_productization://{codebase_id}/profile_onboarding/no_hardcode_audit.json"},
    ]


def human_portal_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "portal_model", "artifact_ref": f"agent_productization://{codebase_id}/human_portal/portal_model.json"},
        {"type": "architecture_overview_svg", "artifact_ref": f"agent_productization://{codebase_id}/human_portal/charts/architecture_overview.svg"},
        {"type": "project_architecture_portal_html", "artifact_ref": f"agent_productization://{codebase_id}/human_portal/project_architecture_portal.html"},
    ]


def task_navigation_artifact_refs(codebase_id: str, task_id: str) -> list[dict[str, str]]:
    return [
        {"type": "reading_order", "artifact_ref": f"agent_productization://{codebase_id}/task_navigation/{task_id}/reading_order.json"},
        {"type": "task_impact", "artifact_ref": f"agent_productization://{codebase_id}/task_navigation/{task_id}/task_impact.json"},
        {"type": "suggested_tests", "artifact_ref": f"agent_productization://{codebase_id}/task_navigation/{task_id}/suggested_tests.json"},
    ]


def governance_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "agent_productization_governance_feedback", "artifact_ref": f"agent_productization://{codebase_id}/governance/feedback.jsonl"},
        {"type": "agent_productization_governance_rules", "artifact_ref": f"agent_productization://{codebase_id}/governance/rules.jsonl"},
        {"type": "agent_productization_governance_overlay", "artifact_ref": f"agent_productization://{codebase_id}/governance/applied_overlay.json"},
    ]


def playbook_artifact_refs(codebase_id: str, role: str | None = None) -> list[dict[str, str]]:
    roles = [role] if role else ["maintainer", "coding_agent", "documentation_agent", "architecture_reviewer"]
    refs = []
    for item in roles:
        refs.append({"type": f"agent_productization_playbook_{item}_json", "artifact_ref": f"agent_productization://{codebase_id}/playbooks/{item}.json"})
        refs.append({"type": f"agent_productization_playbook_{item}_markdown", "artifact_ref": f"agent_productization://{codebase_id}/playbooks/{item}.md"})
    return refs


def closure_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "agent_productization_real_repo_matrix", "artifact_ref": f"agent_productization://{codebase_id}/closure/real_repo_matrix.json"},
        {"type": "agent_productization_public_contract_parity", "artifact_ref": f"agent_productization://{codebase_id}/closure/public_contract_parity.json"},
        {"type": "agent_productization_redaction_audit", "artifact_ref": f"agent_productization://{codebase_id}/closure/redaction_audit.json"},
        {"type": "agent_productization_closure_audit_report", "artifact_ref": f"agent_productization://{codebase_id}/closure/closure_audit_report.md"},
    ]


def write_mcp_productization(
    workspace: Path,
    codebase_id: str,
    usage_guide: dict[str, Any],
    catalog: dict[str, Any],
    workflows: dict[str, Any],
    markdown: str,
) -> None:
    write_json(mcp_usage_guide_path(workspace, codebase_id), usage_guide)
    write_json(mcp_tool_catalog_readable_path(workspace, codebase_id), catalog)
    write_json(mcp_agent_workflows_path(workspace, codebase_id), workflows)
    guide_path = codex_mcp_usage_guide_path(workspace, codebase_id)
    guide_path.parent.mkdir(parents=True, exist_ok=True)
    guide_path.write_text(markdown, encoding="utf-8")


def write_profile_onboarding(
    workspace: Path,
    codebase_id: str,
    profile_draft: dict[str, Any],
    taxonomy_suggestions: dict[str, Any],
    authority_rule_suggestions: dict[str, Any],
    path_pattern_suggestions: dict[str, Any],
    no_hardcode_audit: dict[str, Any],
) -> None:
    write_json(profile_draft_path(workspace, codebase_id), profile_draft)
    write_json(taxonomy_suggestions_path(workspace, codebase_id), taxonomy_suggestions)
    write_json(authority_rule_suggestions_path(workspace, codebase_id), authority_rule_suggestions)
    write_json(path_pattern_suggestions_path(workspace, codebase_id), path_pattern_suggestions)
    write_json(no_hardcode_audit_path(workspace, codebase_id), no_hardcode_audit)


def write_human_portal(
    workspace: Path,
    codebase_id: str,
    portal_model: dict[str, Any],
    svg: str,
    html: str,
) -> None:
    write_json(portal_model_path(workspace, codebase_id), portal_model)
    svg_path = portal_svg_path(workspace, codebase_id)
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.write_text(svg, encoding="utf-8")
    html_path = portal_html_path(workspace, codebase_id)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(html, encoding="utf-8")


def write_task_navigation(
    workspace: Path,
    codebase_id: str,
    task_id: str,
    reading_order: dict[str, Any],
    task_impact: dict[str, Any],
    suggested_tests: dict[str, Any],
) -> None:
    write_json(task_reading_order_path(workspace, codebase_id, task_id), reading_order)
    write_json(task_impact_path(workspace, codebase_id, task_id), task_impact)
    write_json(suggested_tests_path(workspace, codebase_id, task_id), suggested_tests)


def write_governance_feedback(workspace: Path, codebase_id: str, rows: list[dict[str, Any]]) -> None:
    write_jsonl(governance_feedback_path(workspace, codebase_id), rows)


def read_governance_feedback(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    return read_jsonl(governance_feedback_path(workspace, codebase_id))


def write_governance_rules(workspace: Path, codebase_id: str, rows: list[dict[str, Any]]) -> None:
    write_jsonl(governance_rules_path(workspace, codebase_id), rows)


def read_governance_rules(workspace: Path, codebase_id: str) -> list[dict[str, Any]]:
    return read_jsonl(governance_rules_path(workspace, codebase_id))


def write_governance_overlay(workspace: Path, codebase_id: str, payload: dict[str, Any]) -> None:
    write_json(governance_overlay_path(workspace, codebase_id), payload)


def read_governance_overlay(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(governance_overlay_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("AGENT_PRODUCTIZATION_GOVERNANCE_OVERLAY_NOT_BUILT")
    return payload


def write_playbook(workspace: Path, codebase_id: str, role: str, payload: dict[str, Any], markdown: str) -> None:
    write_json(playbook_json_path(workspace, codebase_id, role), payload)
    md_path = playbook_markdown_path(workspace, codebase_id, role)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(markdown, encoding="utf-8")


def read_playbook_json(workspace: Path, codebase_id: str, role: str) -> dict[str, Any]:
    payload = read_json(playbook_json_path(workspace, codebase_id, role), None)
    if not payload:
        raise FileNotFoundError("AGENT_PRODUCTIZATION_PLAYBOOK_NOT_BUILT")
    return payload


def read_playbook_markdown(workspace: Path, codebase_id: str, role: str) -> str:
    path = playbook_markdown_path(workspace, codebase_id, role)
    if not path.exists():
        raise FileNotFoundError("AGENT_PRODUCTIZATION_PLAYBOOK_NOT_BUILT")
    return path.read_text(encoding="utf-8")


def write_closure(
    workspace: Path,
    codebase_id: str,
    real_repo_matrix: dict[str, Any],
    public_contract_parity: dict[str, Any],
    redaction_audit: dict[str, Any],
    closure_report: str,
) -> None:
    write_json(real_repo_matrix_path(workspace, codebase_id), real_repo_matrix)
    write_json(public_contract_parity_path(workspace, codebase_id), public_contract_parity)
    write_json(redaction_audit_path(workspace, codebase_id), redaction_audit)
    report_path = closure_audit_report_path(workspace, codebase_id)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(closure_report, encoding="utf-8")


def read_real_repo_matrix(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(real_repo_matrix_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("AGENT_PRODUCTIZATION_CLOSURE_NOT_BUILT")
    return payload


def read_public_contract_parity(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(public_contract_parity_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("AGENT_PRODUCTIZATION_CLOSURE_NOT_BUILT")
    return payload


def read_redaction_audit(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(redaction_audit_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("AGENT_PRODUCTIZATION_CLOSURE_NOT_BUILT")
    return payload


def read_closure_audit_report(workspace: Path, codebase_id: str) -> str:
    path = closure_audit_report_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("AGENT_PRODUCTIZATION_CLOSURE_NOT_BUILT")
    return path.read_text(encoding="utf-8")


def read_mcp_usage_guide(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(mcp_usage_guide_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("MCP_PRODUCTIZATION_NOT_BUILT")
    return payload


def read_mcp_tool_catalog(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(mcp_tool_catalog_readable_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("MCP_PRODUCTIZATION_NOT_BUILT")
    return payload


def read_mcp_agent_workflows(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(mcp_agent_workflows_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("MCP_PRODUCTIZATION_NOT_BUILT")
    return payload


def read_codex_mcp_usage_guide(workspace: Path, codebase_id: str) -> str:
    path = codex_mcp_usage_guide_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("MCP_PRODUCTIZATION_NOT_BUILT")
    return path.read_text(encoding="utf-8")


def read_profile_draft(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(profile_draft_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("PROJECT_PROFILE_ONBOARDING_NOT_BUILT")
    return payload


def read_taxonomy_suggestions(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(taxonomy_suggestions_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("PROJECT_PROFILE_ONBOARDING_NOT_BUILT")
    return payload


def read_authority_rule_suggestions(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(authority_rule_suggestions_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("PROJECT_PROFILE_ONBOARDING_NOT_BUILT")
    return payload


def read_path_pattern_suggestions(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(path_pattern_suggestions_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("PROJECT_PROFILE_ONBOARDING_NOT_BUILT")
    return payload


def read_no_hardcode_audit(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(no_hardcode_audit_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("PROJECT_PROFILE_ONBOARDING_NOT_BUILT")
    return payload


def read_portal_model(workspace: Path, codebase_id: str) -> dict[str, Any]:
    payload = read_json(portal_model_path(workspace, codebase_id), None)
    if not payload:
        raise FileNotFoundError("HUMAN_PORTAL_NOT_BUILT")
    return payload


def read_portal_svg(workspace: Path, codebase_id: str) -> str:
    path = portal_svg_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("HUMAN_PORTAL_NOT_BUILT")
    return path.read_text(encoding="utf-8")


def read_portal_html(workspace: Path, codebase_id: str) -> str:
    path = portal_html_path(workspace, codebase_id)
    if not path.exists():
        raise FileNotFoundError("HUMAN_PORTAL_NOT_BUILT")
    return path.read_text(encoding="utf-8")


def read_task_reading_order(workspace: Path, codebase_id: str, task_id: str) -> dict[str, Any]:
    payload = read_json(task_reading_order_path(workspace, codebase_id, task_id), None)
    if not payload:
        raise FileNotFoundError("TASK_NAVIGATION_NOT_BUILT")
    return payload


def read_task_impact(workspace: Path, codebase_id: str, task_id: str) -> dict[str, Any]:
    payload = read_json(task_impact_path(workspace, codebase_id, task_id), None)
    if not payload:
        raise FileNotFoundError("TASK_NAVIGATION_NOT_BUILT")
    return payload


def read_suggested_tests(workspace: Path, codebase_id: str, task_id: str) -> dict[str, Any]:
    payload = read_json(suggested_tests_path(workspace, codebase_id, task_id), None)
    if not payload:
        raise FileNotFoundError("TASK_NAVIGATION_NOT_BUILT")
    return payload
