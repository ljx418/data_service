"""Delivery cleanup and versioning for V2.65."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import delivery_artifact_refs, read_cleanup_execution_plan, read_delivery_audit_report, read_review_package_manifest, read_version_manifest, write_delivery
from .shared import base_artifact, redaction_findings


PHASE = "V2.65"


class DeliveryCleanupVersioningService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_delivery(self, codebase_id: str, repo_root: str | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = delivery_artifact_refs(codebase_id)
        root = Path(repo_root or ".")
        files = _classify_files(root)
        version = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="version_manifest", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
        version.update({"version_label": "v2.63-66-delivery", "files": files, "review_required": True})
        package = base_artifact(workspace_id=self.workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="review_package_manifest", generated_at=generated_at, artifact_refs=refs, evidence_refs=refs)
        package["files"] = files
        package["summary"] = _summary(files)
        cleanup = _cleanup_plan(files)
        audit = _audit(files)
        unresolved = redaction_findings(version) + redaction_findings(package) + redaction_findings(cleanup) + redaction_findings(audit)
        if unresolved:
            version["unresolved"].extend(unresolved)
        write_delivery(self.workspace, codebase_id, version, package, cleanup, audit)
        return _bundle(self.workspace_id, codebase_id, version, package, cleanup, audit, refs)

    def read_delivery(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = delivery_artifact_refs(codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            read_version_manifest(self.workspace, codebase_id),
            read_review_package_manifest(self.workspace, codebase_id),
            read_cleanup_execution_plan(self.workspace, codebase_id),
            read_delivery_audit_report(self.workspace, codebase_id),
            refs,
        )


def public_delivery_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "delivery_cleanup_versioning",
        "version_manifest": payload.get("version_manifest") or {},
        "review_package_manifest": payload.get("review_package_manifest") or {},
        "cleanup_execution_plan": {"format": "markdown", "content": payload.get("cleanup_execution_plan") or ""},
        "delivery_audit_report": {"format": "markdown", "content": payload.get("delivery_audit_report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _classify_files(root: Path) -> list[dict[str, Any]]:
    paths = _git_status_paths(root)
    if not paths:
        paths = [
            "backend/data_service/code_assets/external_e2e_portal_delivery",
            "docs/V2.x",
            ".tmp",
        ]
    files = []
    for rel in sorted(set(paths)):
        classification = _classification(rel)
        files.append(
            {
                "path": rel,
                "classification": classification,
                "reason": _reason(rel, classification),
                "safe_to_delete": False,
            }
        )
    return files


def _git_status_paths(root: Path) -> list[str]:
    try:
        result = subprocess.run(["git", "status", "--short"], cwd=root, check=False, capture_output=True, text=True, timeout=10)
    except Exception:
        return []
    paths = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        paths.append(path)
    return paths


def _classification(path: str) -> str:
    if path.startswith(".tmp") or "__pycache__" in path:
        return "local_temp"
    if path.startswith("docs/V2.x") or "ACCEPTANCE" in path:
        return "generated_evidence"
    if path.startswith("backend/tests") or path.startswith("backend/data_service") or path.startswith("backend/app/api"):
        return "commit_candidate"
    return "manual_review"


def _reason(path: str, classification: str) -> str:
    if classification == "local_temp":
        return "local cache or temp output; review manually before deleting"
    if classification == "generated_evidence":
        return "stage documentation or acceptance evidence"
    if classification == "commit_candidate":
        return "source or test change candidate for review"
    return f"{path} requires manual ownership review"


def _summary(files: list[dict[str, Any]]) -> dict[str, int]:
    return {
        "file_count": len(files),
        "commit_candidate_count": sum(1 for item in files if item["classification"] == "commit_candidate"),
        "generated_evidence_count": sum(1 for item in files if item["classification"] == "generated_evidence"),
        "local_temp_count": sum(1 for item in files if item["classification"] == "local_temp"),
        "manual_review_count": sum(1 for item in files if item["classification"] == "manual_review"),
        "safe_to_delete_true_count": sum(1 for item in files if item.get("safe_to_delete") is True),
    }


def _cleanup_plan(files: list[dict[str, Any]]) -> str:
    lines = ["# Cleanup Execution Plan", "", "This plan is advisory. It does not authorize deletion.", ""]
    for item in files:
        lines.append(f"- `{item['path']}`: {item['classification']}; safe_to_delete=false; {item['reason']}")
    return "\n".join(lines) + "\n"


def _audit(files: list[dict[str, Any]]) -> str:
    summary = _summary(files)
    return "\n".join(
        [
            "# Delivery Audit Report",
            "",
            f"- file_count: {summary['file_count']}",
            f"- local_temp_count: {summary['local_temp_count']}",
            f"- safe_to_delete_true_count: {summary['safe_to_delete_true_count']}",
            "- verdict: pass for advisory delivery manifest; no deletion authorized",
            "",
        ]
    )


def _bundle(workspace_id: str, codebase_id: str, version: dict[str, Any], package: dict[str, Any], cleanup: str, audit: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.63-66",
        "artifact_type": "delivery_cleanup_versioning",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "version_manifest": version,
        "review_package_manifest": package,
        "cleanup_execution_plan": cleanup,
        "delivery_audit_report": audit,
        "summary": dict(package.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(version.get("warnings") or []),
        "unresolved": list(version.get("unresolved") or []),
        "next_actions": ["knowledge_code_external_e2e_portal_delivery_delivery_read"],
    }
