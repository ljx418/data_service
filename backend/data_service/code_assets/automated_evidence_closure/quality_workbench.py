"""V2.98 quality decision minimization workbench."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import quality_workbench_artifact_refs, read_decision_recommendations, read_human_decision_backlog, read_risk_queue, write_quality_workbench
from .shared import apply_redaction_guard, base_artifact, public_payload, status_summary, unresolved_item


class QualityDecisionWorkbench:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_quality_workbench(self, codebase_id: str, decision_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        state = decision_state or {}
        generated_at = now()
        refs = quality_workbench_artifact_refs(codebase_id)
        recommendations = _recommendations(state)
        human_decisions = {str(item.get("recommendation_id")): item for item in state.get("human_decisions") or [] if isinstance(item, dict)}
        rows = []
        unresolved = []
        evidence_refs: list[Any] = []
        for rec in recommendations:
            decision = human_decisions.get(rec["recommendation_id"])
            rec["human_decision_state"] = str((decision or {}).get("decision") or "needs_review")
            rec["status"] = "accepted" if rec["risk_level"] != "high" or rec["human_decision_state"] in {"approved", "rejected", "accepted"} else "needs_review"
            rec["decision_evidence_refs"] = list((decision or {}).get("evidence_refs") or [])
            evidence_refs.extend(rec.get("evidence_refs") or [])
            evidence_refs.extend(rec["decision_evidence_refs"])
            rows.append(rec)
            if rec["status"] != "accepted":
                unresolved.append(unresolved_item("needs_review", "high-risk quality recommendation needs human decision", item_id=rec["recommendation_id"], evidence_refs=rec.get("evidence_refs"), next_action="record reviewer decision"))
        if not rows:
            unresolved.append(unresolved_item("needs_review", "quality recommendation input is missing", item_id="quality_recommendations", next_action="provide quality recommendations or upstream quality artifacts"))
        status = "accepted" if rows and all(row["status"] == "accepted" for row in rows) else "needs_review"
        risk_queue = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase="V2.98", artifact_type="quality_risk_queue", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs, unresolved=unresolved, status=status, next_actions=["knowledge_code_automated_evidence_closure_quality_workbench_read"])
        risk_queue.update({"data": {"items": rows}, "summary": status_summary(rows)})
        recommendation_artifact = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase="V2.98", artifact_type="quality_decision_recommendations", generated_at=generated_at, artifact_refs=refs, evidence_refs=evidence_refs, unresolved=unresolved, status=status)
        recommendation_artifact.update({"data": {"recommendations": rows}})
        backlog = _backlog(status, rows)
        apply_redaction_guard(risk_queue, recommendation_artifact, backlog)
        write_quality_workbench(self.workspace, codebase_id, risk_queue, recommendation_artifact, backlog)
        return self.read_quality_workbench(codebase_id)

    def read_quality_workbench(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        risk_queue = read_risk_queue(self.workspace, codebase_id)
        recommendations = read_decision_recommendations(self.workspace, codebase_id)
        backlog = read_human_decision_backlog(self.workspace, codebase_id)
        return {
            "schema_version": "v2.96-100",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.98",
            "artifact_type": "quality_workbench",
            "status": str(risk_queue.get("status") or "needs_review"),
            "data": {"risk_queue": risk_queue, "decision_recommendations": recommendations, "human_decision_backlog": backlog},
            "summary": dict(risk_queue.get("summary") or {}),
            "artifact_refs": quality_workbench_artifact_refs(codebase_id),
            "evidence_refs": list(risk_queue.get("evidence_refs") or []),
            "warnings": list(risk_queue.get("warnings") or []),
            "unresolved": list(risk_queue.get("unresolved") or []),
            "next_actions": ["knowledge_code_automated_evidence_closure_quality_workbench_read"],
        }


def _recommendations(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for idx, item in enumerate(state.get("recommendations") or [], start=1):
        if not isinstance(item, dict):
            continue
        evidence_refs = list(item.get("evidence_refs") or [])
        rows.append({"recommendation_id": str(item.get("recommendation_id") or f"quality_recommendation_{idx}"), "risk_level": str(item.get("risk_level") or "high"), "recommended_decision": str(item.get("recommended_decision") or "needs_review"), "evidence_refs": evidence_refs})
    return rows


def _backlog(status: str, rows: list[dict[str, Any]]) -> str:
    lines = ["# V2.98 Human Quality Decision Backlog", "", f"Status: {status}", ""]
    pending = [row for row in rows if row.get("status") != "accepted"]
    if not pending:
        lines.append("No pending high-risk human quality decisions.")
    for row in pending:
        lines.append(f"- {row['recommendation_id']}: {row['risk_level']} / {row['human_decision_state']}")
    lines.extend(["", "Automatic recommendations do not replace reviewer decisions for high-risk quality items."])
    return "\n".join(lines)


def public_quality_workbench_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)

