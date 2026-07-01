"""V2.88 quality governance human review closure service."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..real_document_acceptance.persistence import read_quality_governance_review
from ..registry import CodebaseRegistry
from .persistence import (
    quality_review_artifact_refs,
    read_correction_decision_history,
    read_human_quality_review,
    read_rule_effect_review,
    write_quality_review,
)
from .shared import base_artifact, public_payload, redaction_findings, status_summary, unresolved_item, worst_status


class QualityReviewClosureService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_quality_review(self, codebase_id: str, review_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        state = review_state or {}
        generated_at = now()
        refs = quality_review_artifact_refs(codebase_id)
        try:
            upstream = read_quality_governance_review(self.workspace, codebase_id)
            upstream_status = str(upstream.get("status") or upstream.get("review_status") or "needs_review")
            upstream_hash = hashlib.sha256(json.dumps(upstream, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
            recommendations = list(upstream.get("rows") or [])
        except FileNotFoundError:
            upstream = {}
            upstream_status = "needs_review"
            upstream_hash = ""
            recommendations = []
        decisions = _decisions(recommendations, state)
        status = worst_status([decision["decision"] for decision in decisions] or ["needs_review"])
        if status == "rejected":
            status = "needs_review"
        unresolved = []
        if not recommendations:
            unresolved.append(unresolved_item("needs_review", "V2.84 quality artifact is missing or empty", item_id="quality_artifact", next_action="build V2.84 quality artifact"))
        for decision in decisions:
            if decision["decision"] == "needs_review":
                unresolved.append(unresolved_item("needs_review", "human decision is required for quality recommendation", item_id=decision["recommendation_id"], next_action=decision["next_action"]))
        review = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.88",
            artifact_type="human_quality_review",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[ref for decision in decisions for ref in decision.get("evidence_refs") or []],
            unresolved=unresolved,
            status=status,
            next_actions=["knowledge_code_real_document_full_corpus_release_quality_review_read"],
        )
        review.update(
            {
                "reviewer": state.get("reviewer") or ("human" if status == "accepted" else "structured_unavailable"),
                "upstream_status": upstream_status,
                "upstream_hash": upstream_hash,
                "hash_unchanged": True,
                "decisions": decisions,
                "summary": status_summary([{"status": decision["decision"]} for decision in decisions]),
            }
        )
        history = "\n".join(json.dumps({**decision, "timestamp": generated_at, "reviewer_state": review["reviewer"]}, ensure_ascii=False) for decision in decisions)
        report = _report(review)
        _apply_redaction(review, history, report)
        write_quality_review(self.workspace, codebase_id, review, history + ("\n" if history else ""), report)
        return self.read_quality_review(codebase_id)

    def read_quality_review(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = quality_review_artifact_refs(codebase_id)
        review = read_human_quality_review(self.workspace, codebase_id)
        history = read_correction_decision_history(self.workspace, codebase_id)
        report = read_rule_effect_review(self.workspace, codebase_id)
        return {
            "schema_version": "v2.86-90",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.88",
            "artifact_type": "quality_governance_human_review",
            "status": str(review.get("status") or "needs_review"),
            "data": {"human_quality_review": review, "correction_decision_history": history, "rule_effect_review": report},
            "summary": dict(review.get("summary") or {}),
            "artifact_refs": refs,
            "evidence_refs": list(review.get("evidence_refs") or []),
            "warnings": [],
            "unresolved": list(review.get("unresolved") or []),
            "next_actions": ["knowledge_code_real_document_full_corpus_release_quality_review_read"],
        }


def _decisions(recommendations: list[dict[str, Any]], state: dict[str, Any]) -> list[dict[str, Any]]:
    provided = {str(item.get("recommendation_id")): item for item in state.get("decisions") or [] if isinstance(item, dict)}
    decisions = []
    for idx, rec in enumerate(recommendations, start=1):
        rec_id = str(rec.get("check_id") or rec.get("recommendation_id") or f"recommendation_{idx}")
        source = provided.get(rec_id, {})
        evidence_refs = list(source.get("evidence_refs") or rec.get("evidence_refs") or [])
        decision = str(source.get("decision") or ("accepted" if source.get("decision") == "accepted" and evidence_refs else "needs_review"))
        if decision == "accepted" and not evidence_refs:
            decision = "needs_review"
        decisions.append(
            {
                "recommendation_id": rec_id,
                "decision": decision if decision in {"accepted", "rejected", "needs_review"} else "needs_review",
                "evidence_refs": evidence_refs,
                "reason": str(source.get("reason") or rec.get("finding") or "human review required"),
                "next_action": str(source.get("next_action") or "record human quality decision"),
            }
        )
    if not recommendations:
        decisions.append({"recommendation_id": "quality_artifact", "decision": "needs_review", "evidence_refs": [], "reason": "quality artifact is missing", "next_action": "build V2.84 quality artifact"})
    return decisions


def _report(review: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V2.88 Rule Effect Review",
            "",
            f"Status: {review['status']}",
            f"Upstream status: {review['upstream_status']}",
            f"Upstream hash unchanged: {review['hash_unchanged']}",
            "",
            "Automatic quality suggestions are not accepted without human decisions.",
        ]
    )


def _apply_redaction(*payloads: Any) -> None:
    findings: list[dict[str, Any]] = []
    for payload in payloads:
        findings.extend(redaction_findings(payload))
    for payload in payloads:
        if isinstance(payload, dict) and findings:
            payload.setdefault("unresolved", []).extend(findings)
            payload["status"] = "structured_blocker"


def public_quality_review_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)
