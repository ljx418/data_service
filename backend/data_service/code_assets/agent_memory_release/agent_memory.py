"""Agent long-term project memory artifacts for V2.73."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    agent_memory_artifact_refs,
    ci_warning_governance_artifact_refs,
    external_project_closure_artifact_refs,
    read_acceptance_state,
    read_evidence_index,
    read_failure_diagnosis,
    read_memory_index,
    read_project_binding_closure,
    read_retention_policy,
    read_task_briefing,
    read_warning_budget,
    write_agent_memory,
)
from .shared import base_artifact, redaction_findings, worst_status


PHASE = "V2.73"


class AgentMemoryService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_agent_memory(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = agent_memory_artifact_refs(codebase_id)
        closure = _try_read(lambda: read_project_binding_closure(self.workspace, codebase_id))
        warning_budget = _try_read(lambda: read_warning_budget(self.workspace, codebase_id))
        failure_diagnosis = _try_read(lambda: read_failure_diagnosis(self.workspace, codebase_id))
        source_refs = _source_refs(codebase_id, closure, warning_budget)
        memory = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="memory_index", generated_at=generated_at, artifact_refs=refs, evidence_refs=source_refs, next_actions=["knowledge_code_agent_memory_release_memory_read"])
        memory["items"] = _memory_items(source_refs, closure, warning_budget)
        evidence = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="evidence_index", generated_at=generated_at, artifact_refs=refs, evidence_refs=source_refs)
        evidence["items"] = [{"evidence_id": f"evidence_{idx}", "artifact_ref": ref.get("artifact_ref", str(ref)), "source": ref.get("type", "artifact")} for idx, ref in enumerate(source_refs, start=1) if isinstance(ref, dict)]
        acceptance = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="acceptance_state", generated_at=generated_at, artifact_refs=refs, evidence_refs=source_refs)
        acceptance["states"] = _acceptance_states(closure, warning_budget)
        acceptance["overall_status"] = worst_status([str(item["status"]) for item in acceptance["states"]])
        briefing = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="task_briefing", generated_at=generated_at, artifact_refs=refs, evidence_refs=source_refs)
        briefing["recommendations"] = _recommendations(source_refs)
        briefing["stop_conditions"] = ["missing evidence must be needs_review", "structured_unavailable must not be accepted", "do not claim generic chat long-term memory"]
        briefing["suggested_tests"] = ["backend/tests/test_v2_73_agent_long_term_memory_productization.py", "backend/tests/test_public_surface_guard.py"]
        retention = _retention_policy()
        unresolved = redaction_findings(memory) + redaction_findings(evidence) + redaction_findings(acceptance) + redaction_findings(briefing) + redaction_findings(retention)
        if failure_diagnosis.get("items"):
            evidence["failure_diagnosis_refs"] = failure_diagnosis.get("artifact_refs", [])
        if unresolved:
            memory["unresolved"].extend(unresolved)
        write_agent_memory(self.workspace, codebase_id, memory, evidence, acceptance, briefing, retention)
        return _bundle(self.workspace_id, codebase_id, memory, evidence, acceptance, briefing, retention, refs)

    def read_agent_memory(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = agent_memory_artifact_refs(codebase_id)
        return _bundle(self.workspace_id, codebase_id, read_memory_index(self.workspace, codebase_id), read_evidence_index(self.workspace, codebase_id), read_acceptance_state(self.workspace, codebase_id), read_task_briefing(self.workspace, codebase_id), read_retention_policy(self.workspace, codebase_id), refs)


def public_agent_memory_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "agent_long_term_memory",
        "memory_index": payload.get("memory_index") or {},
        "evidence_index": payload.get("evidence_index") or {},
        "acceptance_state": payload.get("acceptance_state") or {},
        "task_briefing": payload.get("task_briefing") or {},
        "retention_policy": {"format": "markdown", "content": payload.get("retention_policy") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _try_read(reader) -> dict[str, Any]:
    try:
        return reader()
    except FileNotFoundError:
        return {}


def _source_refs(codebase_id: str, closure: dict[str, Any], warning_budget: dict[str, Any]) -> list[dict[str, str]]:
    refs: list[dict[str, str]] = []
    refs.extend(closure.get("artifact_refs") or external_project_closure_artifact_refs(codebase_id))
    refs.extend(warning_budget.get("artifact_refs") or ci_warning_governance_artifact_refs(codebase_id))
    return refs


def _memory_items(source_refs: list[dict[str, str]], closure: dict[str, Any], warning_budget: dict[str, Any]) -> list[dict[str, Any]]:
    first_ref = source_refs[0]["artifact_ref"] if source_refs else "agent_memory_release://missing/source"
    return [
        {"memory_item_id": "external_project_status", "status": "accepted" if closure else "needs_review", "source_artifact_ref": first_ref, "evidence_refs": closure.get("evidence_refs") or source_refs, "confidence": "medium" if closure else "low", "retention_policy": "review_each_stage", "expires_or_review_after": "next_phase"},
        {"memory_item_id": "ci_warning_status", "status": str(warning_budget.get("status") or "needs_review"), "source_artifact_ref": (source_refs[-1]["artifact_ref"] if source_refs else first_ref), "evidence_refs": warning_budget.get("evidence_refs") or source_refs, "confidence": "medium", "retention_policy": "review_each_stage", "expires_or_review_after": "next_test_run"},
    ]


def _acceptance_states(closure: dict[str, Any], warning_budget: dict[str, Any]) -> list[dict[str, Any]]:
    closure_status = "accepted" if closure.get("summary", {}).get("unavailable_accepted_count") == 0 and closure else "needs_review"
    return [
        {"capability": "external_project_closure", "status": closure_status, "evidence_refs": closure.get("evidence_refs") or [], "unresolved": closure.get("unresolved") or []},
        {"capability": "ci_warning_governance", "status": str(warning_budget.get("status") or "needs_review"), "evidence_refs": warning_budget.get("evidence_refs") or [], "unresolved": warning_budget.get("unresolved") or []},
    ]


def _recommendations(source_refs: list[dict[str, str]]) -> list[dict[str, Any]]:
    return [
        {"id": "read_external_closure_first", "recommendation": "Read external project closure before claiming external acceptance.", "evidence_refs": source_refs[:1], "status": "recommended" if source_refs else "needs_review"},
        {"id": "run_focused_tests", "recommendation": "Run V2.71-V2.75 focused tests before final acceptance.", "evidence_refs": source_refs, "status": "recommended" if source_refs else "needs_review"},
    ]


def _retention_policy() -> str:
    return "# Agent Memory Retention Policy\n\nProject memory is retained as persisted artifact references and must be reviewed after each phase or test run. This is not generic chat memory.\n"


def _bundle(workspace_id: str, codebase_id: str, memory: dict[str, Any], evidence: dict[str, Any], acceptance: dict[str, Any], briefing: dict[str, Any], retention: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.71-75",
        "artifact_type": "agent_long_term_memory",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "memory_index": memory,
        "evidence_index": evidence,
        "acceptance_state": acceptance,
        "task_briefing": briefing,
        "retention_policy": retention,
        "summary": {"memory_item_count": len(memory.get("items") or []), "overall_status": acceptance.get("overall_status")},
        "artifact_refs": refs,
        "warnings": list(memory.get("warnings") or []),
        "unresolved": list(memory.get("unresolved") or []),
        "next_actions": ["knowledge_code_agent_memory_release_memory_read"],
    }

