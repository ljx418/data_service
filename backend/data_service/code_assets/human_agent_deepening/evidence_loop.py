"""Doc-code governance evidence loop for V2.56."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..agent_productization.persistence import (
    governance_artifact_refs,
    governance_feedback_path,
    governance_overlay_path,
    governance_rules_path,
    read_governance_feedback,
    read_governance_overlay,
    read_governance_rules,
)
from ..registry import CodebaseRegistry
from .persistence import (
    doc_code_evidence_loop_artifact_refs,
    read_decision_history,
    read_evidence_loop,
    read_evidence_loop_report,
    read_rule_effect,
    write_doc_code_evidence_loop,
)
from .shared import base_artifact, redaction_findings, structured_unavailable


PHASE = "V2.56"


class DocCodeEvidenceLoopService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_evidence_loop(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = doc_code_evidence_loop_artifact_refs(codebase_id)
        source_refs = governance_artifact_refs(codebase_id)
        before_hashes = _upstream_hashes(self.workspace, codebase_id)
        feedback, rules, overlay, warnings, unresolved = self._load_sources(codebase_id)
        findings = _findings(feedback, rules)
        decisions = _decisions(rules)
        rule_effect = _rule_effect_artifact(self.workspace_id, codebase_id, generated_at, refs, source_refs, rules, overlay, before_hashes, _upstream_hashes(self.workspace, codebase_id))
        evidence_loop = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="doc_code_evidence_loop",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=source_refs,
            warnings=warnings,
            unresolved=unresolved,
        )
        evidence_loop.update(
            {
                "findings": findings,
                "decisions": [{"decision_id": row["decision_id"], "finding_id": row["finding_id"], "action": row["action"]} for row in decisions],
                "rule_effects": rule_effect["rules"],
                "readback": {
                    "approved_rule_count": rule_effect["summary"]["approved_rule_count"],
                    "revoked_rule_count": rule_effect["summary"]["revoked_rule_count"],
                    "hash_unchanged": rule_effect["hash_unchanged"],
                    "visible_statuses": sorted(set(item["status"] for item in findings)),
                },
                "summary": {
                    "finding_count": len(findings),
                    "decision_count": len(decisions),
                    "rule_effect_count": len(rule_effect["rules"]),
                    "hash_unchanged": rule_effect["hash_unchanged"],
                },
            }
        )
        redaction = redaction_findings(evidence_loop) + redaction_findings(rule_effect)
        if redaction:
            evidence_loop["unresolved"].extend(redaction)
        report = _render_report(evidence_loop, decisions, rule_effect)
        write_doc_code_evidence_loop(self.workspace, codebase_id, evidence_loop, decisions, rule_effect, report)
        return _bundle(self.workspace_id, codebase_id, evidence_loop, decisions, rule_effect, report, refs)

    def read_evidence_loop(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = doc_code_evidence_loop_artifact_refs(codebase_id)
        evidence_loop = read_evidence_loop(self.workspace, codebase_id)
        decisions = read_decision_history(self.workspace, codebase_id)
        rule_effect = read_rule_effect(self.workspace, codebase_id)
        report = read_evidence_loop_report(self.workspace, codebase_id)
        return _bundle(self.workspace_id, codebase_id, evidence_loop, decisions, rule_effect, report, refs)

    def _load_sources(self, codebase_id: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any], list[str], list[dict[str, Any]]]:
        warnings = []
        unresolved = []
        try:
            feedback = read_governance_feedback(self.workspace, codebase_id)
        except FileNotFoundError as exc:
            feedback = []
            unresolved.append(structured_unavailable("governance_feedback", str(exc)))
        try:
            rules = read_governance_rules(self.workspace, codebase_id)
        except FileNotFoundError as exc:
            rules = []
            unresolved.append(structured_unavailable("governance_rules", str(exc)))
        try:
            overlay = read_governance_overlay(self.workspace, codebase_id)
        except FileNotFoundError as exc:
            overlay = {}
            unresolved.append(structured_unavailable("governance_overlay", str(exc)))
        if unresolved:
            warnings.append("DOC_CODE_EVIDENCE_LOOP_SOURCE_PARTIAL")
        return feedback, rules, overlay, warnings, unresolved


def public_doc_code_evidence_loop_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "doc_code_evidence_loop",
        "evidence_loop": payload.get("evidence_loop") or {},
        "decision_history": payload.get("decision_history") or [],
        "rule_effect": payload.get("rule_effect") or {},
        "report": {"format": "markdown", "content": payload.get("report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _bundle(workspace_id: str, codebase_id: str, evidence_loop: dict[str, Any], decisions: list[dict[str, Any]], rule_effect: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.54-58",
        "artifact_type": "doc_code_evidence_loop",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "evidence_loop": evidence_loop,
        "decision_history": decisions,
        "rule_effect": rule_effect,
        "report": report,
        "summary": dict(evidence_loop.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(evidence_loop.get("warnings") or []),
        "unresolved": list(evidence_loop.get("unresolved") or []),
        "next_actions": ["knowledge_code_human_agent_deepening_evidence_loop_read"],
    }


def _findings(feedback: list[dict[str, Any]], rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_feedback = {fid: rule for rule in rules for fid in list(rule.get("feedback_ids") or [])}
    findings = []
    for row in feedback:
        rule = by_feedback.get(row.get("feedback_id"), {})
        status = _finding_status(row, rule)
        findings.append(
            {
                "finding_id": str(row.get("feedback_id")),
                "target_type": row.get("target_type"),
                "target_id": row.get("target_id"),
                "claim": row.get("reason") or row.get("action") or "governance feedback",
                "status": status,
                "rule_id": rule.get("rule_id"),
                "evidence_refs": row.get("artifact_refs") or governance_artifact_refs(str(row.get("codebase_id") or "")),
            }
        )
    if not findings:
        findings.append({"finding_id": "governance_feedback_missing", "status": "needs_review", "claim": "no governance feedback available", "evidence_refs": []})
    return findings


def _finding_status(feedback: dict[str, Any], rule: dict[str, Any]) -> str:
    severity = str(feedback.get("severity") or "").lower()
    rule_status = str(rule.get("status") or "").lower()
    rule_type = str(feedback.get("rule_type") or "").lower()
    if rule_status == "approved":
        return "supported"
    if rule_status == "revoked":
        return "contradicted"
    if severity == "high" or "missing" in rule_type:
        return "unsupported"
    if rule:
        return "weak"
    return "needs_review"


def _decisions(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for rule in rules:
        status = str(rule.get("status") or "draft")
        action = "needs_review"
        if status == "approved":
            action = "approve"
        elif status == "revoked":
            action = "revoke"
        elif status == "rejected":
            action = "comment"
        rows.append(
            {
                "decision_id": f"decision_{rule.get('rule_id')}",
                "finding_id": str((rule.get("feedback_ids") or [""])[0]),
                "rule_id": rule.get("rule_id"),
                "action": action,
                "actor": rule.get("reviewer") or "system",
                "reason": rule.get("review_note") or rule.get("reason") or status,
                "timestamp": rule.get("reviewed_at") or rule.get("updated_at") or rule.get("created_at") or now(),
            }
        )
    return rows


def _rule_effect_artifact(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], source_refs: list[dict[str, str]], rules: list[dict[str, Any]], overlay: dict[str, Any], before: dict[str, str], after: dict[str, str]) -> dict[str, Any]:
    rows = []
    for rule in rules:
        rows.append(
            {
                "rule_id": rule.get("rule_id"),
                "current_state": rule.get("status") or "draft",
                "source_decision": f"decision_{rule.get('rule_id')}",
                "effect": "read_time_overlay" if rule.get("status") == "approved" else "inactive_readback",
            }
        )
    return {
        **base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="doc_code_rule_effect", generated_at=generated_at, artifact_refs=refs, evidence_refs=source_refs),
        "rules": rows,
        "overlay_summary": dict(overlay.get("summary") or {}),
        "upstream_hashes": {"before": before, "after": after},
        "hash_unchanged": before == after,
        "summary": {
            "rule_count": len(rows),
            "approved_rule_count": sum(1 for row in rows if row["current_state"] == "approved"),
            "revoked_rule_count": sum(1 for row in rows if row["current_state"] == "revoked"),
        },
    }


def _upstream_hashes(workspace: Path, codebase_id: str) -> dict[str, str]:
    paths = {
        "governance_feedback": governance_feedback_path(workspace, codebase_id),
        "governance_rules": governance_rules_path(workspace, codebase_id),
        "governance_overlay": governance_overlay_path(workspace, codebase_id),
    }
    hashes = {}
    for key, path in paths.items():
        if path.exists():
            hashes[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def _render_report(evidence_loop: dict[str, Any], decisions: list[dict[str, Any]], rule_effect: dict[str, Any]) -> str:
    lines = [
        "# Doc-Code Evidence Loop",
        "",
        f"- finding_count: `{evidence_loop['summary']['finding_count']}`",
        f"- decision_count: `{len(decisions)}`",
        f"- hash_unchanged: `{rule_effect['hash_unchanged']}`",
        "",
        "## Findings",
    ]
    for item in evidence_loop.get("findings", []):
        lines.append(f"- `{item['finding_id']}` {item['status']}: {item.get('claim', '')}")
    lines.extend(["", "## Decisions"])
    for item in decisions:
        lines.append(f"- `{item['decision_id']}` {item['action']} -> `{item['finding_id']}`")
    lines.extend(["", "## Rule Effects"])
    for item in rule_effect.get("rules", []):
        lines.append(f"- `{item['rule_id']}` {item['current_state']} {item['effect']}")
    return "\n".join(lines) + "\n"
