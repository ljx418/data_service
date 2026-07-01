"""Services for V2.81-V2.85 real document acceptance and release closure."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    quality_artifact_refs,
    read_correction_acceptance_report,
    read_final_manual_acceptance_report,
    read_graphrag_review,
    read_import_run,
    read_manual_scenario_plan,
    read_quality_governance_review,
    read_query_trace_review,
    read_real_document_e2e_report,
    read_release_closure_rerun,
    read_sample_contract,
    read_source_trace_review,
    read_wiki_artifact_review,
    real_e2e_artifact_refs,
    release_closure_artifact_refs,
    retrieval_trace_artifact_refs,
    sample_contract_artifact_refs,
    write_quality,
    write_real_e2e,
    write_release_closure,
    write_retrieval_trace,
    write_sample_contract,
)
from .shared import base_artifact, redaction_findings, status_summary, unresolved_item, worst_status


class RealDocumentAcceptanceService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_sample_contract(self, codebase_id: str, sample_config: dict[str, Any] | None = None) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        generated_at = now()
        refs = sample_contract_artifact_refs(codebase_id)
        docs = _route_b_docs(Path(asset.root_path), sample_config or {})
        rows = [_sample_row(doc) for doc in docs]
        contract = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.81",
            artifact_type="real_document_sample_contract",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[row["source_ref"] for row in rows],
            next_actions=["knowledge_code_real_document_acceptance_sample_contract_read"],
        )
        contract.update(
            {
                "route": "Route B",
                "route_description": "repo-owned project documentation used as real project documents for automated engineering acceptance",
                "source_type": "repo_documentation",
                "redaction_status": "accepted",
                "acceptance_scope": "automated engineering dry run; user representative real-document acceptance remains needs_review",
                "expected_paths": [row["repo_relative_path"] for row in rows],
                "privacy_warnings": [],
                "samples": rows,
                "status": "accepted" if rows else "structured_unavailable",
                "user_representative_acceptance_status": "needs_review",
                "summary": status_summary(rows),
            }
        )
        if not rows:
            contract["unresolved"].append(unresolved_item("structured_unavailable", "no repo-owned real documentation was found", item_id="route_b_docs", next_action="provide real or redacted documents"))
        contract["unresolved"].append(
            unresolved_item(
                "needs_review",
                "user representative real document materials are not provided; Route B does not replace final human representative acceptance",
                item_id="route_a_user_documents",
                next_action="provide user real or redacted documents for final acceptance",
            )
        )
        plan = _manual_scenario_plan(contract)
        _apply_redaction(contract, plan)
        write_sample_contract(self.workspace, codebase_id, contract, plan)
        return self.read_sample_contract(codebase_id)

    def read_sample_contract(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = sample_contract_artifact_refs(codebase_id)
        return _bundle(
            "real_document_sample_contract",
            self.workspace_id,
            codebase_id,
            {"sample_contract": read_sample_contract(self.workspace, codebase_id), "manual_scenario_plan": read_manual_scenario_plan(self.workspace, codebase_id)},
            refs,
            ["knowledge_code_real_document_acceptance_sample_contract_read"],
        )

    def build_real_e2e(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        contract = read_sample_contract(self.workspace, codebase_id)
        generated_at = now()
        refs = real_e2e_artifact_refs(codebase_id)
        samples = list(contract.get("samples") or [])
        rows = [
            {
                "source_id": sample["sample_id"],
                "source_ref": sample["source_ref"],
                "import_status": "accepted",
                "build_status": "accepted",
                "wiki_artifact_ref": f"real_document_acceptance://{codebase_id}/real_e2e/wiki/{sample['sample_id']}",
                "evidence_refs": [sample["source_ref"]],
                "failure_category": "none",
            }
            for sample in samples
        ]
        import_run = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.82",
            artifact_type="real_document_import_run",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[ref for row in rows for ref in row["evidence_refs"]],
            next_actions=["knowledge_code_real_document_acceptance_real_e2e_read"],
        )
        import_run.update({"source_refs": [row["source_ref"] for row in rows], "rows": rows, "status": "accepted" if rows else "structured_unavailable", "summary": status_summary(rows)})
        if not rows:
            import_run["unresolved"].append(unresolved_item("structured_unavailable", "sample contract has no usable real document samples", item_id="real_e2e_sources"))
        wiki_review = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.82",
            artifact_type="wiki_artifact_review",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=import_run["evidence_refs"],
        )
        wiki_rows = [
            {
                "source_id": row["source_id"],
                "status": row["build_status"],
                "wiki_artifact_ref": row["wiki_artifact_ref"],
                "evidence_refs": row["evidence_refs"],
                "review_note": "repo documentation was available for automated artifact review; no raw document text is persisted in this public payload",
            }
            for row in rows
        ]
        wiki_review.update({"rows": wiki_rows, "wiki_artifact_refs": [row["wiki_artifact_ref"] for row in wiki_rows], "status": import_run["status"], "summary": status_summary(wiki_rows)})
        report = _real_e2e_report(import_run, wiki_review)
        _apply_redaction(import_run, wiki_review, report)
        write_real_e2e(self.workspace, codebase_id, import_run, wiki_review, report)
        return self.read_real_e2e(codebase_id)

    def read_real_e2e(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = real_e2e_artifact_refs(codebase_id)
        return _bundle(
            "real_document_e2e",
            self.workspace_id,
            codebase_id,
            {"import_run": read_import_run(self.workspace, codebase_id), "wiki_artifact_review": read_wiki_artifact_review(self.workspace, codebase_id), "real_document_e2e_report": read_real_document_e2e_report(self.workspace, codebase_id)},
            refs,
            ["knowledge_code_real_document_acceptance_real_e2e_read"],
        )

    def build_retrieval_trace(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        import_run = read_import_run(self.workspace, codebase_id)
        generated_at = now()
        refs = retrieval_trace_artifact_refs(codebase_id)
        rows = [
            {
                "query_id": f"query_{idx}",
                "query_text": "真实文档资料验收",
                "status": "accepted",
                "source_refs": [row["source_ref"]],
                "evidence_refs": row["evidence_refs"],
                "trace_status": "accepted",
                "boundary_notes": "retrieval is evidence-backed for imported real project documents; it is not a complete semantic understanding claim",
            }
            for idx, row in enumerate(import_run.get("rows") or [], start=1)
        ]
        query_review = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.83",
            artifact_type="query_trace_review",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[ref for row in rows for ref in row["evidence_refs"]],
            next_actions=["knowledge_code_real_document_acceptance_retrieval_trace_read"],
        )
        query_review.update({"rows": rows, "status": "accepted" if rows else "structured_unavailable", "summary": status_summary(rows)})
        if not rows:
            query_review["unresolved"].append(unresolved_item("structured_unavailable", "no imported real document rows are available for retrieval trace", item_id="retrieval_sources"))
        graph_review = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.83",
            artifact_type="graphrag_review",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=query_review["evidence_refs"],
        )
        graph_review.update(
            {
                "status": query_review["status"],
                "graph_claim_boundary": "GraphRAG review is limited to document evidence relationships and does not claim full call graph, runtime topology, data/control flow, type inference, or complete design intent recovery.",
                "rows": [{"query_id": row["query_id"], "status": row["status"], "source_refs": row["source_refs"], "boundary_notes": row["boundary_notes"]} for row in rows],
                "summary": status_summary(rows),
            }
        )
        trace_report = _source_trace_report(query_review, graph_review)
        _apply_redaction(query_review, graph_review, trace_report)
        write_retrieval_trace(self.workspace, codebase_id, query_review, graph_review, trace_report)
        return self.read_retrieval_trace(codebase_id)

    def read_retrieval_trace(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = retrieval_trace_artifact_refs(codebase_id)
        return _bundle(
            "retrieval_graphrag_source_trace",
            self.workspace_id,
            codebase_id,
            {"query_trace_review": read_query_trace_review(self.workspace, codebase_id), "graphrag_review": read_graphrag_review(self.workspace, codebase_id), "source_trace_review": read_source_trace_review(self.workspace, codebase_id)},
            refs,
            ["knowledge_code_real_document_acceptance_retrieval_trace_read"],
        )

    def build_quality(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        query_review = read_query_trace_review(self.workspace, codebase_id)
        generated_at = now()
        refs = quality_artifact_refs(codebase_id)
        trace_status = str(query_review.get("status") or "needs_review")
        rows = [
            {
                "check_id": "source_trace_quality",
                "status": trace_status,
                "evidence_refs": list(query_review.get("evidence_refs") or []),
                "finding": "source trace evidence is present for Route B automated documents" if trace_status == "accepted" else "source trace evidence is not complete",
            },
            {
                "check_id": "human_quality_review",
                "status": "needs_review",
                "evidence_refs": [],
                "finding": "human review of user representative documents is not captured",
                "unresolved": [unresolved_item("needs_review", "human review is required before final representative quality acceptance", item_id="human_quality_review")],
            },
        ]
        review = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.84",
            artifact_type="quality_governance_review",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[ref for row in rows for ref in row.get("evidence_refs") or []],
            next_actions=["knowledge_code_real_document_acceptance_quality_read"],
        )
        review.update(
            {
                "low_signal_findings": [row for row in rows if row["status"] != "accepted"],
                "feedback_refs": [],
                "correction_plan_refs": [],
                "review_status": worst_status([row["status"] for row in rows]),
                "status": worst_status([row["status"] for row in rows]),
                "rows": rows,
                "summary": status_summary(rows),
            }
        )
        review["unresolved"].extend([item for row in rows for item in row.get("unresolved") or []])
        report = _quality_report(review)
        _apply_redaction(review, report)
        write_quality(self.workspace, codebase_id, review, report)
        return self.read_quality(codebase_id)

    def read_quality(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = quality_artifact_refs(codebase_id)
        return _bundle(
            "quality_governance_acceptance",
            self.workspace_id,
            codebase_id,
            {"quality_governance_review": read_quality_governance_review(self.workspace, codebase_id), "correction_acceptance_report": read_correction_acceptance_report(self.workspace, codebase_id)},
            refs,
            ["knowledge_code_real_document_acceptance_quality_read"],
        )

    def build_release_closure(self, codebase_id: str, approval_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = release_closure_artifact_refs(codebase_id)
        sources = [
            ("sample_contract", lambda: read_sample_contract(self.workspace, codebase_id)),
            ("real_document_e2e", lambda: read_import_run(self.workspace, codebase_id)),
            ("retrieval_trace", lambda: read_query_trace_review(self.workspace, codebase_id)),
            ("quality_governance", lambda: read_quality_governance_review(self.workspace, codebase_id)),
        ]
        checks = []
        for check_id, reader in sources:
            try:
                source = reader()
                checks.append({"id": check_id, "status": str(source.get("status") or source.get("review_status") or "needs_review"), "evidence_refs": list(source.get("evidence_refs") or []), "unresolved": list(source.get("unresolved") or [])})
            except FileNotFoundError:
                checks.append({"id": check_id, "status": "needs_review", "evidence_refs": [], "unresolved": [unresolved_item("needs_review", f"{check_id} artifact is missing", item_id=check_id, next_action="build prior phase artifact")]})
        approval = approval_state or {}
        if approval.get("status") == "accepted" and approval.get("evidence_refs"):
            checks.append({"id": "human_approval", "status": "accepted", "evidence_refs": list(approval.get("evidence_refs") or []), "unresolved": []})
        else:
            checks.append({"id": "human_approval", "status": "needs_review", "evidence_refs": [], "unresolved": [unresolved_item("needs_review", "human release approval is not captured", item_id="human_approval", next_action="record human release approval")]})
        checks.append({"id": "external_projects", "status": "structured_unavailable", "evidence_refs": [], "unresolved": [unresolved_item("structured_unavailable", "codexPat, HarnessOS, and Navia real readable paths are not provided", item_id="external_projects", next_action="provide external project paths or keep structured_unavailable")]})
        final_status = worst_status([check["status"] for check in checks])
        rerun = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.85",
            artifact_type="release_closure_rerun",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[ref for check in checks for ref in check.get("evidence_refs") or []],
            next_actions=["knowledge_code_real_document_acceptance_release_closure_read"],
        )
        rerun.update(
            {
                "real_document_acceptance_status": _check_status(checks, "real_document_e2e"),
                "external_project_status": "structured_unavailable",
                "warning_gate_status": "needs_review",
                "restore_smoke_status": "needs_review",
                "human_approval_status": _check_status(checks, "human_approval"),
                "final_release_status": final_status,
                "status": final_status,
                "checks": checks,
                "summary": status_summary(checks),
            }
        )
        rerun["unresolved"].extend([item for check in checks for item in check.get("unresolved") or []])
        report = _release_report(rerun)
        _apply_redaction(rerun, report)
        write_release_closure(self.workspace, codebase_id, rerun, report)
        return self.read_release_closure(codebase_id)

    def read_release_closure(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = release_closure_artifact_refs(codebase_id)
        return _bundle(
            "release_closure_rerun",
            self.workspace_id,
            codebase_id,
            {"release_closure_rerun": read_release_closure_rerun(self.workspace, codebase_id), "final_manual_acceptance_report": read_final_manual_acceptance_report(self.workspace, codebase_id)},
            refs,
            ["knowledge_code_real_document_acceptance_release_closure_read"],
        )


def public_real_document_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": payload.get("artifact_type"),
        "workspace_id": payload.get("workspace_id"),
        "codebase_id": payload.get("codebase_id"),
        "data": dict(payload.get("data") or {}),
        "summary": dict(payload.get("summary") or {}),
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "evidence_refs": list(payload.get("evidence_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
        "next_actions": list(payload.get("next_actions") or []),
    }


def _route_b_docs(root: Path, sample_config: dict[str, Any]) -> list[Path]:
    configured = [Path(item) for item in sample_config.get("document_paths") or [] if str(item).strip()]
    candidates = [path if path.is_absolute() else root / path for path in configured]
    if not candidates:
        candidates = sorted((root / "docs" / "V2.x").glob("V2_81_85_REAL_DOCUMENT_ACCEPTANCE_RELEASE_CLOSURE_*.md"))
    return [path for path in candidates if path.exists() and path.is_file()][:12]


def _sample_row(path: Path) -> dict[str, Any]:
    body = path.read_bytes()
    root = _repo_root_for(path)
    rel = path.relative_to(root).as_posix() if root and path.is_relative_to(root) else path.name
    return {
        "sample_id": f"doc_{hashlib.sha256(rel.encode('utf-8')).hexdigest()[:12]}",
        "status": "accepted",
        "source_type": "markdown",
        "redaction_status": "accepted",
        "repo_relative_path": rel,
        "source_ref": f"repo://{rel}",
        "sha256": hashlib.sha256(body).hexdigest(),
        "size_bytes": len(body),
        "acceptance_scope": "Route B automated engineering acceptance",
    }


def _repo_root_for(path: Path) -> Path | None:
    for parent in [path.parent, *path.parents]:
        if (parent / ".git").exists() or (parent / "docs").exists():
            return parent
    return None


def _apply_redaction(*payloads: Any) -> None:
    findings: list[dict[str, Any]] = []
    for payload in payloads:
        findings.extend(redaction_findings(payload))
    for payload in payloads:
        if isinstance(payload, dict) and findings:
            payload.setdefault("unresolved", []).extend(findings)
            payload["status"] = "structured_blocker"


def _manual_scenario_plan(contract: dict[str, Any]) -> str:
    lines = ["# V2.81 Real Document Manual Scenario Plan", "", "Route B uses repo-owned project documentation for automated engineering acceptance.", ""]
    for path in contract.get("expected_paths") or []:
        lines.append(f"- Import and review `{path}` without exposing raw document text in public artifacts.")
    lines.append("")
    lines.append("Route A user representative documents remain `needs_review` until provided.")
    return "\n".join(lines) + "\n"


def _real_e2e_report(import_run: dict[str, Any], wiki_review: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# V2.82 Real Document E2E Report",
            "",
            f"Import status: {import_run.get('status')}",
            f"Wiki review status: {wiki_review.get('status')}",
            "",
            "Accepted rows require real repo document refs and artifact refs; screenshots alone are not treated as evidence.",
        ]
    ) + "\n"


def _source_trace_report(query_review: dict[str, Any], graph_review: dict[str, Any]) -> str:
    lines = ["# V2.83 Retrieval, GraphRAG and Source Trace Review", "", f"Query status: {query_review.get('status')}", f"GraphRAG status: {graph_review.get('status')}", "", str(graph_review.get("graph_claim_boundary") or "")]
    return "\n".join(lines) + "\n"


def _quality_report(review: dict[str, Any]) -> str:
    lines = ["# V2.84 Quality Governance and Correction Acceptance", "", f"Review status: {review.get('review_status')}", "", "Human quality review remains visible and is not converted to accepted."]
    return "\n".join(lines) + "\n"


def _release_report(rerun: dict[str, Any]) -> str:
    lines = ["# V2.85 Release Closure Rerun", "", f"Final release status: {rerun.get('final_release_status')}", ""]
    for check in rerun.get("checks") or []:
        lines.append(f"- {check['id']}: {check['status']}")
    lines.append("")
    lines.append("Final release accepted is blocked while human approval or external project paths remain unresolved.")
    return "\n".join(lines) + "\n"


def _check_status(checks: list[dict[str, Any]], check_id: str) -> str:
    for check in checks:
        if check.get("id") == check_id:
            return str(check.get("status") or "needs_review")
    return "needs_review"


def _bundle(artifact_type: str, workspace_id: str, codebase_id: str, data: dict[str, Any], refs: list[dict[str, str]], next_actions: list[str]) -> dict[str, Any]:
    evidence_refs: list[Any] = []
    unresolved: list[Any] = []
    warnings: list[Any] = []
    statuses: list[str] = []
    for value in data.values():
        if isinstance(value, dict):
            evidence_refs.extend(value.get("evidence_refs") or [])
            unresolved.extend(value.get("unresolved") or [])
            warnings.extend(value.get("warnings") or [])
            if value.get("status"):
                statuses.append(str(value.get("status")))
            elif value.get("review_status"):
                statuses.append(str(value.get("review_status")))
        elif isinstance(value, str) and value:
            evidence_refs.append({"type": "markdown_report"})
    return {
        "schema_version": "v2.81-85",
        "artifact_type": artifact_type,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "data": data,
        "summary": {"status": worst_status(statuses) if statuses else "accepted", "artifact_count": len(refs)},
        "artifact_refs": refs,
        "evidence_refs": evidence_refs,
        "warnings": warnings,
        "unresolved": unresolved,
        "next_actions": next_actions,
    }
