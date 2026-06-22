"""Read-time governance workflow for V2.50 Agent Productization artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .mcp_usage import AGENT_PRODUCTIZATION_SCHEMA_VERSION
from .persistence import (
    governance_artifact_refs,
    read_governance_feedback,
    read_governance_overlay,
    read_governance_rules,
    read_mcp_agent_workflows,
    read_portal_model,
    read_profile_draft,
    read_task_impact,
    read_task_reading_order,
    write_governance_feedback,
    write_governance_overlay,
    write_governance_rules,
)


RULE_STATUSES = {"draft", "approved", "rejected", "revoked"}
TARGET_TYPES = {"portal_section", "profile_artifact", "task_artifact", "mcp_workflow"}


class AgentProductizationGovernanceService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def record_feedback(
        self,
        codebase_id: str,
        *,
        target_type: str,
        target_id: str,
        action: str,
        rule_type: str = "read_time_overlay",
        severity: str = "medium",
        reason: str = "",
        suggested_value: str = "",
    ) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        resolved = self.resolve_target(codebase_id, target_type, target_id)
        feedback = {
            "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
            "artifact_type": "agent_productization_governance_feedback",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "feedback_id": _stable_id("feedback", codebase_id, target_type, target_id, action, rule_type, suggested_value),
            "target_type": target_type,
            "target_id": target_id,
            "action": str(action or "").strip(),
            "rule_type": str(rule_type or "read_time_overlay").strip(),
            "severity": str(severity or "medium").strip(),
            "reason": reason,
            "suggested_value": suggested_value,
            "resolved_target": resolved,
            "status": "recorded",
            "created_at": now(),
            "artifact_refs": governance_artifact_refs(codebase_id),
        }
        if not feedback["action"]:
            raise ValueError("INVALID_ACTION")
        rows = [row for row in read_governance_feedback(self.workspace, codebase_id) if row.get("feedback_id") != feedback["feedback_id"]]
        rows.append(feedback)
        write_governance_feedback(self.workspace, codebase_id, sorted(rows, key=lambda row: str(row.get("feedback_id"))))
        overlay = self.build_overlay(codebase_id)
        return {"feedback": feedback, "overlay": overlay, "artifact_refs": governance_artifact_refs(codebase_id)}

    def build_rules(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        feedback_rows = read_governance_feedback(self.workspace, codebase_id)
        if not feedback_rows:
            raise FileNotFoundError("AGENT_PRODUCTIZATION_GOVERNANCE_FEEDBACK_NOT_FOUND")
        existing = {str(row.get("rule_id")): row for row in read_governance_rules(self.workspace, codebase_id)}
        rules = []
        for feedback in feedback_rows:
            rule_id = _stable_id("rule", feedback.get("target_type"), feedback.get("target_id"), feedback.get("rule_type"), feedback.get("suggested_value"))
            current = dict(existing.get(rule_id) or {})
            status = str(current.get("status") or "draft")
            rules.append(
                {
                    "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
                    "artifact_type": "agent_productization_governance_rule",
                    "workspace_id": self.workspace_id,
                    "codebase_id": codebase_id,
                    "rule_id": rule_id,
                    "feedback_ids": sorted(set([*list(current.get("feedback_ids") or []), str(feedback["feedback_id"])])),
                    "target_type": feedback["target_type"],
                    "target_id": feedback["target_id"],
                    "rule_type": feedback["rule_type"],
                    "severity": feedback["severity"],
                    "effect": "read_time_overlay",
                    "status": status,
                    "suggested_value": feedback.get("suggested_value"),
                    "reason": feedback.get("reason"),
                    "resolved_target": feedback.get("resolved_target", {}),
                    "created_at": current.get("created_at") or now(),
                    "updated_at": now(),
                    "artifact_refs": governance_artifact_refs(codebase_id),
                }
            )
        write_governance_rules(self.workspace, codebase_id, sorted(rules, key=lambda row: str(row.get("rule_id"))))
        overlay = self.build_overlay(codebase_id)
        return {"rules": rules, "overlay": overlay, "artifact_refs": governance_artifact_refs(codebase_id)}

    def review_rule(self, codebase_id: str, rule_id: str, *, status: str, reviewer: str = "", note: str = "") -> dict[str, Any]:
        self.registry.describe(codebase_id)
        normalized = str(status or "").strip()
        if normalized not in RULE_STATUSES:
            raise ValueError("INVALID_RULE_STATUS")
        rows = read_governance_rules(self.workspace, codebase_id)
        updated = []
        reviewed = None
        for row in rows:
            item = dict(row)
            if item.get("rule_id") == rule_id:
                item["status"] = normalized
                item["reviewer"] = reviewer or "unknown"
                item["review_note"] = note
                item["reviewed_at"] = now()
                item["updated_at"] = item["reviewed_at"]
                reviewed = item
            updated.append(item)
        if reviewed is None:
            raise FileNotFoundError("AGENT_PRODUCTIZATION_GOVERNANCE_RULE_NOT_FOUND")
        write_governance_rules(self.workspace, codebase_id, updated)
        overlay = self.build_overlay(codebase_id)
        return {"rule": reviewed, "overlay": overlay, "artifact_refs": governance_artifact_refs(codebase_id)}

    def build_overlay(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        source_hash_before = self._source_hashes(codebase_id)
        feedback_rows = read_governance_feedback(self.workspace, codebase_id)
        rules = read_governance_rules(self.workspace, codebase_id)
        approved = [row for row in rules if row.get("status") == "approved"]
        revoked = [row for row in rules if row.get("status") == "revoked"]
        applied_rules = []
        for rule in approved:
            applied_rules.append(
                {
                    "rule_id": rule.get("rule_id"),
                    "target_type": rule.get("target_type"),
                    "target_id": rule.get("target_id"),
                    "effect": "read_time_overlay",
                    "suggested_value": rule.get("suggested_value"),
                    "resolved_target": self.resolve_target(codebase_id, str(rule.get("target_type") or ""), str(rule.get("target_id") or "")),
                }
            )
        source_hash_after = self._source_hashes(codebase_id)
        overlay = {
            "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
            "artifact_type": "agent_productization_governance_overlay",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "summary": {
                "feedback_count": len(feedback_rows),
                "rule_count": len(rules),
                "approved_rule_count": len(approved),
                "revoked_rule_count": len(revoked),
                "applied_rule_count": len(applied_rules),
                "source_artifact_hash_unchanged": source_hash_before == source_hash_after,
            },
            "applied_rules": applied_rules,
            "revoked_rule_ids": [row.get("rule_id") for row in revoked],
            "source_artifact_hash_before": source_hash_before,
            "source_artifact_hash_after": source_hash_after,
            "warnings": [] if source_hash_before == source_hash_after else ["SOURCE_ARTIFACT_HASH_CHANGED"],
            "unresolved": [],
            "artifact_refs": governance_artifact_refs(codebase_id),
            "created_at": now(),
        }
        write_governance_overlay(self.workspace, codebase_id, overlay)
        return overlay

    def read_overlay(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        try:
            return read_governance_overlay(self.workspace, codebase_id)
        except FileNotFoundError:
            return self.build_overlay(codebase_id)

    def resolve_target(self, codebase_id: str, target_type: str, target_id: str) -> dict[str, Any]:
        if target_type not in TARGET_TYPES or not str(target_id or "").strip():
            raise FileNotFoundError("AGENT_PRODUCTIZATION_GOVERNANCE_TARGET_NOT_FOUND")
        if target_type == "portal_section":
            model = read_portal_model(self.workspace, codebase_id)
            for section in model.get("sections", []):
                if section.get("section_id") == target_id:
                    return {"target_type": target_type, "target_id": target_id, "title": section.get("title"), "status": section.get("status")}
        if target_type == "profile_artifact":
            profile = read_profile_draft(self.workspace, codebase_id)
            if target_id in {"profile_draft", str(profile.get("profile_id") or "")}:
                return {"target_type": target_type, "target_id": target_id, "profile_status": profile.get("profile_status")}
        if target_type == "mcp_workflow":
            workflows = read_mcp_agent_workflows(self.workspace, codebase_id)
            for workflow in workflows.get("workflows", []):
                if workflow.get("workflow_id") == target_id:
                    return {"target_type": target_type, "target_id": target_id, "title": workflow.get("title")}
        if target_type == "task_artifact":
            if ":" not in target_id:
                raise FileNotFoundError("AGENT_PRODUCTIZATION_GOVERNANCE_TARGET_NOT_FOUND")
            task_id, artifact = target_id.split(":", 1)
            if artifact == "reading_order":
                payload = read_task_reading_order(self.workspace, codebase_id, task_id)
            elif artifact == "task_impact":
                payload = read_task_impact(self.workspace, codebase_id, task_id)
            else:
                raise FileNotFoundError("AGENT_PRODUCTIZATION_GOVERNANCE_TARGET_NOT_FOUND")
            return {"target_type": target_type, "target_id": target_id, "artifact_type": payload.get("artifact_type"), "task_id": task_id}
        raise FileNotFoundError("AGENT_PRODUCTIZATION_GOVERNANCE_TARGET_NOT_FOUND")

    def _source_hashes(self, codebase_id: str) -> dict[str, str]:
        candidates = []
        for reader_name, reader in [
            ("portal_model", read_portal_model),
            ("profile_draft", read_profile_draft),
            ("mcp_workflows", read_mcp_agent_workflows),
        ]:
            try:
                payload = reader(self.workspace, codebase_id)
            except FileNotFoundError:
                continue
            candidates.append((reader_name, payload))
        return {name: hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest() for name, payload in candidates}


def public_governance_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "artifact_type": "agent_productization_governance_bundle",
        "feedback": payload.get("feedback"),
        "rules": payload.get("rules"),
        "rule": payload.get("rule"),
        "overlay": payload.get("overlay") or payload.get("overlay_report") or payload,
        "artifact_refs": payload.get("artifact_refs", []),
    }


def _stable_id(prefix: str, *parts: Any) -> str:
    payload = json.dumps([str(part) for part in parts], sort_keys=True, ensure_ascii=False)
    return f"{prefix}_{hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16]}"
