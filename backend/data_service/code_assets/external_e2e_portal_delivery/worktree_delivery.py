"""Worktree delivery consolidation for V2.68."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    read_delivery_review_audit,
    read_delivery_review_manifest,
    read_delivery_review_plan,
    worktree_delivery_artifact_refs,
    write_worktree_delivery,
)
from .shared import base_artifact, redaction_findings


PHASE = "V2.68"


class WorktreeDeliveryConsolidationService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_worktree_delivery(self, codebase_id: str, repo_root: str | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = worktree_delivery_artifact_refs(codebase_id)
        files = _classify_files(Path(repo_root or "."))
        manifest = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="delivery_review_manifest",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=refs,
            next_actions=["knowledge_code_external_e2e_portal_delivery_worktree_delivery_read"],
        )
        manifest["files"] = files
        manifest["summary"] = _summary(files)
        manifest["exit_gate"] = _exit_gate(files)
        plan = _plan(files)
        audit = _audit(manifest)
        unresolved = redaction_findings(manifest) + redaction_findings(plan) + redaction_findings(audit)
        if unresolved:
            manifest["unresolved"].extend(unresolved)
        write_worktree_delivery(self.workspace, codebase_id, manifest, plan, audit)
        return _bundle(self.workspace_id, codebase_id, manifest, plan, audit, refs)

    def read_worktree_delivery(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = worktree_delivery_artifact_refs(codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            read_delivery_review_manifest(self.workspace, codebase_id),
            read_delivery_review_plan(self.workspace, codebase_id),
            read_delivery_review_audit(self.workspace, codebase_id),
            refs,
        )


def public_worktree_delivery_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "worktree_delivery_consolidation",
        "delivery_review_manifest": payload.get("delivery_review_manifest") or {},
        "delivery_review_plan": {"format": "markdown", "content": payload.get("delivery_review_plan") or ""},
        "delivery_review_audit": {"format": "markdown", "content": payload.get("delivery_review_audit") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _classify_files(root: Path) -> list[dict[str, Any]]:
    rows = _git_status_rows(root)
    if not rows and root.exists():
        rows = [("?", _repo_relative(root, path)) for path in root.rglob("*") if path.is_file()]
    files = []
    for status, path in rows:
        classification = _classification(path)
        files.append(
            {
                "path": path,
                "git_status": status,
                "classification": classification,
                "reason": _reason(path, classification),
                "safe_to_delete": False,
                "requires_human_review": classification in {"manual_review", "local_temp"},
            }
        )
    return files


def _git_status_rows(root: Path) -> list[tuple[str, str]]:
    try:
        result = subprocess.run(["git", "status", "--short"], cwd=root, check=False, capture_output=True, text=True, timeout=10)
    except Exception:
        return []
    rows = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        status = line[:2].strip() or "?"
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        rows.append((status, path))
    return sorted(rows, key=lambda item: item[1])


def _repo_relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _classification(path: str) -> str:
    if path.startswith(".tmp") or "__pycache__" in path:
        return "local_temp"
    if path.startswith("docs/V2.x/") and ("ACCEPTANCE" in path or "AUDIT" in path or "PLAN" in path or "PRD" in path or "TARGET" in path):
        return "generated_evidence"
    if path.startswith("backend/tests/") or path.startswith("backend/data_service/") or path.startswith("backend/app/api/"):
        return "commit_candidate"
    return "manual_review"


def _reason(path: str, classification: str) -> str:
    if classification == "commit_candidate":
        return "source or focused test change for review package"
    if classification == "generated_evidence":
        return "stage planning, PRD/spec review, or acceptance evidence"
    if classification == "local_temp":
        return "local cache or dependency output; deletion requires explicit human approval"
    return f"{path} ownership is not classified by this stage"


def _summary(files: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "file_count": len(files),
        "commit_candidate_count": sum(1 for item in files if item["classification"] == "commit_candidate"),
        "generated_evidence_count": sum(1 for item in files if item["classification"] == "generated_evidence"),
        "manual_review_count": sum(1 for item in files if item["classification"] == "manual_review"),
        "local_temp_count": sum(1 for item in files if item["classification"] == "local_temp"),
        "safe_to_delete_true_count": sum(1 for item in files if item.get("safe_to_delete") is True),
    }


def _exit_gate(files: list[dict[str, Any]]) -> dict[str, Any]:
    summary = _summary(files)
    status = "needs_review" if summary["manual_review_count"] or summary["local_temp_count"] else "accepted"
    return {
        "status": status,
        "reason": "manual or local temp rows require human review" if status != "accepted" else "all rows classified for review package",
        "safe_to_delete_true_count": summary["safe_to_delete_true_count"],
    }


def _plan(files: list[dict[str, Any]]) -> str:
    lines = ["# Worktree Delivery Review Plan", "", "This plan is review-only. It does not authorize deletion.", ""]
    for item in files:
        lines.append(f"- `{item['path']}`: {item['classification']}; git_status={item['git_status']}; safe_to_delete=false; {item['reason']}")
    return "\n".join(lines) + "\n"


def _audit(manifest: dict[str, Any]) -> str:
    summary = manifest.get("summary") or {}
    gate = manifest.get("exit_gate") or {}
    return "\n".join(
        [
            "# Worktree Delivery Consolidation Audit",
            "",
            f"- file_count: {summary.get('file_count', 0)}",
            f"- commit_candidate_count: {summary.get('commit_candidate_count', 0)}",
            f"- generated_evidence_count: {summary.get('generated_evidence_count', 0)}",
            f"- manual_review_count: {summary.get('manual_review_count', 0)}",
            f"- local_temp_count: {summary.get('local_temp_count', 0)}",
            f"- safe_to_delete_true_count: {summary.get('safe_to_delete_true_count', 0)}",
            f"- exit_gate: {gate.get('status')}",
            "- verdict: pass for advisory manifest; no cleanup execution performed",
            "",
        ]
    )


def _bundle(workspace_id: str, codebase_id: str, manifest: dict[str, Any], plan: str, audit: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.63-70",
        "artifact_type": "worktree_delivery_consolidation",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "delivery_review_manifest": manifest,
        "delivery_review_plan": plan,
        "delivery_review_audit": audit,
        "summary": dict(manifest.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(manifest.get("warnings") or []),
        "unresolved": list(manifest.get("unresolved") or []),
        "next_actions": ["knowledge_code_external_e2e_portal_delivery_worktree_delivery_read"],
    }
