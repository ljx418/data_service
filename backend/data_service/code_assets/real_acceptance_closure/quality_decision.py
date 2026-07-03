"""V2.93 human quality decision closure service."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..real_document_acceptance.persistence import read_quality_governance_review
from ..real_document_full_corpus_release.persistence import read_human_quality_review
from ..registry import CodebaseRegistry
from .persistence import (
    quality_decision_artifact_refs,
    read_human_decisions,
    read_quality_closure_report,
    read_rule_effect_closure,
    write_quality_decision,
)
from .shared import apply_redaction_guard, base_artifact, public_payload, status_summary, unresolved_item, worst_status


class HumanQualityDecisionRecorder:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_quality_decision(self, codebase_id: str, decision_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        state = decision_state or {}
        generated_at = now()
        refs = quality_decision_artifact_refs(codebase_id)
        upstream, upstream_ref = _read_upstream_quality(self.workspace, codebase_id)
        recommendations = _recommendations(upstream)
        decisions = _decisions(recommendations, state)
        statuses = [str(item.get("decision") or "needs_review") for item in decisions]
        status = "accepted" if decisions and all(item.get("decision") in {"approved", "rejected", "revoked", "out_of_scope"} and item.get("evidence_refs") for item in decisions) else worst_status(statuses or ["needs_review"])
        unresolved = []
        if not upstream:
            unresolved.append(unresolved_item("needs_review", "quality upstream artifact is missing", item_id="quality_upstream", next_action="build V2.84 or V2.88 quality artifact"))
        for decision in decisions:
            if decision.get("decision") == "needs_review" or not decision.get("evidence_refs"):
                unresolved.append(unresolved_item("needs_review", "human decision evidence is required for quality recommendation", item_id=str(decision.get("decision_id")), next_action="record human quality decision with evidence"))
        closure = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.93",
            artifact_type="rule_effect_closure",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[ref for decision in decisions for ref in decision.get("evidence_refs") or []],
            unresolved=unresolved,
            status=status,
            next_actions=["knowledge_code_real_acceptance_closure_quality_decision_read"],
        )
        closure.update(
            {
                "upstream_hashes": [_hash_row(upstream_ref, upstream)] if upstream else [],
                "decisions": decisions,
                "summary": status_summary([{"status": "accepted" if item.get("decision") in {"approved", "rejected", "revoked", "out_of_scope"} else "needs_review"} for item in decisions]),
            }
        )
        history = "\n".join(json.dumps({**decision, "timestamp": generated_at}, ensure_ascii=False) for decision in decisions)
        report = _report(closure)
        apply_redaction_guard(closure, history, report)
        write_quality_decision(self.workspace, codebase_id, history + ("\n" if history else ""), closure, report)
        return self.read_quality_decision(codebase_id)

    def read_quality_decision(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = quality_decision_artifact_refs(codebase_id)
        history = read_human_decisions(self.workspace, codebase_id)
        closure = read_rule_effect_closure(self.workspace, codebase_id)
        report = read_quality_closure_report(self.workspace, codebase_id)
        return {
            "schema_version": "v2.91-95",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.93",
            "artifact_type": "human_quality_decision_closure",
            "status": str(closure.get("status") or "needs_review"),
            "data": {"human_decisions": history, "rule_effect_closure": closure, "quality_closure_report": report},
            "summary": dict(closure.get("summary") or {}),
            "artifact_refs": refs,
            "evidence_refs": list(closure.get("evidence_refs") or []),
            "warnings": [],
            "unresolved": list(closure.get("unresolved") or []),
            "next_actions": ["knowledge_code_real_acceptance_closure_quality_decision_read"],
        }


def _read_upstream_quality(workspace: Path, codebase_id: str) -> tuple[dict[str, Any], str]:
    try:
        return read_human_quality_review(workspace, codebase_id), "real_document_full_corpus_release://quality_review/human_quality_review.json"
    except FileNotFoundError:
        pass
    try:
        return read_quality_governance_review(workspace, codebase_id), "real_document_acceptance://quality/quality_governance_review.json"
    except FileNotFoundError:
        return {}, ""


def _recommendations(upstream: dict[str, Any]) -> list[dict[str, Any]]:
    if not upstream:
        return []
    rows = upstream.get("decisions") or upstream.get("rows") or upstream.get("findings") or []
    if isinstance(rows, list) and rows:
        return [dict(row) for row in rows if isinstance(row, dict)]
    return [{"check_id": upstream.get("artifact_type") or "quality_artifact", "finding": "human review required", "evidence_refs": upstream.get("evidence_refs") or []}]


def _decisions(recommendations: list[dict[str, Any]], state: dict[str, Any]) -> list[dict[str, Any]]:
    provided = {str(item.get("decision_id") or item.get("recommendation_id") or item.get("check_id")): item for item in state.get("decisions") or [] if isinstance(item, dict)}
    reviewer = str(state.get("reviewer") or "")
    decisions = []
    for idx, rec in enumerate(recommendations, start=1):
        rec_id = str(rec.get("decision_id") or rec.get("recommendation_id") or rec.get("check_id") or f"recommendation_{idx}")
        source = provided.get(rec_id, {})
        evidence_refs = list(source.get("evidence_refs") or [])
        decision = str(source.get("decision") or "needs_review")
        if decision not in {"approved", "rejected", "needs_review", "revoked", "out_of_scope"}:
            decision = "needs_review"
        if decision != "needs_review" and not evidence_refs:
            decision = "needs_review"
        decisions.append(
            {
                "decision_id": rec_id,
                "target_ref": str(rec.get("target_ref") or rec.get("recommendation_id") or rec_id),
                "reviewer": str(source.get("reviewer") or reviewer),
                "decision": decision,
                "reason": str(source.get("reason") or rec.get("reason") or rec.get("finding") or "human review required"),
                "evidence_refs": evidence_refs,
            }
        )
    if not recommendations:
        decisions.append({"decision_id": "quality_upstream", "target_ref": "quality_upstream", "reviewer": reviewer, "decision": "needs_review", "reason": "quality upstream artifact is missing", "evidence_refs": []})
    return decisions


def _hash_row(ref: str, payload: dict[str, Any]) -> dict[str, Any]:
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
    return {"artifact_ref": ref, "sha256": digest, "hash_unchanged": True}


def _report(closure: dict[str, Any]) -> str:
    lines = ["# V2.93 Quality Decision Closure Report", "", f"Status: {closure.get('status')}", ""]
    for decision in closure.get("decisions") or []:
        lines.append(f"- {decision.get('decision_id')}: {decision.get('decision')}")
    lines.extend(["", "Automatic quality suggestions are not accepted without human decisions."])
    return "\n".join(lines)


def public_quality_decision_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)
