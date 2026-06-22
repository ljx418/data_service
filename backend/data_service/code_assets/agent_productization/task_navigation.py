"""Task navigation and impact candidates for V2.49."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .mcp_usage import AGENT_PRODUCTIZATION_SCHEMA_VERSION
from .persistence import (
    read_suggested_tests,
    read_task_impact,
    read_task_reading_order,
    task_navigation_artifact_refs,
    write_task_navigation,
)


SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "build", "__pycache__", ".pytest_cache", ".mypy_cache"}
SOURCE_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".swift", ".kt"}
DOC_SUFFIXES = {".md", ".mdx", ".rst", ".drawio"}
TEST_HINTS = ("test", "spec")
FORBIDDEN_CLAIM_TYPES = {"runtime_call", "data_flow", "control_flow", "production_topology"}


class AgentTaskNavigationService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_task_navigation(self, codebase_id: str, *, task: str) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        task_text = str(task or "").strip()
        if not task_text:
            raise ValueError("TASK_REQUIRED")
        task_id = _stable_id("task", codebase_id, task_text)
        refs = task_navigation_artifact_refs(codebase_id, task_id)
        created_at = now()
        repo_root = Path(asset.root_path).expanduser()
        if not repo_root.exists() or not repo_root.is_dir():
            reading_order = _unavailable("reading_order", self.workspace_id, codebase_id, task_id, created_at)
            task_impact = _unavailable("task_impact", self.workspace_id, codebase_id, task_id, created_at)
            suggested_tests = _unavailable("suggested_tests", self.workspace_id, codebase_id, task_id, created_at)
            write_task_navigation(self.workspace, codebase_id, task_id, reading_order, task_impact, suggested_tests)
            return _bundle(self.workspace_id, codebase_id, task_id, task_text, reading_order, task_impact, suggested_tests, refs)

        files = _candidate_files(repo_root)
        tokens = _tokens(task_text)
        ranked = _rank_files(repo_root, files, tokens)
        tests = [item for item in ranked if _is_test(item["path"])]
        reading_order = _reading_order(self.workspace_id, codebase_id, task_id, task_text, ranked, created_at)
        task_impact = _task_impact(self.workspace_id, codebase_id, task_id, task_text, ranked, created_at)
        suggested_tests = _suggested_tests(self.workspace_id, codebase_id, task_id, tests, ranked, created_at)
        write_task_navigation(self.workspace, codebase_id, task_id, reading_order, task_impact, suggested_tests)
        return _bundle(self.workspace_id, codebase_id, task_id, task_text, reading_order, task_impact, suggested_tests, refs)

    def read_task_navigation(self, codebase_id: str, *, task_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        task_key = str(task_id or "").strip()
        if not task_key:
            raise FileNotFoundError("TASK_NAVIGATION_NOT_BUILT")
        refs = task_navigation_artifact_refs(codebase_id, task_key)
        reading_order = read_task_reading_order(self.workspace, codebase_id, task_key)
        task_impact = read_task_impact(self.workspace, codebase_id, task_key)
        suggested_tests = read_suggested_tests(self.workspace, codebase_id, task_key)
        return _bundle(self.workspace_id, codebase_id, task_key, str(reading_order.get("task") or ""), reading_order, task_impact, suggested_tests, refs)


def public_task_navigation_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "artifact_type": "task_navigation_and_impact",
        "task_id": payload.get("task_id"),
        "task": payload.get("task"),
        "reading_order": payload.get("reading_order") or {},
        "task_impact": payload.get("task_impact") or {},
        "suggested_tests": payload.get("suggested_tests") or {},
        "summary": dict(payload.get("summary") or {}),
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _bundle(
    workspace_id: str,
    codebase_id: str,
    task_id: str,
    task: str,
    reading_order: dict[str, Any],
    task_impact: dict[str, Any],
    suggested_tests: dict[str, Any],
    refs: list[dict[str, str]],
) -> dict[str, Any]:
    unresolved = []
    for artifact in (reading_order, task_impact, suggested_tests):
        unresolved.extend(artifact.get("unresolved") or [])
    candidates = list(task_impact.get("impact_candidates") or [])
    forbidden = [item for item in candidates if item.get("claim_type") in FORBIDDEN_CLAIM_TYPES]
    if forbidden:
        unresolved.append({"code": "FORBIDDEN_IMPACT_CLAIM", "count": len(forbidden)})
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "task_id": task_id,
        "task": task,
        "reading_order": reading_order,
        "task_impact": task_impact,
        "suggested_tests": suggested_tests,
        "summary": {
            "reading_item_count": len(reading_order.get("items") or []),
            "impact_candidate_count": len(candidates),
            "suggested_test_count": len(suggested_tests.get("tests") or []),
            "forbidden_claim_count": len(forbidden),
        },
        "artifact_refs": refs,
        "warnings": [],
        "unresolved": unresolved,
        "next_actions": ["knowledge_code_agent_productization_task_navigation_read"],
    }


def _reading_order(workspace_id: str, codebase_id: str, task_id: str, task: str, ranked: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    items = []
    for index, item in enumerate(ranked[:12], start=1):
        items.append(
            {
                "order": index,
                "path": item["path"],
                "reason": item["reason"],
                "token_estimate": max(40, min(1200, item.get("size", 0) // 4)),
                "evidence_refs": [f"repo://{item['path']}"],
            }
        )
    return {
        **_base(workspace_id, codebase_id, task_id, created_at),
        "artifact_type": "reading_order",
        "task": task,
        "items": items,
        "bounded": True,
        "unresolved": [] if items else [{"code": "NO_READING_ORDER_CANDIDATES", "reason": "no matching source/doc/test files"}],
    }


def _task_impact(workspace_id: str, codebase_id: str, task_id: str, task: str, ranked: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    candidates = []
    for item in ranked[:12]:
        candidates.append(
            {
                "path": item["path"],
                "impact_type": _impact_type(item["path"]),
                "claim_type": "heuristic_candidate",
                "match_strategy": item.get("match_strategy", "path_token_match"),
                "confidence": item.get("confidence", 0.45),
                "reason": item["reason"],
                "evidence_refs": [f"repo://{item['path']}"],
                "needs_review": item.get("confidence", 0.0) < 0.8,
            }
        )
    return {
        **_base(workspace_id, codebase_id, task_id, created_at),
        "artifact_type": "task_impact",
        "task": task,
        "impact_candidates": candidates,
        "forbidden_claim_types": sorted(FORBIDDEN_CLAIM_TYPES),
        "unresolved": [] if candidates else [{"code": "NO_IMPACT_CANDIDATES", "reason": "no matching files"}],
    }


def _suggested_tests(workspace_id: str, codebase_id: str, task_id: str, tests: list[dict[str, Any]], ranked: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    selected = tests[:8]
    if not selected:
        selected = [item for item in ranked if item["path"].endswith((".py", ".ts", ".tsx", ".js", ".jsx"))][:3]
    rows = []
    for item in selected:
        is_test = _is_test(item["path"])
        rows.append(
            {
                "path": item["path"],
                "command_hint": _command_hint(item["path"], is_test=is_test),
                "reason": "matched test file" if is_test else "no direct test found; review related source before choosing test",
                "evidence_refs": [f"repo://{item['path']}"] if is_test else [],
                "needs_review": not is_test,
            }
        )
    return {
        **_base(workspace_id, codebase_id, task_id, created_at),
        "artifact_type": "suggested_tests",
        "tests": rows,
        "unresolved": [] if rows else [{"code": "NO_TEST_SUGGESTIONS", "reason": "no test or source candidate found"}],
    }


def _candidate_files(repo_root: Path) -> list[Path]:
    files = []
    for item in repo_root.rglob("*"):
        if len(files) >= 1800:
            break
        if any(part in SKIP_DIRS for part in item.parts):
            continue
        if item.is_file() and (item.suffix.lower() in SOURCE_SUFFIXES or item.suffix.lower() in DOC_SUFFIXES or _is_test(str(item))):
            files.append(item)
    return files


def _rank_files(repo_root: Path, files: list[Path], tokens: list[str]) -> list[dict[str, Any]]:
    ranked = []
    for file_path in files:
        rel = str(file_path.relative_to(repo_root))
        lower = rel.lower()
        score = 0
        for token in tokens:
            if token in lower:
                score += 4
        if rel.lower().startswith("docs/"):
            score += 2
        if _is_test(rel):
            score += 2
        if file_path.suffix.lower() in SOURCE_SUFFIXES:
            score += 1
        if score <= 0 and len(ranked) > 40:
            continue
        size = file_path.stat().st_size if file_path.exists() else 0
        ranked.append(
            {
                "path": rel,
                "score": score,
                "size": size,
                "confidence": min(0.9, 0.35 + score * 0.08),
                "match_strategy": "task_token_path_match" if score > 0 else "fallback_relevant_file",
                "reason": "path tokens match task" if score > 0 else "fallback bounded project reading candidate",
            }
        )
    return sorted(ranked, key=lambda item: (-int(item["score"]), item["path"]))[:40]


def _tokens(task: str) -> list[str]:
    return [token.lower() for token in re.split(r"[^A-Za-z0-9]+", task) if len(token) >= 3]


def _is_test(path: str) -> bool:
    lower = path.lower()
    return any(hint in lower for hint in TEST_HINTS)


def _impact_type(path: str) -> str:
    lower = path.lower()
    if lower.startswith("docs/") or lower.endswith(tuple(DOC_SUFFIXES)):
        return "documentation_candidate"
    if _is_test(path):
        return "test_candidate"
    return "source_candidate"


def _command_hint(path: str, *, is_test: bool) -> str:
    if path.endswith(".py"):
        return f"pytest -q {path}" if is_test else "pytest -q"
    if path.endswith((".ts", ".tsx", ".js", ".jsx")):
        return "npm test"
    return "run project-specific tests"


def _unavailable(artifact_type: str, workspace_id: str, codebase_id: str, task_id: str, created_at: str) -> dict[str, Any]:
    return {
        **_base(workspace_id, codebase_id, task_id, created_at),
        "artifact_type": artifact_type,
        "status": "structured_unavailable",
        "unresolved": [{"code": "PROJECT_REPO_UNAVAILABLE", "reason": "registered codebase root is missing or not a directory"}],
    }


def _base(workspace_id: str, codebase_id: str, task_id: str, created_at: str) -> dict[str, Any]:
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "task_id": task_id,
        "created_at": created_at,
    }


def _stable_id(*parts: str) -> str:
    text = ":".join(str(part or "") for part in parts)
    return f"task_{hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]}"
