"""Agent task workflow hardening for V2.55."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..agent_productization.persistence import read_playbook_json
from ..agent_productization.task_navigation import AgentTaskNavigationService, FORBIDDEN_CLAIM_TYPES
from ..registry import CodebaseRegistry
from .persistence import (
    agent_task_workflow_artifact_refs,
    read_project_story,
    read_risk_priority,
    read_stop_conditions,
    read_task_workflow_markdown,
    read_task_workflow_suggested_tests,
    read_workflow_bundle,
    write_agent_task_workflow,
)
from .shared import base_artifact, needs_review, redaction_findings, structured_unavailable


PHASE = "V2.55"
DEFAULT_MAX_TOKENS = 4000
SKIP_DIRS = {".git", ".tmp", ".venv", "venv", "node_modules", "dist", "build", "__pycache__", ".pytest_cache", ".mypy_cache"}
SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".swift", ".kt"}
DOC_SUFFIXES = {".md", ".mdx", ".rst", ".drawio"}


class AgentTaskWorkflowService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_task_workflow(self, codebase_id: str, *, task: str, max_tokens: int = DEFAULT_MAX_TOKENS) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        task_text = str(task or "").strip()
        if not task_text:
            raise ValueError("TASK_REQUIRED")

        navigation = AgentTaskNavigationService(self.workspace, workspace_id=self.workspace_id).build_task_navigation(codebase_id, task=task_text)
        task_id = str(navigation["task_id"])
        generated_at = now()
        refs = agent_task_workflow_artifact_refs(codebase_id, task_id)
        sources = self._load_sources(codebase_id)

        fallback_candidates = _fallback_repo_candidates(Path(asset.root_path).expanduser(), task_text)
        reading_items, omitted_items = _bounded_reading_items(navigation.get("reading_order", {}).get("items") or [], max_tokens=max_tokens)
        if not reading_items and fallback_candidates:
            reading_items, fallback_omitted = _bounded_reading_items(_fallback_reading_items(fallback_candidates), max_tokens=max_tokens)
            omitted_items.extend(fallback_omitted)
        impact_candidates = _impact_candidates(navigation.get("task_impact", {}).get("impact_candidates") or [])
        if not impact_candidates and fallback_candidates:
            impact_candidates = _impact_candidates(_fallback_impact_candidates(fallback_candidates))
        raw_tests = list(navigation.get("suggested_tests", {}).get("tests") or [])
        if not any(_allowed_candidate_path(item.get("path")) for item in raw_tests):
            raw_tests = _fallback_suggested_tests(fallback_candidates)
        suggested_tests = _suggested_tests_artifact(
            self.workspace_id,
            codebase_id,
            task_id,
            generated_at,
            refs,
            raw_tests,
        )
        stop_conditions = _stop_conditions_artifact(self.workspace_id, codebase_id, task_id, generated_at, refs)
        recommendations = _recommendations(sources, navigation)
        unresolved = [
            *list(navigation.get("unresolved") or []),
            *list(sources["unresolved"]),
            *list(suggested_tests.get("unresolved") or []),
        ]
        warnings = [*list(sources["warnings"])]
        workflow_bundle = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="agent_task_workflow_bundle",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=_source_refs(sources, navigation),
            warnings=warnings,
            unresolved=unresolved,
        )
        workflow_bundle.update(
            {
                "task_id": task_id,
                "task_summary": {"task": task_text, "source": "user_supplied_task"},
                "reading_order": reading_items,
                "impact_candidates": impact_candidates,
                "suggested_tests": [{"command": item["command"], "status": item["status"], "evidence_refs": item["evidence_refs"]} for item in suggested_tests["tests"]],
                "stop_conditions": stop_conditions["conditions"],
                "recommendations": recommendations,
                "omitted_items": omitted_items,
                "constraints": [
                    "Impact candidates are static candidates only, not deterministic runtime calls.",
                    "Do not modify protected legacy files without explicit approval.",
                    "Do not count mock-only or unavailable evidence as accepted.",
                ],
                "summary": {
                    "reading_item_count": len(reading_items),
                    "impact_candidate_count": len(impact_candidates),
                    "suggested_test_count": len(suggested_tests["tests"]),
                    "omitted_item_count": len(omitted_items),
                    "recommendation_count": len(recommendations),
                },
            }
        )
        redaction = redaction_findings(workflow_bundle) + redaction_findings(stop_conditions) + redaction_findings(suggested_tests)
        if redaction:
            workflow_bundle["unresolved"].extend(redaction)
        markdown = _render_markdown(workflow_bundle, stop_conditions, suggested_tests)
        write_agent_task_workflow(self.workspace, codebase_id, task_id, workflow_bundle, stop_conditions, suggested_tests, markdown)
        return _bundle(self.workspace_id, codebase_id, task_id, workflow_bundle, stop_conditions, suggested_tests, markdown, refs)

    def read_task_workflow(self, codebase_id: str, *, task_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        task_key = str(task_id or "").strip()
        if not task_key:
            raise FileNotFoundError("AGENT_TASK_WORKFLOW_NOT_BUILT")
        refs = agent_task_workflow_artifact_refs(codebase_id, task_key)
        workflow_bundle = read_workflow_bundle(self.workspace, codebase_id, task_key)
        stop_conditions = read_stop_conditions(self.workspace, codebase_id, task_key)
        suggested_tests = read_task_workflow_suggested_tests(self.workspace, codebase_id, task_key)
        markdown = read_task_workflow_markdown(self.workspace, codebase_id, task_key)
        return _bundle(self.workspace_id, codebase_id, task_key, workflow_bundle, stop_conditions, suggested_tests, markdown, refs)

    def _load_sources(self, codebase_id: str) -> dict[str, Any]:
        warnings = []
        unresolved = []

        def optional(name: str, reader):
            try:
                return reader(self.workspace, codebase_id)
            except FileNotFoundError as exc:
                unresolved.append(structured_unavailable(name, str(exc)))
                return {}

        playbook = optional("coding_agent_playbook", lambda workspace, cid: read_playbook_json(workspace, cid, "coding_agent"))
        project_story = optional("human_portal_project_story", read_project_story)
        risk_priority = optional("human_portal_risk_priority", read_risk_priority)
        if unresolved:
            warnings.append("AGENT_TASK_WORKFLOW_SOURCE_PARTIAL")
        return {
            "playbook": playbook,
            "project_story": project_story,
            "risk_priority": risk_priority,
            "warnings": warnings,
            "unresolved": unresolved,
        }


def public_agent_task_workflow_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "agent_task_workflow",
        "task_id": payload.get("task_id"),
        "workflow_bundle": payload.get("workflow_bundle") or {},
        "stop_conditions": payload.get("stop_conditions") or {},
        "suggested_tests": payload.get("suggested_tests") or {},
        "markdown": {"format": "markdown", "content": payload.get("markdown") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _bundle(
    workspace_id: str,
    codebase_id: str,
    task_id: str,
    workflow_bundle: dict[str, Any],
    stop_conditions: dict[str, Any],
    suggested_tests: dict[str, Any],
    markdown: str,
    refs: list[dict[str, str]],
) -> dict[str, Any]:
    unresolved = [*list(workflow_bundle.get("unresolved") or []), *list(stop_conditions.get("unresolved") or []), *list(suggested_tests.get("unresolved") or [])]
    warnings = [*list(workflow_bundle.get("warnings") or []), *list(stop_conditions.get("warnings") or []), *list(suggested_tests.get("warnings") or [])]
    return {
        "schema_version": "v2.54-58",
        "artifact_type": "agent_task_workflow",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "task_id": task_id,
        "workflow_bundle": workflow_bundle,
        "stop_conditions": stop_conditions,
        "suggested_tests": suggested_tests,
        "markdown": markdown,
        "summary": dict(workflow_bundle.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": warnings,
        "unresolved": unresolved,
        "next_actions": ["knowledge_code_human_agent_deepening_task_workflow_read"],
    }


def _bounded_reading_items(items: list[dict[str, Any]], *, max_tokens: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    budget = max(120, int(max_tokens or DEFAULT_MAX_TOKENS))
    kept = []
    omitted = []
    used = 0
    for item in items:
        if not _allowed_candidate_path(item.get("path")):
            omitted.append({"item_id": item.get("path"), "reason": "ephemeral_or_dependency_path", "estimated_tokens": int(item.get("token_estimate") or 0)})
            continue
        estimate = int(item.get("token_estimate") or 120)
        row = {
            "order": len(kept) + 1,
            "path": item.get("path"),
            "reason": item.get("reason"),
            "evidence_refs": list(item.get("evidence_refs") or []),
            "token_estimate": estimate,
        }
        if kept and used + estimate > budget:
            omitted.append({"item_id": item.get("path"), "reason": "token_budget", "estimated_tokens": estimate})
            continue
        kept.append(row)
        used += estimate
    return kept, omitted


def _impact_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for item in candidates:
        if not _allowed_candidate_path(item.get("path")):
            continue
        claim_type = str(item.get("claim_type") or "heuristic_candidate")
        if claim_type in FORBIDDEN_CLAIM_TYPES:
            claim_type = "needs_review"
        rows.append(
            {
                "path": item.get("path"),
                "impact_type": item.get("impact_type"),
                "claim_type": claim_type,
                "candidate_kind": "static_candidate",
                "confidence": item.get("confidence"),
                "reason": item.get("reason"),
                "evidence_refs": list(item.get("evidence_refs") or []),
                "needs_review": bool(item.get("needs_review") or not item.get("evidence_refs")),
            }
        )
    return rows


def _suggested_tests_artifact(workspace_id: str, codebase_id: str, task_id: str, generated_at: str, refs: list[dict[str, str]], tests: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    unresolved = []
    for item in tests:
        if not _allowed_candidate_path(item.get("path")):
            continue
        evidence_refs = list(item.get("evidence_refs") or [])
        status = "recommended" if evidence_refs and not item.get("needs_review") else "needs_review"
        rows.append(
            {
                "command": item.get("command_hint") or "manual review required",
                "scope": item.get("path") or "unknown",
                "confidence": "medium" if status == "recommended" else "low",
                "evidence_refs": evidence_refs,
                "status": status,
                "reason": item.get("reason") or "",
            }
        )
    if not rows:
        unresolved.append(structured_unavailable("suggested_tests", "no suggested tests available from task navigation"))
    payload = base_artifact(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        phase=PHASE,
        artifact_type="agent_task_workflow_suggested_tests",
        generated_at=generated_at,
        artifact_refs=refs,
        evidence_refs=[ref for item in rows for ref in item["evidence_refs"]],
        unresolved=unresolved,
    )
    payload.update({"task_id": task_id, "tests": rows})
    return payload


def _allowed_candidate_path(path: Any) -> bool:
    text = str(path or "")
    if not text:
        return False
    blocked_prefixes = (
        ".tmp/",
        ".venv/",
        "venv/",
        "node_modules/",
        "dist/",
        "build/",
        "__pycache__/",
        ".pytest_cache/",
        ".mypy_cache/",
    )
    return not text.startswith(blocked_prefixes) and "/node_modules/" not in text and "/.tmp/" not in text


def _fallback_repo_candidates(repo_root: Path, task: str) -> list[dict[str, Any]]:
    if not repo_root.exists() or not repo_root.is_dir():
        return []
    tokens = [token.lower() for token in task.replace("_", " ").replace("-", " ").split() if len(token) >= 3]
    candidates = []
    for path in repo_root.rglob("*"):
        if len(candidates) >= 1200:
            break
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        rel = str(path.relative_to(repo_root))
        if suffix not in SOURCE_SUFFIXES and suffix not in DOC_SUFFIXES and "test" not in rel.lower():
            continue
        lower = rel.lower()
        score = sum(4 for token in tokens if token in lower)
        if lower.startswith("backend/tests/") or lower.startswith("tests/"):
            score += 3
        if lower.startswith("backend/data_service/") or lower.startswith("src/"):
            score += 2
        if lower.startswith("docs/"):
            score += 1
        if score <= 0 and len(candidates) > 80:
            continue
        candidates.append(
            {
                "path": rel,
                "score": score,
                "reason": "fallback non-ephemeral task candidate" if score > 0 else "fallback non-ephemeral project candidate",
                "confidence": min(0.82, 0.35 + score * 0.07),
            }
        )
    return sorted(candidates, key=lambda item: (-int(item["score"]), item["path"]))[:20]


def _fallback_reading_items(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "path": item["path"],
            "reason": item["reason"],
            "token_estimate": 600,
            "evidence_refs": [f"repo://{item['path']}"],
        }
        for item in candidates[:10]
    ]


def _fallback_impact_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "path": item["path"],
            "impact_type": "test_candidate" if "test" in item["path"].lower() else ("documentation_candidate" if item["path"].lower().startswith("docs/") else "source_candidate"),
            "claim_type": "heuristic_candidate",
            "confidence": item["confidence"],
            "reason": item["reason"],
            "evidence_refs": [f"repo://{item['path']}"],
            "needs_review": item["confidence"] < 0.8,
        }
        for item in candidates[:12]
    ]


def _fallback_suggested_tests(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    tests = [item for item in candidates if "test" in item["path"].lower()][:8]
    if not tests:
        tests = candidates[:3]
    rows = []
    for item in tests:
        is_test = "test" in item["path"].lower()
        rows.append(
            {
                "path": item["path"],
                "command_hint": f"pytest -q {item['path']}" if item["path"].endswith(".py") and is_test else "run project-specific tests",
                "reason": "fallback non-ephemeral test candidate" if is_test else "fallback source candidate; review before selecting test",
                "evidence_refs": [f"repo://{item['path']}"] if is_test else [],
                "needs_review": not is_test,
            }
        )
    return rows


def _stop_conditions_artifact(workspace_id: str, codebase_id: str, task_id: str, generated_at: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    conditions = [
        {
            "id": "unsupported_accepted_claim",
            "trigger": "A recommendation or acceptance row has no evidence and is not marked needs_review.",
            "required_action": "Stop and move the item to needs_review or collect evidence before continuing.",
        },
        {
            "id": "protected_legacy_mutation",
            "trigger": "A change would modify backend/app/api/v1/data_service.py or backend/data_service/service.py without explicit approval.",
            "required_action": "Stop and request human approval.",
        },
        {
            "id": "mock_only_acceptance",
            "trigger": "Only mock data is available for a row that requires real-project E2E.",
            "required_action": "Stop and record needs_review or structured_unavailable; do not mark accepted.",
        },
        {
            "id": "private_path_leak",
            "trigger": "Public payload contains local absolute path, secret, token, or raw traceback.",
            "required_action": "Stop, redact, and rerun focused tests.",
        },
        {
            "id": "static_analysis_overclaim",
            "trigger": "Impact candidates are described as runtime calls, data flow, control flow, production topology, or type inference.",
            "required_action": "Stop and relabel the item as static candidate or needs_review.",
        },
    ]
    payload = base_artifact(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        phase=PHASE,
        artifact_type="agent_task_workflow_stop_conditions",
        generated_at=generated_at,
        artifact_refs=refs,
        evidence_refs=[],
    )
    payload.update({"task_id": task_id, "conditions": conditions})
    return payload


def _recommendations(sources: dict[str, Any], navigation: dict[str, Any]) -> list[dict[str, Any]]:
    refs = _source_refs(sources, navigation)
    recs = [
        {
            "id": "read_bounded_context_first",
            "text": "Read the task workflow reading order before editing files.",
            "evidence_refs": refs[:2],
            "needs_review": not bool(refs[:2]),
        },
        {
            "id": "treat_impact_as_candidates",
            "text": "Treat impact entries as bounded static candidates, not runtime call evidence.",
            "evidence_refs": refs[:1],
            "needs_review": False,
        },
        {
            "id": "run_evidence_backed_tests",
            "text": "Run suggested tests that carry evidence refs; review low-confidence suggestions before relying on them.",
            "evidence_refs": refs[:2],
            "needs_review": not bool(refs[:2]),
        },
    ]
    playbook_recs = list((sources.get("playbook") or {}).get("recommendations") or [])[:3]
    for item in playbook_recs:
        evidence_refs = list(item.get("evidence_refs") or [])
        recs.append(
            {
                "id": f"playbook_{item.get('recommendation_id')}",
                "text": item.get("text") or "",
                "evidence_refs": evidence_refs,
                "needs_review": bool(item.get("needs_review") or not evidence_refs),
            }
        )
    for item in recs:
        if not item["evidence_refs"] and not item["needs_review"]:
            item["needs_review"] = True
    return recs


def _source_refs(sources: dict[str, Any], navigation: dict[str, Any]) -> list[dict[str, Any]]:
    refs = []
    refs.extend(list(navigation.get("artifact_refs") or []))
    for key in ("playbook", "project_story", "risk_priority"):
        refs.extend(list((sources.get(key) or {}).get("artifact_refs") or []))
    return refs


def _render_markdown(workflow: dict[str, Any], stop_conditions: dict[str, Any], suggested_tests: dict[str, Any]) -> str:
    lines = [
        "# Agent Task Workflow",
        "",
        f"- task_id: `{workflow['task_id']}`",
        f"- task: {workflow['task_summary']['task']}",
        "",
        "## Reading Order",
    ]
    for item in workflow.get("reading_order", []):
        lines.append(f"- {item['order']}. `{item['path']}` - {item['reason']}")
    lines.extend(["", "## Impact Candidates"])
    for item in workflow.get("impact_candidates", []):
        lines.append(f"- `{item['path']}` ({item['candidate_kind']}, {item['claim_type']}): {item['reason']}")
    lines.extend(["", "## Suggested Tests"])
    for item in suggested_tests.get("tests", []):
        lines.append(f"- `{item['command']}` - {item['status']} - {item['scope']}")
    lines.extend(["", "## Stop Conditions"])
    for item in stop_conditions.get("conditions", []):
        lines.append(f"- **{item['id']}**: {item['trigger']} Required action: {item['required_action']}")
    if workflow.get("omitted_items"):
        lines.extend(["", "## Omitted Items"])
        for item in workflow["omitted_items"]:
            lines.append(f"- `{item['item_id']}` omitted due to {item['reason']}")
    return "\n".join(lines) + "\n"
