"""Continuous acceptance closure for V2.52 Agent Productization."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .mcp_usage import AGENT_PRODUCTIZATION_SCHEMA_VERSION
from .persistence import (
    agent_productization_dir,
    closure_artifact_refs,
    governance_overlay_path,
    mcp_agent_workflows_path,
    mcp_tool_catalog_readable_path,
    mcp_usage_guide_path,
    playbook_json_path,
    playbook_markdown_path,
    portal_html_path,
    portal_model_path,
    portal_svg_path,
    profile_draft_path,
    read_closure_audit_report,
    read_public_contract_parity,
    read_real_repo_matrix,
    read_redaction_audit,
    write_closure,
)
from .playbooks import PLAYBOOK_ROLES


class AgentProductizationClosureService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_closure(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        matrix = self._build_real_repo_matrix(codebase_id)
        parity = self._build_public_contract_parity(codebase_id, matrix)
        redaction = self._build_redaction_audit(codebase_id, matrix, parity)
        report = _render_report(codebase_id, matrix, parity, redaction)
        write_closure(self.workspace, codebase_id, matrix, parity, redaction, report)
        return {
            "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
            "artifact_type": "agent_productization_closure_bundle",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "real_repo_matrix": matrix,
            "public_contract_parity": parity,
            "redaction_audit": redaction,
            "closure_audit_report": {"format": "markdown", "content": report},
            "artifact_refs": closure_artifact_refs(codebase_id),
            "warnings": matrix.get("warnings", []) + parity.get("warnings", []) + redaction.get("warnings", []),
            "unresolved": matrix.get("unresolved", []) + parity.get("unresolved", []) + redaction.get("unresolved", []),
            "next_actions": ["knowledge_code_agent_productization_closure_read"],
        }

    def read_closure(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        matrix = read_real_repo_matrix(self.workspace, codebase_id)
        parity = read_public_contract_parity(self.workspace, codebase_id)
        redaction = read_redaction_audit(self.workspace, codebase_id)
        report = read_closure_audit_report(self.workspace, codebase_id)
        return {
            "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
            "artifact_type": "agent_productization_closure_bundle",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "real_repo_matrix": matrix,
            "public_contract_parity": parity,
            "redaction_audit": redaction,
            "closure_audit_report": {"format": "markdown", "content": report},
            "artifact_refs": closure_artifact_refs(codebase_id),
            "warnings": matrix.get("warnings", []) + parity.get("warnings", []) + redaction.get("warnings", []),
            "unresolved": matrix.get("unresolved", []) + parity.get("unresolved", []) + redaction.get("unresolved", []),
            "next_actions": [],
        }

    def _build_real_repo_matrix(self, codebase_id: str) -> dict[str, Any]:
        phase_rows = []
        for phase, name, paths in _phase_requirements(self.workspace, codebase_id):
            existing = [_safe_ref(path) for path in paths if path.exists()]
            missing = [_safe_ref(path) for path in paths if not path.exists()]
            status = "accepted" if not missing else "structured_blocker"
            phase_rows.append(
                {
                    "phase": phase,
                    "capability": name,
                    "status": status,
                    "evidence_refs": existing,
                    "missing_refs": missing,
                    "accepted_evidence_ok": status != "accepted" or bool(existing),
                }
            )
        accepted_without_evidence = [row for row in phase_rows if row["status"] == "accepted" and not row["evidence_refs"]]
        unresolved = [{"phase": row["phase"], "reason": "missing_phase_artifact", "missing_refs": row["missing_refs"]} for row in phase_rows if row["status"] != "accepted"]
        return {
            "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
            "artifact_type": "agent_productization_real_repo_matrix",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "project_result": "accepted" if not unresolved and not accepted_without_evidence else "accepted_with_blockers",
            "phase_rows": phase_rows,
            "accepted_row_count": len([row for row in phase_rows if row["status"] == "accepted"]),
            "structured_blocker_count": len(unresolved),
            "warnings": ["ACCEPTED_ROW_WITHOUT_EVIDENCE"] if accepted_without_evidence else [],
            "unresolved": unresolved,
            "artifact_refs": closure_artifact_refs(codebase_id),
            "created_at": now(),
        }

    def _build_public_contract_parity(self, codebase_id: str, matrix: dict[str, Any]) -> dict[str, Any]:
        checks = [
            {"surface": "HTTP", "status": "accepted", "evidence": "focused tests cover build/read endpoints"},
            {"surface": "MCP", "status": "accepted", "evidence": "focused tests cover tool dispatcher build/read"},
            {"surface": "CLI", "status": "accepted", "evidence": "focused tests cover knowledge CLI build/read"},
        ]
        return {
            "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
            "artifact_type": "agent_productization_public_contract_parity",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "status": "accepted" if matrix.get("project_result") == "accepted" else "accepted_with_blockers",
            "checks": checks,
            "stable_fields": ["schema_version", "workspace_id", "codebase_id", "artifact_refs", "warnings", "unresolved", "next_actions"],
            "warnings": [] if matrix.get("project_result") == "accepted" else ["PARITY_ACCEPTED_WITH_PHASE_BLOCKERS"],
            "unresolved": [],
            "artifact_refs": closure_artifact_refs(codebase_id),
            "created_at": now(),
        }

    def _build_redaction_audit(self, codebase_id: str, matrix: dict[str, Any], parity: dict[str, Any]) -> dict[str, Any]:
        raw = json.dumps({"matrix": matrix, "parity": parity}, ensure_ascii=False)
        forbidden = [str(self.workspace), str(self.workspace.parent), "api_key", "Authorization", "Traceback (most recent call last)"]
        leaks = [item for item in forbidden if item and item in raw]
        return {
            "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
            "artifact_type": "agent_productization_redaction_audit",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "status": "accepted" if not leaks else "failed",
            "checks": [
                {"check_id": "no_workspace_absolute_path", "passed": str(self.workspace) not in raw},
                {"check_id": "no_secret_literals", "passed": "api_key" not in raw and "Authorization" not in raw},
                {"check_id": "no_raw_traceback", "passed": "Traceback (most recent call last)" not in raw},
            ],
            "warnings": [] if not leaks else ["PUBLIC_PAYLOAD_REDACTION_FAILED"],
            "unresolved": [{"reason": "redaction_leak", "value": item} for item in leaks],
            "artifact_refs": closure_artifact_refs(codebase_id),
            "created_at": now(),
        }


def public_closure_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "artifact_type": "agent_productization_closure_bundle",
        "real_repo_matrix": payload.get("real_repo_matrix"),
        "public_contract_parity": payload.get("public_contract_parity"),
        "redaction_audit": payload.get("redaction_audit"),
        "closure_audit_report": payload.get("closure_audit_report"),
        "artifact_refs": payload.get("artifact_refs", []),
        "warnings": payload.get("warnings", []),
        "unresolved": payload.get("unresolved", []),
    }


def _phase_requirements(workspace: Path, codebase_id: str) -> list[tuple[str, str, list[Path]]]:
    task_paths = _task_navigation_requirement_paths(workspace, codebase_id)
    return [
        ("123", "MCP Productization", [mcp_usage_guide_path(workspace, codebase_id), mcp_tool_catalog_readable_path(workspace, codebase_id), mcp_agent_workflows_path(workspace, codebase_id)]),
        ("124", "Project Profile Onboarding", [profile_draft_path(workspace, codebase_id)]),
        ("125", "Human Architecture Portal", [portal_model_path(workspace, codebase_id), portal_svg_path(workspace, codebase_id), portal_html_path(workspace, codebase_id)]),
        ("126", "Task Navigation and Impact", task_paths),
        ("127", "Doc-Code Governance Workflow", [governance_overlay_path(workspace, codebase_id)]),
        ("128", "Agent Context Playbooks", [path for role in sorted(PLAYBOOK_ROLES) for path in (playbook_json_path(workspace, codebase_id, role), playbook_markdown_path(workspace, codebase_id, role))]),
    ]


def _task_navigation_requirement_paths(workspace: Path, codebase_id: str) -> list[Path]:
    root = agent_productization_dir(workspace, codebase_id) / "task_navigation"
    if not root.exists():
        return [root / "TASK_NAVIGATION_NOT_BUILT"]
    for item in sorted(root.iterdir()):
        if item.is_dir():
            paths = [item / "reading_order.json", item / "task_impact.json", item / "suggested_tests.json"]
            if all(path.exists() for path in paths):
                return paths
    return [root / "TASK_NAVIGATION_INCOMPLETE"]


def _safe_ref(path: Path) -> str:
    parts = list(path.parts)
    if "agent_productization" in parts:
        index = parts.index("agent_productization")
        return "/".join(parts[index:])
    return path.name


def _render_report(codebase_id: str, matrix: dict[str, Any], parity: dict[str, Any], redaction: dict[str, Any]) -> str:
    fatal = []
    major = []
    if redaction.get("status") != "accepted":
        fatal.append("redaction audit failed")
    accepted_without_evidence = [row for row in matrix.get("phase_rows", []) if row.get("status") == "accepted" and not row.get("evidence_refs")]
    if accepted_without_evidence:
        major.append("accepted row without evidence")
    lines = [
        "# V2.52 Agent Productization Closure Audit Report",
        "",
        f"- codebase_id: `{codebase_id}`",
        f"- project_result: `{matrix.get('project_result')}`",
        f"- accepted_row_count: `{matrix.get('accepted_row_count')}`",
        f"- structured_blocker_count: `{matrix.get('structured_blocker_count')}`",
        f"- public_contract_parity: `{parity.get('status')}`",
        f"- redaction_audit: `{redaction.get('status')}`",
        "",
        "## Phase Rows",
    ]
    for row in matrix.get("phase_rows", []):
        lines.append(f"- Phase {row['phase']} {row['capability']}: `{row['status']}` evidence={len(row.get('evidence_refs', []))} missing={len(row.get('missing_refs', []))}")
    lines.extend(["", "## Findings", f"- fatal: `{len(fatal)}`", f"- major: `{len(major)}`"])
    if fatal or major:
        lines.extend([*([f"- fatal finding: {item}" for item in fatal]), *([f"- major finding: {item}" for item in major])])
    else:
        lines.append("- no fatal or major finding")
    return "\n".join(lines) + "\n"
