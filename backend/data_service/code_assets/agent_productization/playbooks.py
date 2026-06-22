"""Role-scoped Agent Context Playbooks for V2.51 Agent Productization."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .mcp_usage import AGENT_PRODUCTIZATION_SCHEMA_VERSION
from .persistence import (
    playbook_artifact_refs,
    read_governance_overlay,
    read_mcp_agent_workflows,
    read_portal_model,
    read_profile_draft,
    read_taxonomy_suggestions,
    read_playbook_json,
    read_playbook_markdown,
    write_playbook,
)


PLAYBOOK_ROLES = {"maintainer", "coding_agent", "documentation_agent", "architecture_reviewer"}
DEFAULT_MAX_TOKENS = 4000


class AgentProductizationPlaybookService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_playbooks(self, codebase_id: str, *, role: str | None = None, max_tokens: int = DEFAULT_MAX_TOKENS) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        roles = [_normalize_role(role)] if role else sorted(PLAYBOOK_ROLES)
        built = []
        for item in roles:
            payload = self._build_role_playbook(codebase_id, item, max_tokens=max_tokens)
            markdown = _render_markdown(payload)
            write_playbook(self.workspace, codebase_id, item, payload, markdown)
            built.append({"role": item, "playbook": payload, "markdown": markdown})
        refs = []
        for item in roles:
            refs.extend(playbook_artifact_refs(codebase_id, item))
        return {
            "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
            "artifact_type": "agent_productization_playbook_build_result",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "roles": [item["role"] for item in built],
            "playbooks": [item["playbook"] for item in built],
            "artifact_refs": refs,
            "warnings": [],
            "unresolved": [],
            "next_actions": ["knowledge_code_agent_productization_playbook_read"],
        }

    def read_playbook(self, codebase_id: str, *, role: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        normalized = _normalize_role(role)
        playbook = read_playbook_json(self.workspace, codebase_id, normalized)
        markdown = read_playbook_markdown(self.workspace, codebase_id, normalized)
        return {
            "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
            "artifact_type": "agent_productization_playbook_read_result",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "role": normalized,
            "playbook": playbook,
            "markdown": {"format": "markdown", "content": markdown},
            "artifact_refs": playbook_artifact_refs(codebase_id, normalized),
            "warnings": playbook.get("warnings", []),
            "unresolved": playbook.get("unresolved", []),
            "next_actions": playbook.get("next_actions", []),
        }

    def _build_role_playbook(self, codebase_id: str, role: str, *, max_tokens: int) -> dict[str, Any]:
        source = self._load_sources(codebase_id)
        recommendations = _recommendations_for(role, source)
        recommendations, omitted_items = _apply_budget(recommendations, max_tokens=max_tokens)
        _assert_recommendation_policy(recommendations)
        warnings = list(source["warnings"])
        unresolved = list(source["unresolved"])
        if not recommendations:
            warnings.append("AGENT_PRODUCTIZATION_PLAYBOOK_RECOMMENDATIONS_TRIMMED")
        return {
            "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
            "artifact_type": "agent_productization_role_playbook",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "role": role,
            "playbook_id": _stable_id("playbook", codebase_id, role, max_tokens),
            "title": _role_title(role),
            "target_user": _target_user(role),
            "source_phase_refs": ["123", "124", "125", "126", "127"],
            "recommended_tool_sequence": _tool_sequence(role),
            "recommendations": recommendations,
            "constraints": [
                "Do not treat this playbook as a substitute for evidence-backed code review.",
                "Every recommendation must keep evidence_refs or be marked needs_review.",
                "Relationship and task impact outputs are reading guidance, not full runtime call graph.",
            ],
            "risk_summary": _risk_summary(source),
            "omitted_items": omitted_items,
            "token_budget": {"requested_max_tokens": max_tokens, "estimated_tokens": _estimate_tokens(recommendations)},
            "artifact_refs": playbook_artifact_refs(codebase_id, role),
            "warnings": warnings,
            "unresolved": unresolved,
            "created_at": now(),
        }

    def _load_sources(self, codebase_id: str) -> dict[str, Any]:
        warnings = []
        unresolved = []

        def optional(name: str, reader):
            try:
                return reader(self.workspace, codebase_id)
            except FileNotFoundError as exc:
                unresolved.append({"source": name, "reason": str(exc)})
                return {}

        workflows = optional("mcp_agent_workflows", read_mcp_agent_workflows)
        profile = optional("profile_draft", read_profile_draft)
        taxonomy = optional("taxonomy_suggestions", read_taxonomy_suggestions)
        portal = optional("portal_model", read_portal_model)
        overlay = optional("governance_overlay", read_governance_overlay)
        if unresolved:
            warnings.append("AGENT_PRODUCTIZATION_PLAYBOOK_SOURCE_PARTIAL")
        return {
            "workflows": workflows,
            "profile": profile,
            "taxonomy": taxonomy,
            "portal": portal,
            "overlay": overlay,
            "warnings": warnings,
            "unresolved": unresolved,
        }


def public_playbook_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "artifact_type": "agent_productization_playbook_bundle",
        "roles": payload.get("roles", [payload.get("role")]) if payload.get("roles") or payload.get("role") else [],
        "playbooks": payload.get("playbooks") or ([payload.get("playbook")] if payload.get("playbook") else []),
        "playbook": payload.get("playbook"),
        "markdown": payload.get("markdown"),
        "artifact_refs": payload.get("artifact_refs", []),
        "warnings": payload.get("warnings", []),
        "unresolved": payload.get("unresolved", []),
    }


def _normalize_role(role: str | None) -> str:
    normalized = str(role or "").strip()
    if normalized not in PLAYBOOK_ROLES:
        raise ValueError("INVALID_AGENT_PRODUCTIZATION_PLAYBOOK_ROLE")
    return normalized


def _recommendations_for(role: str, source: dict[str, Any]) -> list[dict[str, Any]]:
    profile_ref = _ref(source["profile"], "profile_draft", "profile_onboarding/profile_draft.json")
    portal_ref = _ref(source["portal"], "portal_model", "human_portal/portal_model.json")
    workflow_ref = _ref(source["workflows"], "mcp_agent_workflows", "mcp_agent_workflows.json")
    overlay_ref = _ref(source["overlay"], "governance_overlay", "governance/applied_overlay.json")
    taxonomy_ref = _ref(source["taxonomy"], "taxonomy_suggestions", "profile_onboarding/taxonomy_suggestions.json")
    shared = [
        _rec("read_portal_first", "Open the persisted human portal before broad code reading.", 100, [portal_ref]),
        _rec("use_mcp_workflow_sequence", "Follow the MCP project reading and task context workflow before ad hoc file scans.", 90, [workflow_ref]),
        _rec("inspect_profile_terms", "Review profile and taxonomy suggestions to understand project-specific terminology.", 80, [profile_ref, taxonomy_ref]),
        _rec("check_governance_overlay", "Check approved governance overlays before treating a report item as final.", 70, [overlay_ref], needs_review=not bool(source["overlay"])),
    ]
    by_role = {
        "maintainer": [
            _rec("triage_unresolved_items", "Triage unresolved and weak evidence sections before assigning implementation work.", 95, [portal_ref, overlay_ref], needs_review=not bool(source["overlay"])),
            _rec("confirm_profile_before_scaling", "Confirm profile draft rules before applying them to future project scans.", 75, [profile_ref]),
        ],
        "coding_agent": [
            _rec("prepare_task_navigation", "Build task navigation for the concrete task and read bounded files first.", 100, [workflow_ref], needs_review=True),
            _rec("run_suggested_tests", "Run suggested tests from task navigation when they carry evidence or mark them needs_review.", 85, [workflow_ref], needs_review=True),
        ],
        "documentation_agent": [
            _rec("align_docs_with_portal", "Compare documentation claims with portal target/current/diff sections before editing docs.", 95, [portal_ref]),
            _rec("record_doc_feedback", "Record doc-code mismatch feedback through governance instead of rewriting source docs directly.", 85, [overlay_ref], needs_review=not bool(source["overlay"])),
        ],
        "architecture_reviewer": [
            _rec("review_target_current_diff", "Review target/current/diff and only accept claims with persisted evidence.", 100, [portal_ref]),
            _rec("treat_relationships_as_guidance", "Treat relationship and impact artifacts as bounded guidance, not full runtime topology.", 90, [workflow_ref]),
        ],
    }
    return sorted([*by_role[role], *shared], key=lambda item: (-int(item["priority"]), item["recommendation_id"]))


def _rec(recommendation_id: str, text: str, priority: int, evidence_refs: list[dict[str, Any]], *, needs_review: bool = False) -> dict[str, Any]:
    refs = [ref for ref in evidence_refs if ref.get("artifact_ref")]
    return {
        "recommendation_id": recommendation_id,
        "text": text,
        "priority": priority,
        "evidence_refs": refs,
        "needs_review": bool(needs_review or not refs),
    }


def _ref(payload: dict[str, Any], artifact_type: str, fallback_ref: str) -> dict[str, Any]:
    refs = list(payload.get("artifact_refs") or [])
    if refs:
        return refs[0]
    if payload:
        return {"type": artifact_type, "artifact_ref": fallback_ref}
    return {}


def _apply_budget(recommendations: list[dict[str, Any]], *, max_tokens: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    budget = max(120, int(max_tokens or DEFAULT_MAX_TOKENS))
    kept = list(recommendations)
    omitted = []
    while kept and _estimate_tokens(kept) > budget:
        item = kept.pop()
        omitted.append({"item_id": item["recommendation_id"], "reason": "token_budget", "estimated_tokens": _estimate_tokens([item])})
    return kept, omitted


def _estimate_tokens(items: list[dict[str, Any]]) -> int:
    return sum(max(20, len(json.dumps(item, ensure_ascii=False)) // 4) for item in items)


def _assert_recommendation_policy(recommendations: list[dict[str, Any]]) -> None:
    for item in recommendations:
        if not item.get("evidence_refs") and not item.get("needs_review"):
            raise ValueError("PLAYBOOK_RECOMMENDATION_MISSING_EVIDENCE_OR_NEEDS_REVIEW")


def _render_markdown(playbook: dict[str, Any]) -> str:
    lines = [
        f"# {playbook['title']}",
        "",
        f"- role: `{playbook['role']}`",
        f"- playbook_id: `{playbook['playbook_id']}`",
        f"- source_phase_refs: `{', '.join(playbook['source_phase_refs'])}`",
        "",
        "## Recommended Tool Sequence",
    ]
    for tool in playbook.get("recommended_tool_sequence", []):
        lines.append(f"- `{tool}`")
    lines.extend(["", "## Recommendations"])
    for item in playbook.get("recommendations", []):
        marker = "needs_review" if item.get("needs_review") else "evidence_backed"
        refs = ", ".join(ref.get("artifact_ref", "") for ref in item.get("evidence_refs", [])) or "none"
        lines.append(f"- **{item['recommendation_id']}** ({marker}): {item['text']} Evidence: `{refs}`")
    lines.extend(["", "## Constraints"])
    for item in playbook.get("constraints", []):
        lines.append(f"- {item}")
    if playbook.get("omitted_items"):
        lines.extend(["", "## Omitted Items"])
        for item in playbook["omitted_items"]:
            lines.append(f"- `{item['item_id']}` omitted because `{item['reason']}`")
    lines.extend(["", "## Risk Summary"])
    for item in playbook.get("risk_summary", []):
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def _role_title(role: str) -> str:
    return {
        "maintainer": "Maintainer Agent Productization Playbook",
        "coding_agent": "Coding Agent Productization Playbook",
        "documentation_agent": "Documentation Agent Productization Playbook",
        "architecture_reviewer": "Architecture Reviewer Productization Playbook",
    }[role]


def _target_user(role: str) -> str:
    return {
        "maintainer": "Human maintainer coordinating project understanding and governance.",
        "coding_agent": "Codex/Copilot-style coding agent preparing bounded implementation context.",
        "documentation_agent": "Documentation agent aligning docs with persisted architecture evidence.",
        "architecture_reviewer": "Reviewer checking target/current/diff and evidence quality.",
    }[role]


def _tool_sequence(role: str) -> list[str]:
    base = [
        "knowledge_code_agent_productization_mcp_read",
        "knowledge_code_agent_productization_profile_read",
        "knowledge_code_agent_productization_portal_read",
    ]
    if role == "coding_agent":
        return [*base, "knowledge_code_agent_productization_task_navigation_build", "knowledge_code_agent_productization_task_navigation_read"]
    if role in {"documentation_agent", "architecture_reviewer", "maintainer"}:
        return [*base, "knowledge_code_agent_productization_governance_overlay"]
    return base


def _risk_summary(source: dict[str, Any]) -> list[str]:
    risks = [
        "Playbook output is a reading and governance aid; it is not accepted implementation evidence by itself.",
        "Structured unavailable or needs_review items must remain visible to downstream Agents.",
    ]
    if source.get("unresolved"):
        risks.append("Some upstream productization artifacts are missing; recommendations may require needs_review.")
    overlay = source.get("overlay") or {}
    if overlay.get("summary", {}).get("applied_rule_count"):
        risks.append("Approved governance overlays are present and should be applied at read time only.")
    return risks


def _stable_id(prefix: str, *parts: Any) -> str:
    payload = json.dumps([str(part) for part in parts], sort_keys=True, ensure_ascii=False)
    return f"{prefix}_{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]}"
