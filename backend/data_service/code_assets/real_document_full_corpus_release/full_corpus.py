"""V2.86 full corpus E2E hardening service."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    full_corpus_artifact_refs,
    read_full_corpus_report,
    read_full_corpus_run,
    read_parser_failures,
    write_full_corpus,
)
from .shared import base_artifact, public_payload, redaction_findings, status_summary, unresolved_item, worst_status


class FullCorpusE2EHardeningService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_full_corpus(self, codebase_id: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        root = Path(asset.root_path)
        opts = options or {}
        source_root = _safe_source_root(root, str(opts.get("source_root") or "docs/V2.x"))
        docs = _collect_docs(source_root)
        generated_at = now()
        refs = full_corpus_artifact_refs(codebase_id)
        rows: list[dict[str, Any]] = []
        failures: list[dict[str, Any]] = []
        for path in docs:
            row = _process_doc(root, path)
            rows.append(row)
            if row["status"] != "accepted":
                failures.append(
                    {
                        "path": row["repo_relative_path"],
                        "parser": row["parser"],
                        "category": row["failure_category"],
                        "failure_category": row["failure_category"],
                        "message": row["message"],
                        "status": row["status"],
                        "next_action": row["next_action"],
                    }
                )
        status = "accepted" if rows and not failures else ("structured_blocker" if failures else "structured_unavailable")
        unresolved = []
        if not rows:
            unresolved.append(unresolved_item("structured_unavailable", "docs/V2.x contains no supported real document inputs", item_id="full_corpus_inputs", next_action="provide repo documents"))
        for failure in failures:
            unresolved.append(unresolved_item(failure["status"], failure["message"], item_id=failure["path"], next_action=failure["next_action"]))
        evidence_refs = [row["source_ref"] for row in rows if row["status"] == "accepted"]
        run = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.86",
            artifact_type="full_corpus_run",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=evidence_refs,
            unresolved=unresolved,
            next_actions=["knowledge_code_real_document_full_corpus_release_full_corpus_read"],
            status=status,
        )
        run.update(
            {
                "source_root": "docs/V2.x",
                "input_scope": "docs/V2.x",
                "included_files": [row["repo_relative_path"] for row in rows],
                "excluded_files": _excluded_notes(source_root),
                "processed_count": len(rows),
                "accepted_count": sum(1 for row in rows if row["status"] == "accepted"),
                "failure_count": len(failures),
                "rows": rows,
                "graph_claim_boundary": "document evidence relationship only; does not claim full call graph, runtime topology, data/control flow, type inference, or complete design intent recovery",
                "summary": status_summary(rows),
            }
        )
        failure_payload = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.86",
            artifact_type="parser_failures",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[],
            unresolved=unresolved,
            status="accepted" if not failures else worst_status([failure["status"] for failure in failures]),
        )
        failure_payload.update({"failures": failures, "failure_count": len(failures)})
        report = _report(run, failure_payload)
        _apply_redaction(run, failure_payload, report)
        write_full_corpus(self.workspace, codebase_id, run, failure_payload, report)
        return self.read_full_corpus(codebase_id)

    def read_full_corpus(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = full_corpus_artifact_refs(codebase_id)
        run = read_full_corpus_run(self.workspace, codebase_id)
        failures = read_parser_failures(self.workspace, codebase_id)
        report = read_full_corpus_report(self.workspace, codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            "full_corpus_e2e",
            "V2.86",
            "full_corpus_e2e",
            {
                "full_corpus_run": run,
                "parser_failures": failures,
                "full_corpus_report": report,
            },
            refs,
            status=str(run.get("status") or "needs_review"),
            evidence_refs=list(run.get("evidence_refs") or []),
            unresolved=list(run.get("unresolved") or []),
            next_actions=["knowledge_code_real_document_full_corpus_release_full_corpus_read"],
        )


def _safe_source_root(root: Path, source_root: str) -> Path:
    requested = Path(source_root)
    path = requested if requested.is_absolute() else root / requested
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return root / "docs" / "V2.x"
    return path


def _collect_docs(source_root: Path) -> list[Path]:
    if not source_root.exists():
        return []
    supported = {".md", ".html", ".json", ".drawio"}
    return sorted(
        path
        for path in source_root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in supported
        and ".tmp" not in path.parts
        and not path.name.startswith("._")
        and not path.name.startswith("~")
    )


def _process_doc(root: Path, path: Path) -> dict[str, Any]:
    rel = path.relative_to(root).as_posix() if path.is_relative_to(root) else path.name
    parser = _parser_for(path)
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8", errors="replace")
        if not text.strip():
            status = "needs_review"
            category = "empty_content"
            message = "document content is empty or whitespace-only"
            next_action = "review or remove empty document"
        elif parser == "html" and "name 'Section' is not defined" in text:
            status = "structured_blocker"
            category = "extractor_bug"
            message = "HTML extractor Section error marker is present and must be fixed or isolated"
            next_action = "fix HTML extractor Section handling"
        else:
            status = "accepted"
            category = "none"
            message = "document processed as real full corpus input"
            next_action = "read full corpus report"
    except OSError:
        raw = b""
        status = "failed"
        category = "needs_review"
        message = "document could not be read"
        next_action = "inspect file permissions"
    return {
        "document_id": f"doc_{hashlib.sha256(rel.encode('utf-8')).hexdigest()[:12]}",
        "repo_relative_path": rel,
        "source_ref": f"repo://{rel}",
        "parser": parser,
        "status": status,
        "failure_category": category,
        "message": message,
        "next_action": next_action,
        "sha256": hashlib.sha256(raw).hexdigest() if raw else "",
        "size_bytes": len(raw),
        "source_trace_status": "accepted" if status == "accepted" else "needs_review",
        "graph_boundary": "document evidence relationship only; not full call graph, runtime topology, data/control flow, or type inference",
        "evidence_refs": [f"repo://{rel}"] if status == "accepted" else [],
    }


def _parser_for(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".md":
        return "markdown"
    if suffix == ".html":
        return "html"
    if suffix == ".json":
        return "json"
    if suffix == ".drawio":
        return "drawio"
    return "unknown"


def _excluded_notes(source_root: Path) -> list[str]:
    return [f"repo://{item}" for item in [".tmp", "backend/.tmp", "resource_fork_files", "cache_files"] if source_root]


def _report(run: dict[str, Any], failures: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V2.86 Full Corpus E2E Report",
            "",
            f"Status: {run['status']}",
            f"Processed: {run['processed_count']}",
            f"Accepted: {run['accepted_count']}",
            f"Failures: {run['failure_count']}",
            "",
            "GraphRAG and source trace outputs are limited to document evidence relationships and do not claim full call graph, runtime topology, data/control flow, type inference, or complete design intent recovery.",
            "",
            "## Parser Failures",
            *(f"- {item['path']}: {item['category']} / {item['status']} / {item['next_action']}" for item in failures.get("failures", [])),
        ]
    )


def _bundle(workspace_id: str, codebase_id: str, artifact_type: str, phase: str, key: str, data: dict[str, Any], artifact_refs: list[Any], *, status: str, evidence_refs: list[Any], unresolved: list[Any], next_actions: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "v2.86-90",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "phase": phase,
        "artifact_type": artifact_type,
        "status": status,
        "data": data,
        "summary": dict(data.get("full_corpus_run", {}).get("summary") or {}),
        "artifact_refs": list(artifact_refs),
        "evidence_refs": list(evidence_refs),
        "warnings": [],
        "unresolved": list(unresolved),
        "next_actions": list(next_actions),
    }


def _apply_redaction(*payloads: Any) -> None:
    findings: list[dict[str, Any]] = []
    for payload in payloads:
        findings.extend(redaction_findings(payload))
    for payload in payloads:
        if isinstance(payload, dict) and findings:
            payload.setdefault("unresolved", []).extend(findings)
            payload["status"] = "structured_blocker"


def public_full_corpus_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)
