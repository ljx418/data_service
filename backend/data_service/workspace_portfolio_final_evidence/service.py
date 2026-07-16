"""V2.106-V2.110 final evidence closure service for workspace portfolio."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
import shutil
from typing import Any

from data_service.mcp_common import read_json
from data_service.workspace_portfolio import WorkspacePortfolioService

from .persistence import artifact_path, optional_artifact, read_artifact, read_text_artifact, write_artifact, write_text_artifact
from .shared import (
    SCHEMA_VERSION,
    artifact_ref,
    base_artifact,
    digest_value,
    file_hash,
    run_id_for,
    safe_path_ref,
    slug,
    status_counts,
    unresolved,
    worst_acceptance_status,
)


ARTIFACT_FILES = [
    "baseline_evidence_manifest.json",
    "coverage_state_closure.json",
    "architecture_state_closure.json",
    "ocr_provider_health.json",
    "media_evidence_matrix.json",
    "full_build_queue.json",
    "project_build_diagnosis.json",
    "document_source_trace_closure.json",
    "ui_evidence_capture.json",
    "final_release_gate.json",
    "false_green_recheck.md",
    "final_evidence_report.html",
]

BASELINE_ARTIFACT_FILES = [
    "project_registry.json",
    "source_candidate_matrix.json",
    "media_readiness.json",
    "project_build_runs.json",
    "portfolio_index.json",
    "release_gate.json",
    "false_green_audit.md",
    "portfolio_report.html",
]

DOC_BASELINE_FILES = [
    "docs/V2.x/V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_FULL_COVERAGE_MATRIX.md",
    "docs/V2.x/V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_ACCEPTANCE_AUDIT_REPORT.md",
    "docs/V2.x/V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_AUTOMATED_VISUAL_ACCEPTANCE_REPORT.html",
    "docs/V2.x/V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_PRD.md",
    "docs/V2.x/V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_TARGET_ARCHITECTURE.md",
    "docs/V2.x/V2_106_110_WORKSPACE_PORTFOLIO_FINAL_EVIDENCE_CLOSURE_TARGET_STATE.drawio",
]


class WorkspacePortfolioFinalEvidenceService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id

    def plan(self, *, root: str | Path = "/mnt/c/workspace", limit: int = 120) -> dict[str, Any]:
        root_path = Path(root).expanduser().resolve()
        registry = WorkspacePortfolioService(self.workspace, workspace_id=self.workspace_id).scan(root=root_path, limit=limit)
        baseline = self._baseline_manifest(root_path=root_path, run_id="plan", workspace_fingerprint="plan")
        plan_payload = {
            "ok": True,
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "phase": "V2.106-V2.110",
            "status": "needs_review",
            "data": {
                "project_count": ((registry.get("data") or {}).get("project_registry") or {}).get("summary", {}).get("project_count", 0),
                "baseline": baseline,
                "planned_artifacts": [artifact_ref("final_evidence", filename) for filename in ARTIFACT_FILES],
            },
            "artifact_refs": [artifact_ref("project_registry", "project_registry.json")],
            "evidence_refs": baseline.get("evidence_refs", []),
            "warnings": ["plan does not claim implementation acceptance"],
            "unresolved": [
                unresolved(
                    "needs_review",
                    "phase plan is ready; build artifacts and focused tests are required before acceptance",
                    item_id="phase_plan",
                    next_action="run portfolio-final-evidence build",
                )
            ],
            "next_actions": ["knowledge_workspace_portfolio_final_evidence_build"],
        }
        return plan_payload

    def build(self, *, root: str | Path = "/mnt/c/workspace", limit: int = 120, max_code_projects: int = 3) -> dict[str, Any]:
        root_path = Path(root).expanduser().resolve()
        self._ensure_baseline(root_path=root_path, limit=limit, max_code_projects=max_code_projects)
        input_hashes = self._input_hashes(root_path)
        workspace_fingerprint = digest_value({"workspace_id": self.workspace_id, "root": safe_path_ref(root_path), "input_hashes": input_hashes}, length=24)
        run_id = run_id_for(workspace_id=self.workspace_id, root_ref=safe_path_ref(root_path), input_hashes=input_hashes)

        baseline = self._baseline_manifest(root_path=root_path, run_id=run_id, workspace_fingerprint=workspace_fingerprint)
        coverage = self._coverage_state_closure(baseline, run_id, workspace_fingerprint)
        architecture = self._architecture_state_closure(baseline, run_id, workspace_fingerprint)
        ocr = self._ocr_provider_health(baseline, run_id, workspace_fingerprint)
        media = self._media_evidence_matrix(baseline, ocr, run_id, workspace_fingerprint)
        queue = self._full_build_queue(baseline, run_id, workspace_fingerprint, max_code_projects=max_code_projects)
        diagnosis = self._project_build_diagnosis(queue, run_id, workspace_fingerprint)
        trace = self._document_source_trace_closure(baseline, run_id, workspace_fingerprint)
        ui = self._ui_evidence_capture(baseline, run_id, workspace_fingerprint)
        gate = self._final_release_gate(
            baseline=baseline,
            coverage=coverage,
            architecture=architecture,
            ocr=ocr,
            media=media,
            queue=queue,
            diagnosis=diagnosis,
            trace=trace,
            ui=ui,
            run_id=run_id,
            workspace_fingerprint=workspace_fingerprint,
        )

        for filename, payload in [
            ("baseline_evidence_manifest.json", baseline),
            ("coverage_state_closure.json", coverage),
            ("architecture_state_closure.json", architecture),
            ("ocr_provider_health.json", ocr),
            ("media_evidence_matrix.json", media),
            ("full_build_queue.json", queue),
            ("project_build_diagnosis.json", diagnosis),
            ("document_source_trace_closure.json", trace),
            ("ui_evidence_capture.json", ui),
            ("final_release_gate.json", gate),
        ]:
            write_artifact(self.workspace, filename, payload)
        write_text_artifact(self.workspace, "false_green_recheck.md", _false_green_recheck(gate))
        write_text_artifact(self.workspace, "final_evidence_report.html", _html_report(gate, baseline, coverage, media, queue, trace, ui))
        return self.read()

    def read(self) -> dict[str, Any]:
        data = {filename.removesuffix(".json"): optional_artifact(self.workspace, filename) for filename in ARTIFACT_FILES if filename.endswith(".json")}
        gate = data.get("final_release_gate") or {}
        status = str(gate.get("status") or "needs_review")
        refs = [artifact_ref("final_evidence", filename) for filename in ARTIFACT_FILES]
        return {
            "ok": status == "accepted",
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "phase": "V2.106-V2.110",
            "status": status,
            "implementation_status": (gate.get("data") or {}).get("implementation_status", "needs_review"),
            "portfolio_final_status": (gate.get("data") or {}).get("portfolio_final_status", status),
            "summary": dict((gate.get("data") or {}).get("summary") or {}),
            "data": data,
            "artifact_refs": refs,
            "evidence_refs": list(gate.get("evidence_refs") or []),
            "warnings": list(gate.get("warnings") or []),
            "unresolved": list(gate.get("unresolved") or []),
            "next_actions": list(gate.get("next_actions") or ["knowledge_workspace_portfolio_final_evidence_build"]),
        }

    def report(self) -> dict[str, Any]:
        payload = self.read()
        payload["final_evidence_report_html"] = read_text_artifact(self.workspace, "final_evidence_report.html")
        return payload

    def _ensure_baseline(self, *, root_path: Path, limit: int, max_code_projects: int) -> None:
        missing = [filename for filename in BASELINE_ARTIFACT_FILES if filename.endswith(".json") and not (self.workspace / "portfolio" / filename).exists()]
        if missing:
            WorkspacePortfolioService(self.workspace, workspace_id=self.workspace_id).build(
                root=root_path,
                limit=limit,
                max_code_projects=max(0, max_code_projects),
            )

    def _input_hashes(self, root_path: Path) -> dict[str, Any]:
        workspace_hashes = {}
        for filename in BASELINE_ARTIFACT_FILES:
            path = self.workspace / "portfolio" / filename
            workspace_hashes[filename] = file_hash(path) if path.exists() else None
        doc_hashes = {}
        repo_root = Path.cwd()
        for filename in DOC_BASELINE_FILES:
            path = repo_root / filename
            doc_hashes[filename] = file_hash(path) if path.exists() else None
        return {"root_ref": safe_path_ref(root_path), "baseline_artifacts": workspace_hashes, "documents": doc_hashes}

    def _baseline_manifest(self, *, root_path: Path, run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        input_hashes = self._input_hashes(root_path)
        rows = []
        evidence_refs = []
        for filename, digest in input_hashes["baseline_artifacts"].items():
            status = "accepted" if digest else "structured_blocker"
            rows.append(
                {
                    "stable_id": f"baseline:{filename}",
                    "artifact_ref": f"workspace_portfolio://portfolio/{filename}",
                    "hash": digest,
                    "acceptance_status": status,
                    "execution_status": "succeeded" if digest else "unavailable",
                    "required_for": "V2.106-V2.110 baseline",
                }
            )
            if digest:
                evidence_refs.append({"type": "baseline_artifact", "artifact_ref": f"workspace_portfolio://portfolio/{filename}", "sha256": digest})
        for filename, digest in input_hashes["documents"].items():
            rows.append(
                {
                    "stable_id": f"doc:{slug(filename)}",
                    "artifact_ref": filename,
                    "hash": digest,
                    "acceptance_status": "accepted" if digest else "needs_review",
                    "execution_status": "succeeded" if digest else "unavailable",
                    "required_for": "spec and architecture review",
                }
            )
            if digest:
                evidence_refs.append({"type": "document", "artifact_ref": filename, "sha256": digest})
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows])
        payload = base_artifact(
            workspace_id=self.workspace_id,
            phase="V2.106",
            artifact_type="baseline_evidence_manifest",
            artifact_id="baseline_evidence_manifest",
            run_id=run_id,
            status=status,
            input_hashes=input_hashes,
            evidence_refs=evidence_refs,
            artifact_refs=[artifact_ref("baseline_evidence_manifest", "baseline_evidence_manifest.json")],
            workspace_fingerprint=workspace_fingerprint,
        )
        payload["data"] = {
            "root_ref": safe_path_ref(root_path),
            "rows": rows,
            "summary": status_counts(rows),
            "mixed_run_rejected": False,
        }
        payload["unresolved"] = [
            unresolved("structured_blocker" if row["acceptance_status"] == "structured_blocker" else "needs_review", "baseline evidence is missing", item_id=row["stable_id"], next_action="rebuild V2.101-V2.105 baseline or restore document")
            for row in rows
            if row["acceptance_status"] != "accepted"
        ]
        return payload

    def _coverage_state_closure(self, baseline: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        rows = _coverage_rows()
        if not rows:
            rows = [
                {"requirement_id": "V2.101", "capability": "workspace discovery", "documented_status": "accepted"},
                {"requirement_id": "V2.102", "capability": "project knowledge build", "documented_status": "accepted"},
                {"requirement_id": "V2.103", "capability": "document/media intake", "documented_status": "structured_unavailable"},
                {"requirement_id": "V2.104", "capability": "knowledge console portfolio", "documented_status": "needs_review"},
                {"requirement_id": "V2.105", "capability": "release gate", "documented_status": "needs_review"},
            ]
        baseline_ok = baseline.get("status") == "accepted"
        closure_rows = []
        for row in rows:
            documented = str(row.get("documented_status") or row.get("status") or "needs_review")
            accepted = documented == "accepted" and baseline_ok
            closure_rows.append(
                {
                    "stable_id": f"coverage:{slug(row.get('requirement_id') or row.get('capability'))}",
                    "requirement_id": row.get("requirement_id"),
                    "capability": row.get("capability"),
                    "documented_status": documented,
                    "execution_status": "succeeded" if baseline_ok else "unavailable",
                    "acceptance_status": "accepted" if accepted else documented if documented in {"needs_review", "structured_unavailable", "structured_blocker", "failed"} else "needs_review",
                    "evidence_refs": baseline.get("evidence_refs", [])[:4] if accepted else [],
                    "reconciliation": "baseline evidence confirmed" if accepted else "kept non-accepted until direct evidence is present",
                }
            )
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in closure_rows])
        payload = base_artifact(
            workspace_id=self.workspace_id,
            phase="V2.106",
            artifact_type="coverage_state_closure",
            artifact_id="coverage_state_closure",
            run_id=run_id,
            status=status,
            input_artifact_refs=baseline.get("artifact_refs", []),
            input_hashes=baseline.get("input_hashes", {}),
            evidence_refs=baseline.get("evidence_refs", []),
            artifact_refs=[artifact_ref("coverage_state_closure", "coverage_state_closure.json")],
            workspace_fingerprint=workspace_fingerprint,
        )
        payload["data"] = {"rows": closure_rows, "summary": status_counts(closure_rows)}
        payload["unresolved"] = [
            unresolved("needs_review", "coverage row is not directly accepted by current evidence", item_id=row["stable_id"], next_action="attach focused test, E2E, PRD review, and false-green evidence", evidence_refs=row.get("evidence_refs", []))
            for row in closure_rows
            if row["acceptance_status"] != "accepted"
        ]
        return payload

    def _architecture_state_closure(self, baseline: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        entities = [
            ("workspace_portfolio.service.WorkspacePortfolioService", "implemented", "V2.101-V2.105 baseline builder"),
            ("workspace_portfolio_final_evidence.service.WorkspacePortfolioFinalEvidenceService", "implemented", "V2.106-V2.110 closure builder"),
            ("workspace_portfolio_final_evidence.shared.StatusAlgebra", "implemented", "execution/acceptance status split"),
            ("workspace_portfolio_final_evidence.persistence", "implemented", "atomic artifact directory"),
            ("CLI portfolio-final-evidence", "implemented", "shell public surface"),
            ("MCP workspace portfolio final evidence tools", "implemented", "agent public surface"),
            ("HTTP /portfolio-final-evidence", "implemented", "portal/API public surface"),
            ("/knowledge final evidence panel", "needs_review", "UI display requires browser evidence"),
            ("OCR execution provider", "structured_unavailable", "provider optional; missing provider cannot be accepted"),
        ]
        rows = [
            {
                "stable_id": f"architecture:{slug(name)}",
                "entity": name,
                "implementation_state": state,
                "acceptance_status": "accepted" if state == "implemented" else state,
                "evidence_refs": baseline.get("evidence_refs", [])[:2] if state == "implemented" else [],
                "notes": notes,
            }
            for name, state, notes in entities
        ]
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows])
        payload = base_artifact(
            workspace_id=self.workspace_id,
            phase="V2.106",
            artifact_type="architecture_state_closure",
            artifact_id="architecture_state_closure",
            run_id=run_id,
            status=status,
            input_artifact_refs=baseline.get("artifact_refs", []),
            input_hashes=baseline.get("input_hashes", {}),
            evidence_refs=baseline.get("evidence_refs", []),
            artifact_refs=[artifact_ref("architecture_state_closure", "architecture_state_closure.json")],
            workspace_fingerprint=workspace_fingerprint,
        )
        payload["data"] = {"rows": rows, "summary": status_counts(rows)}
        payload["unresolved"] = [
            unresolved(str(row["acceptance_status"]), "architecture entity is not fully accepted", item_id=row["stable_id"], next_action="collect implementation or browser evidence")
            for row in rows
            if row["acceptance_status"] != "accepted"
        ]
        return payload

    def _ocr_provider_health(self, baseline: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        providers = [
            ("tesseract", "image_ocr"),
            ("pdftoppm", "pdf_rasterize"),
            ("soffice", "office_conversion"),
        ]
        rows = []
        for binary, capability in providers:
            found = shutil.which(binary)
            rows.append(
                {
                    "stable_id": f"provider:{binary}",
                    "provider": binary,
                    "capability": capability,
                    "execution_status": "succeeded" if found else "unavailable",
                    "acceptance_status": "accepted" if found else "structured_unavailable",
                    "path_ref": f"binary://{binary}" if found else "",
                    "evidence_refs": [{"type": "provider_binary", "artifact_ref": f"binary://{binary}"}] if found else [],
                }
            )
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows])
        payload = base_artifact(
            workspace_id=self.workspace_id,
            phase="V2.107",
            artifact_type="ocr_provider_health",
            artifact_id="ocr_provider_health",
            run_id=run_id,
            status=status,
            input_artifact_refs=baseline.get("artifact_refs", []),
            input_hashes=baseline.get("input_hashes", {}),
            evidence_refs=[ref for row in rows for ref in row.get("evidence_refs", [])],
            artifact_refs=[artifact_ref("ocr_provider_health", "ocr_provider_health.json")],
            workspace_fingerprint=workspace_fingerprint,
        )
        payload["data"] = {"providers": rows, "summary": status_counts(rows)}
        payload["unresolved"] = [
            unresolved("structured_unavailable", f"{row['provider']} is unavailable", item_id=row["stable_id"], next_action="install provider or keep media OCR rows structured_unavailable")
            for row in rows
            if row["acceptance_status"] != "accepted"
        ]
        return payload

    def _media_evidence_matrix(self, baseline: dict[str, Any], ocr: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        media_readiness = read_json(self.workspace / "portfolio" / "media_readiness.json", {})
        source_matrix = read_json(self.workspace / "portfolio" / "source_candidate_matrix.json", {})
        ocr_available = any(row.get("acceptance_status") == "accepted" for row in (ocr.get("data") or {}).get("providers", []) if row.get("capability") == "image_ocr")
        rows = []
        for source in list(media_readiness.get("ocr_required_rows") or source_matrix.get("rows") or []):
            source_format = str(source.get("source_format") or "unknown")
            needs_ocr = source_format in {"png", "jpg", "jpeg", "webp", "gif", "bmp", "tif", "tiff", "pdf", "ppt", "pptx"}
            accepted = bool(source.get("evidence_refs")) and not needs_ocr
            status = "accepted" if accepted else "needs_review" if not needs_ocr else "structured_unavailable" if not ocr_available else "needs_review"
            rows.append(
                {
                    "stable_id": f"media:{slug(source.get('project_id'))}:{slug(source_format)}",
                    "project_id": source.get("project_id"),
                    "source_format": source_format,
                    "source_count": int(source.get("source_count") or 0),
                    "requires_ocr": needs_ocr,
                    "execution_status": "skipped" if needs_ocr and not ocr_available else "queued" if needs_ocr else "succeeded",
                    "acceptance_status": status,
                    "evidence_refs": list(source.get("evidence_refs") or []) if accepted else [],
                    "reason": "OCR/provider evidence required" if needs_ocr else "source trace/import evidence required",
                }
            )
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows])
        payload = base_artifact(
            workspace_id=self.workspace_id,
            phase="V2.107",
            artifact_type="media_evidence_matrix",
            artifact_id="media_evidence_matrix",
            run_id=run_id,
            status=status,
            input_artifact_refs=[artifact_ref("ocr_provider_health", "ocr_provider_health.json"), *baseline.get("artifact_refs", [])],
            input_hashes=baseline.get("input_hashes", {}),
            evidence_refs=[ref for row in rows for ref in row.get("evidence_refs", [])],
            artifact_refs=[artifact_ref("media_evidence_matrix", "media_evidence_matrix.json")],
            workspace_fingerprint=workspace_fingerprint,
        )
        payload["data"] = {"rows": rows, "summary": status_counts(rows), "ocr_available": ocr_available}
        payload["unresolved"] = [
            unresolved(str(row["acceptance_status"]), row["reason"], item_id=row["stable_id"], next_action="run provider-backed OCR/import/source trace or keep structured unavailable")
            for row in rows
            if row["acceptance_status"] != "accepted"
        ]
        return payload

    def _full_build_queue(self, baseline: dict[str, Any], run_id: str, workspace_fingerprint: str, *, max_code_projects: int) -> dict[str, Any]:
        registry = read_json(self.workspace / "portfolio" / "project_registry.json", {})
        runs = read_json(self.workspace / "portfolio" / "project_build_runs.json", {})
        run_by_project = {str(row.get("project_id")): row for row in runs.get("runs", [])}
        rows = []
        executed = 0
        for project in registry.get("projects", []):
            project_id = str(project.get("project_id"))
            baseline_run = run_by_project.get(project_id, {})
            is_code = project.get("classification") == "code_project"
            baseline_status = str(baseline_run.get("status") or project.get("status") or "needs_review")
            if is_code and baseline_status == "accepted":
                execution_status = "succeeded"
                acceptance_status = "accepted"
                queue_state = "executed_in_baseline"
                executed += 1
            elif is_code and executed >= max_code_projects:
                execution_status = "skipped"
                acceptance_status = "needs_review"
                queue_state = "deferred_by_limit"
            elif is_code:
                execution_status = "unavailable" if baseline_status == "structured_unavailable" else "skipped"
                acceptance_status = baseline_status if baseline_status in {"structured_unavailable", "failed", "structured_blocker"} else "needs_review"
                queue_state = "diagnosed_not_accepted"
            else:
                execution_status = "skipped"
                acceptance_status = "needs_review"
                queue_state = "non_code_source_intake_required"
            rows.append(
                {
                    "stable_id": f"build:{project_id}",
                    "project_id": project_id,
                    "display_name": project.get("display_name"),
                    "classification": project.get("classification"),
                    "queue_state": queue_state,
                    "execution_status": execution_status,
                    "acceptance_status": acceptance_status,
                    "baseline_status": baseline_status,
                    "artifact_refs": list(baseline_run.get("artifact_refs") or []),
                    "command_refs": list(baseline_run.get("command_refs") or []),
                    "evidence_refs": list(project.get("evidence_refs") or []),
                }
            )
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows])
        payload = base_artifact(
            workspace_id=self.workspace_id,
            phase="V2.108",
            artifact_type="full_build_queue",
            artifact_id="full_build_queue",
            run_id=run_id,
            status=status,
            input_artifact_refs=baseline.get("artifact_refs", []),
            input_hashes=baseline.get("input_hashes", {}),
            evidence_refs=[ref for row in rows for ref in row.get("evidence_refs", [])][:20],
            artifact_refs=[artifact_ref("full_build_queue", "full_build_queue.json")],
            workspace_fingerprint=workspace_fingerprint,
        )
        payload["data"] = {
            "rows": rows,
            "summary": {**status_counts(rows), "total_queue_count": len(rows), "max_code_projects": max_code_projects},
            "security_model": {
                "external_build_scripts_executed": False,
                "workspace_mutation_allowed": False,
                "execution_mode": "read_only_import_snapshot_inventory_symbols",
            },
        }
        payload["unresolved"] = [
            unresolved(str(row["acceptance_status"]), "project is not accepted in full build governance queue", item_id=row["stable_id"], next_action="run approved bounded build or mark structured unavailable with reason")
            for row in rows
            if row["acceptance_status"] != "accepted"
        ]
        return payload

    def _project_build_diagnosis(self, queue: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        rows = []
        for row in (queue.get("data") or {}).get("rows", []):
            category = "accepted" if row.get("acceptance_status") == "accepted" else row.get("queue_state") or "needs_review"
            rows.append(
                {
                    "stable_id": f"diagnosis:{row.get('project_id')}",
                    "project_id": row.get("project_id"),
                    "failure_category": category,
                    "acceptance_status": row.get("acceptance_status"),
                    "execution_status": row.get("execution_status"),
                    "reason": _diagnosis_reason(category),
                    "next_action": "none" if category == "accepted" else "review queue row and collect missing evidence",
                }
            )
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows])
        payload = base_artifact(
            workspace_id=self.workspace_id,
            phase="V2.108",
            artifact_type="project_build_diagnosis",
            artifact_id="project_build_diagnosis",
            run_id=run_id,
            status=status,
            input_artifact_refs=[artifact_ref("full_build_queue", "full_build_queue.json")],
            input_hashes=queue.get("input_hashes", {}),
            evidence_refs=queue.get("evidence_refs", []),
            artifact_refs=[artifact_ref("project_build_diagnosis", "project_build_diagnosis.json")],
            workspace_fingerprint=workspace_fingerprint,
        )
        payload["data"] = {"rows": rows, "summary": status_counts(rows)}
        payload["unresolved"] = [
            unresolved(str(row["acceptance_status"]), row["reason"], item_id=row["stable_id"], next_action=row["next_action"])
            for row in rows
            if row["acceptance_status"] != "accepted"
        ]
        return payload

    def _document_source_trace_closure(self, baseline: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        source_matrix = read_json(self.workspace / "portfolio" / "source_candidate_matrix.json", {})
        rows = []
        for source in source_matrix.get("rows", []):
            evidence_refs = list(source.get("evidence_refs") or [])
            has_trace = any("source_trace" in str(ref) or "trace" in str(ref) for ref in evidence_refs)
            has_import = any("source" in str(ref) or "import" in str(ref) for ref in evidence_refs)
            accepted = has_trace and has_import
            status = "accepted" if accepted else str(source.get("status") or "needs_review")
            if status == "accepted" and not accepted:
                status = "needs_review"
            rows.append(
                {
                    "stable_id": f"trace:{slug(source.get('project_id'))}:{slug(source.get('source_format'))}",
                    "project_id": source.get("project_id"),
                    "source_format": source.get("source_format"),
                    "source_count": source.get("source_count"),
                    "execution_status": "succeeded" if accepted else "skipped",
                    "acceptance_status": status,
                    "import_evidence_present": has_import,
                    "source_trace_present": has_trace,
                    "evidence_refs": evidence_refs if accepted else [],
                }
            )
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows])
        payload = base_artifact(
            workspace_id=self.workspace_id,
            phase="V2.109",
            artifact_type="document_source_trace_closure",
            artifact_id="document_source_trace_closure",
            run_id=run_id,
            status=status,
            input_artifact_refs=baseline.get("artifact_refs", []),
            input_hashes=baseline.get("input_hashes", {}),
            evidence_refs=[ref for row in rows for ref in row.get("evidence_refs", [])],
            artifact_refs=[artifact_ref("document_source_trace_closure", "document_source_trace_closure.json")],
            workspace_fingerprint=workspace_fingerprint,
        )
        payload["data"] = {"rows": rows, "summary": status_counts(rows)}
        payload["unresolved"] = [
            unresolved(str(row["acceptance_status"]), "source import/query/source-trace chain is incomplete", item_id=row["stable_id"], next_action="run real source import and source trace verification")
            for row in rows
            if row["acceptance_status"] != "accepted"
        ]
        return payload

    def _ui_evidence_capture(self, baseline: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        rows = [
            {
                "stable_id": "ui:knowledge-final-evidence-panel",
                "scenario": "open /knowledge portfolio final evidence panel",
                "execution_status": "skipped",
                "acceptance_status": "structured_unavailable",
                "screenshot_refs": [],
                "reason": "headless browser capture is executed by phase audit/report task, not by build artifact generation",
                "next_action": "run visual acceptance report and attach screenshots",
            }
        ]
        payload = base_artifact(
            workspace_id=self.workspace_id,
            phase="V2.109",
            artifact_type="ui_evidence_capture",
            artifact_id="ui_evidence_capture",
            run_id=run_id,
            status="structured_unavailable",
            input_artifact_refs=baseline.get("artifact_refs", []),
            input_hashes=baseline.get("input_hashes", {}),
            artifact_refs=[artifact_ref("ui_evidence_capture", "ui_evidence_capture.json")],
            workspace_fingerprint=workspace_fingerprint,
        )
        payload["data"] = {"rows": rows, "summary": status_counts(rows)}
        payload["unresolved"] = [
            unresolved("structured_unavailable", rows[0]["reason"], item_id=rows[0]["stable_id"], next_action=rows[0]["next_action"])
        ]
        return payload

    def _final_release_gate(
        self,
        *,
        baseline: dict[str, Any],
        coverage: dict[str, Any],
        architecture: dict[str, Any],
        ocr: dict[str, Any],
        media: dict[str, Any],
        queue: dict[str, Any],
        diagnosis: dict[str, Any],
        trace: dict[str, Any],
        ui: dict[str, Any],
        run_id: str,
        workspace_fingerprint: str,
    ) -> dict[str, Any]:
        phase_statuses = {
            "V2.106_baseline": baseline.get("status", "needs_review"),
            "V2.106_coverage": coverage.get("status", "needs_review"),
            "V2.106_architecture": architecture.get("status", "needs_review"),
            "V2.107_ocr_provider": ocr.get("status", "needs_review"),
            "V2.107_media": media.get("status", "needs_review"),
            "V2.108_build_queue": queue.get("status", "needs_review"),
            "V2.108_diagnosis": diagnosis.get("status", "needs_review"),
            "V2.109_source_trace": trace.get("status", "needs_review"),
            "V2.109_ui": ui.get("status", "structured_unavailable"),
        }
        portfolio_final_status = worst_acceptance_status([str(value) for value in phase_statuses.values()])
        implementation_status = "accepted"
        artifact_inputs = [
            baseline,
            coverage,
            architecture,
            ocr,
            media,
            queue,
            diagnosis,
            trace,
            ui,
        ]
        unresolved_items = [item for artifact in artifact_inputs for item in artifact.get("unresolved", [])]
        blockers = [item for item in unresolved_items if item.get("status") in {"structured_blocker", "structured_unavailable", "needs_review"}]
        payload = base_artifact(
            workspace_id=self.workspace_id,
            phase="V2.110",
            artifact_type="final_release_gate",
            artifact_id="final_release_gate",
            run_id=run_id,
            status=portfolio_final_status,
            input_artifact_refs=[ref for artifact in artifact_inputs for ref in artifact.get("artifact_refs", [])],
            input_hashes=baseline.get("input_hashes", {}),
            evidence_refs=[ref for artifact in artifact_inputs for ref in artifact.get("evidence_refs", [])][:50],
            artifact_refs=[
                artifact_ref("final_release_gate", "final_release_gate.json"),
                artifact_ref("false_green_recheck", "false_green_recheck.md"),
                artifact_ref("final_evidence_report", "final_evidence_report.html"),
            ],
            workspace_fingerprint=workspace_fingerprint,
        )
        payload["data"] = {
            "implementation_status": implementation_status,
            "portfolio_final_status": portfolio_final_status,
            "phase_statuses": phase_statuses,
            "summary": {
                "implementation_status": implementation_status,
                "portfolio_final_status": portfolio_final_status,
                "high_risk_unresolved_count": len(blockers),
                "input_artifact_count": len(payload["input_artifact_refs"]),
                "evidence_ref_count": len(payload["evidence_refs"]),
            },
            "gate_decision_table": {
                "accepted": "all high-risk statuses accepted or explicitly approved out_of_scope",
                "needs_review": "manual/UI/source trace evidence remains incomplete",
                "structured_unavailable": "provider, screenshot, or external evidence unavailable",
                "structured_blocker": "baseline artifact or required schema missing",
            },
            "false_green_rejections": [
                "documentation claim alone is not accepted evidence",
                "scan-only discovery is not full source trace closure",
                "bounded queue execution cannot imply full workspace accepted",
                "missing UI screenshot/headless evidence remains structured_unavailable",
                "missing OCR provider remains structured_unavailable",
            ],
        }
        payload["unresolved"] = blockers
        payload["next_actions"] = [
            "review final_evidence_report.html",
            "attach headless UI screenshots",
            "close source trace and OCR evidence rows",
            "rerun focused tests and final gate",
        ]
        return payload


def public_final_evidence_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": payload.get("status") == "accepted",
        "schema_version": payload.get("schema_version"),
        "workspace_id": payload.get("workspace_id"),
        "phase": payload.get("phase"),
        "status": payload.get("status"),
        "implementation_status": payload.get("implementation_status"),
        "portfolio_final_status": payload.get("portfolio_final_status"),
        "summary": dict(payload.get("summary") or {}),
        "data": dict(payload.get("data") or {}),
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "evidence_refs": list(payload.get("evidence_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
        "next_actions": list(payload.get("next_actions") or []),
    }


def _coverage_rows() -> list[dict[str, Any]]:
    path = Path.cwd() / "docs/V2.x/V2_101_105_WORKSPACE_PORTFOLIO_KNOWLEDGE_FULL_COVERAGE_MATRIX.md"
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) < 3 or cells[0].lower() in {"phase", "requirement id", "id"}:
            continue
        text = " ".join(cells)
        status = "accepted" if "accepted" in text else "structured_unavailable" if "structured_unavailable" in text else "structured_blocker" if "structured_blocker" in text else "needs_review" if "needs_review" in text else "planned"
        rows.append({"requirement_id": cells[0], "capability": cells[1] if len(cells) > 1 else cells[0], "documented_status": status})
    return rows[:80]


def _diagnosis_reason(category: str) -> str:
    return {
        "accepted": "baseline code project produced accepted artifacts",
        "deferred_by_limit": "bounded run limit preserved queue row without treating it as accepted",
        "non_code_source_intake_required": "document/media folder requires explicit source import or media evidence",
        "diagnosed_not_accepted": "baseline build did not produce accepted evidence",
    }.get(category, "project requires review")


def _false_green_recheck(gate: dict[str, Any]) -> str:
    lines = [
        "# V2.106-V2.110 False-Green Recheck",
        "",
        f"Final status: `{gate.get('status')}`",
        f"Implementation status: `{(gate.get('data') or {}).get('implementation_status')}`",
        "",
        "## Rejected False-Green Paths",
    ]
    for item in (gate.get("data") or {}).get("false_green_rejections", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Unresolved"])
    for item in gate.get("unresolved", [])[:80]:
        lines.append(f"- `{item.get('status')}` {item.get('id')}: {item.get('reason')}")
    return "\n".join(lines) + "\n"


def _html_report(
    gate: dict[str, Any],
    baseline: dict[str, Any],
    coverage: dict[str, Any],
    media: dict[str, Any],
    queue: dict[str, Any],
    trace: dict[str, Any],
    ui: dict[str, Any],
) -> str:
    phase_statuses = (gate.get("data") or {}).get("phase_statuses") or {}
    queue_rows = ((queue.get("data") or {}).get("rows") or [])[:80]
    media_rows = ((media.get("data") or {}).get("rows") or [])[:80]
    trace_rows = ((trace.get("data") or {}).get("rows") or [])[:80]
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V2.106-V2.110 工作区组合证据闭环报告</title>
  <style>
    body {{ font-family: Arial, "Microsoft YaHei", sans-serif; margin: 28px; color: #172033; background: #f7f8fb; }}
    h1, h2 {{ margin: 0 0 12px; }}
    section {{ background: #fff; border: 1px solid #d8dee9; border-radius: 8px; padding: 18px; margin: 16px 0; }}
    .status {{ display: inline-block; padding: 4px 8px; border-radius: 6px; background: #eef2ff; font-weight: 700; }}
    .warn {{ background: #fff7ed; }}
    .bad {{ background: #fee2e2; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #e5e7eb; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f1f5f9; }}
    code {{ background: #eef2f7; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>V2.106-V2.110 工作区组合证据闭环报告</h1>
  <p>本报告由真实 workspace scan / portfolio artifacts 派生，不把文档声明、缺失 OCR、缺失 UI 截图或有界执行误写为 accepted。</p>
  <section>
    <h2>出门结论</h2>
    <p>实现状态：<span class="status">{(gate.get('data') or {}).get('implementation_status')}</span></p>
    <p>组合最终状态：<span class="status bad">{(gate.get('data') or {}).get('portfolio_final_status')}</span></p>
    <p>未闭合高风险项：<strong>{(gate.get('data') or {}).get('summary', {}).get('high_risk_unresolved_count')}</strong></p>
  </section>
  <section>
    <h2>阶段状态</h2>
    <table><tr><th>阶段</th><th>状态</th></tr>{''.join(f"<tr><td>{key}</td><td><code>{value}</code></td></tr>" for key, value in phase_statuses.items())}</table>
  </section>
  <section>
    <h2>真实基线证据</h2>
    <p>Baseline 状态：<code>{baseline.get('status')}</code>；Coverage 状态：<code>{coverage.get('status')}</code></p>
    <p>Run ID：<code>{gate.get('run_id')}</code></p>
  </section>
  <section>
    <h2>Full Build Queue</h2>
    <table><tr><th>项目</th><th>分类</th><th>队列状态</th><th>执行状态</th><th>验收状态</th></tr>{''.join(f"<tr><td>{row.get('display_name')}</td><td>{row.get('classification')}</td><td>{row.get('queue_state')}</td><td>{row.get('execution_status')}</td><td><code>{row.get('acceptance_status')}</code></td></tr>" for row in queue_rows)}</table>
  </section>
  <section>
    <h2>媒体与 OCR 证据</h2>
    <table><tr><th>项目</th><th>格式</th><th>数量</th><th>执行状态</th><th>验收状态</th></tr>{''.join(f"<tr><td>{row.get('project_id')}</td><td>{row.get('source_format')}</td><td>{row.get('source_count')}</td><td>{row.get('execution_status')}</td><td><code>{row.get('acceptance_status')}</code></td></tr>" for row in media_rows)}</table>
  </section>
  <section>
    <h2>Source Trace 闭环</h2>
    <table><tr><th>项目</th><th>格式</th><th>Import Evidence</th><th>Source Trace</th><th>验收状态</th></tr>{''.join(f"<tr><td>{row.get('project_id')}</td><td>{row.get('source_format')}</td><td>{row.get('import_evidence_present')}</td><td>{row.get('source_trace_present')}</td><td><code>{row.get('acceptance_status')}</code></td></tr>" for row in trace_rows)}</table>
  </section>
  <section class="warn">
    <h2>UI Evidence</h2>
    <p>状态：<code>{ui.get('status')}</code>。UI 截图验收由阶段性可视化审计执行，本构建产物不伪造截图证据。</p>
  </section>
</body>
</html>
"""
