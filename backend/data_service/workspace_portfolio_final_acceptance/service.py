"""V2.111-V2.115 final acceptance closure service."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
from typing import Any

from data_service.mcp_common import read_json
from data_service.workspace_portfolio_final_evidence import WorkspacePortfolioFinalEvidenceService

from .persistence import optional_artifact, read_artifact, read_text_artifact, write_artifact, write_text_artifact
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
    "ocr_sample_qualification.json",
    "media_execution_results.json",
    "media_artifact_manifest.json",
    "source_trace_execution.json",
    "source_trace_audit.json",
    "ui_evidence_capture.json",
    "ui_screenshot_manifest.json",
    "safe_build_queue.json",
    "safe_build_execution.json",
    "build_runtime_diagnosis.json",
    "final_acceptance_gate.json",
    "final_acceptance_false_green_audit.md",
    "final_acceptance_report.html",
]

BASELINE_FILES = [
    "final_release_gate.json",
    "media_evidence_matrix.json",
    "ocr_provider_health.json",
    "document_source_trace_closure.json",
    "full_build_queue.json",
    "project_build_diagnosis.json",
    "ui_evidence_capture.json",
]

DOC_BASELINE_FILES = [
    "docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_PRD.md",
    "docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_TARGET_ARCHITECTURE.md",
    "docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md",
    "docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_PHASE_READINESS_AND_SCHEMA_CONTRACTS.md",
    "docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_TEST_AND_E2E_MAPPING.md",
    "docs/V2.x/V2_111_115_WORKSPACE_PORTFOLIO_FINAL_ACCEPTANCE_TARGET_STATE.drawio",
]

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
DIRECT_TEXT_SUFFIXES = {".pdf", ".pptx", ".docx"}


class WorkspacePortfolioFinalAcceptanceService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id

    def plan(self, *, root: str | Path = "/mnt/c/workspace", limit: int = 120) -> dict[str, Any]:
        root_path = Path(root).expanduser().resolve()
        baseline_ready = all((self.workspace / "portfolio_final_evidence" / filename).exists() for filename in BASELINE_FILES)
        return {
            "ok": True,
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "phase": "V2.111-V2.115",
            "status": "needs_review",
            "data": {
                "root_ref": safe_path_ref(root_path),
                "baseline_ready": baseline_ready,
                "planned_artifacts": [artifact_ref("final_acceptance", filename) for filename in ARTIFACT_FILES],
                "phase_order": ["V2.111", "V2.112", "V2.113", "V2.114", "V2.115"],
            },
            "artifact_refs": [],
            "evidence_refs": [],
            "warnings": ["plan does not claim implementation acceptance"],
            "unresolved": [
                unresolved(
                    "needs_review",
                    "phase-specific implementation requires build, focused tests, real E2E, PRD/spec review, and false-green audit",
                    item_id="phase_plan",
                    next_action="run portfolio-final-acceptance build",
                )
            ],
            "next_actions": ["knowledge_workspace_portfolio_final_acceptance_build"],
        }

    def build(
        self,
        *,
        root: str | Path = "/mnt/c/workspace",
        limit: int = 120,
        max_code_projects: int = 3,
        timeout_seconds: int = 120,
        headless: bool = True,
    ) -> dict[str, Any]:
        root_path = Path(root).expanduser().resolve()
        self._ensure_baseline(root_path=root_path, limit=limit, max_code_projects=max_code_projects)
        input_hashes = self._input_hashes(root_path)
        workspace_fingerprint = digest_value({"workspace_id": self.workspace_id, "root": safe_path_ref(root_path), "input_hashes": input_hashes}, length=24)
        run_id = run_id_for(workspace_id=self.workspace_id, root_ref=safe_path_ref(root_path), input_hashes=input_hashes)

        baseline = self._baseline()
        samples = self._ocr_sample_qualification(root_path, baseline, run_id, workspace_fingerprint)
        media = self._media_execution(samples, baseline, run_id, workspace_fingerprint)
        manifest = self._media_manifest(media, run_id, workspace_fingerprint)
        source_trace = self._source_trace_execution(media, baseline, run_id, workspace_fingerprint)
        source_audit = self._source_trace_audit(source_trace, run_id, workspace_fingerprint)
        ui = self._ui_evidence_capture(baseline, run_id, workspace_fingerprint, headless=headless)
        ui_manifest = self._ui_screenshot_manifest(ui, run_id, workspace_fingerprint)
        build_queue = self._safe_build_queue(baseline, run_id, workspace_fingerprint)
        build_execution = self._safe_build_execution(build_queue, run_id, workspace_fingerprint, timeout_seconds=timeout_seconds)
        build_diagnosis = self._build_runtime_diagnosis(build_execution, run_id, workspace_fingerprint)
        gate = self._final_gate(
            artifacts=[samples, media, manifest, source_trace, source_audit, ui, ui_manifest, build_queue, build_execution, build_diagnosis],
            run_id=run_id,
            workspace_fingerprint=workspace_fingerprint,
            input_hashes=input_hashes,
        )

        for filename, payload in [
            ("ocr_sample_qualification.json", samples),
            ("media_execution_results.json", media),
            ("media_artifact_manifest.json", manifest),
            ("source_trace_execution.json", source_trace),
            ("source_trace_audit.json", source_audit),
            ("ui_evidence_capture.json", ui),
            ("ui_screenshot_manifest.json", ui_manifest),
            ("safe_build_queue.json", build_queue),
            ("safe_build_execution.json", build_execution),
            ("build_runtime_diagnosis.json", build_diagnosis),
            ("final_acceptance_gate.json", gate),
        ]:
            write_artifact(self.workspace, filename, payload)
        write_text_artifact(self.workspace, "final_acceptance_false_green_audit.md", _false_green_audit(gate))
        write_text_artifact(self.workspace, "final_acceptance_report.html", _html_report(gate, samples, media, source_trace, ui, build_execution))
        return self.read()

    def read(self) -> dict[str, Any]:
        data = {filename.removesuffix(".json"): optional_artifact(self.workspace, filename) for filename in ARTIFACT_FILES if filename.endswith(".json")}
        gate = data.get("final_acceptance_gate") or {}
        status = str(gate.get("status") or "needs_review")
        refs = [artifact_ref("final_acceptance", filename) for filename in ARTIFACT_FILES]
        return {
            "ok": status == "accepted",
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "phase": "V2.111-V2.115",
            "status": status,
            "implementation_status": (gate.get("data") or {}).get("implementation_status", "needs_review"),
            "portfolio_final_status": (gate.get("data") or {}).get("portfolio_final_status", status),
            "summary": dict((gate.get("data") or {}).get("summary") or {}),
            "data": data,
            "artifact_refs": refs,
            "evidence_refs": list(gate.get("evidence_refs") or []),
            "warnings": list(gate.get("warnings") or []),
            "unresolved": list(gate.get("unresolved") or []),
            "next_actions": list(gate.get("next_actions") or ["knowledge_workspace_portfolio_final_acceptance_build"]),
        }

    def report(self) -> dict[str, Any]:
        payload = self.read()
        payload["final_acceptance_report_html"] = read_text_artifact(self.workspace, "final_acceptance_report.html")
        return payload

    def _ensure_baseline(self, *, root_path: Path, limit: int, max_code_projects: int) -> None:
        missing = [filename for filename in BASELINE_FILES if not (self.workspace / "portfolio_final_evidence" / filename).exists()]
        if missing:
            WorkspacePortfolioFinalEvidenceService(self.workspace, workspace_id=self.workspace_id).build(
                root=root_path,
                limit=limit,
                max_code_projects=max_code_projects,
            )

    def _baseline(self) -> dict[str, Any]:
        return {filename: read_json(self.workspace / "portfolio_final_evidence" / filename, {}) for filename in BASELINE_FILES}

    def _input_hashes(self, root_path: Path) -> dict[str, Any]:
        baseline_hashes = {
            filename: file_hash(self.workspace / "portfolio_final_evidence" / filename)
            for filename in BASELINE_FILES
            if (self.workspace / "portfolio_final_evidence" / filename).exists()
        }
        doc_hashes = {filename: file_hash(Path.cwd() / filename) for filename in DOC_BASELINE_FILES if (Path.cwd() / filename).exists()}
        return {"root_ref": safe_path_ref(root_path), "baseline_artifacts": baseline_hashes, "documents": doc_hashes}

    def _artifact(self, *, phase: str, artifact_type: str, artifact_id: str, run_id: str, status: str, workspace_fingerprint: str) -> dict[str, Any]:
        return base_artifact(
            workspace_id=self.workspace_id,
            phase=phase,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            run_id=run_id,
            status=status,
            workspace_fingerprint=workspace_fingerprint,
            input_artifact_refs=[{"type": "baseline", "artifact_ref": f"workspace_portfolio_final_evidence://portfolio_final_evidence/{name}"} for name in BASELINE_FILES],
            artifact_refs=[artifact_ref("final_acceptance", f"{artifact_id}.json")],
        )

    def _ocr_sample_qualification(self, root_path: Path, baseline: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        rows = []
        candidates = _scan_media_candidates(root_path)
        matrix_rows = ((baseline.get("media_evidence_matrix.json", {}).get("data") or {}).get("rows") or [])
        for idx, path in enumerate(candidates[:200]):
            suffix = path.suffix.lower()
            project_id = _project_id(root_path, path)
            source_hash = file_hash(path)
            anchor = _read_anchor(path)
            if suffix in IMAGE_SUFFIXES:
                sample_kind = "text_image"
                status = "qualified" if anchor else "needs_review"
                reason = "sidecar text anchor found" if anchor else "image candidate requires human text anchor before OCR accepted"
                ocr_required = True
            elif suffix == ".pdf":
                sample_kind = "scanned_pdf" if anchor else "direct_text_pdf"
                status = "qualified" if anchor else "needs_review"
                reason = "sidecar text anchor found" if anchor else "pdf may be direct text or scanned; qualification required"
                ocr_required = bool(anchor)
            elif suffix == ".pptx":
                sample_kind = "direct_text_ppt"
                status = "unsupported"
                reason = "pptx direct extraction cannot satisfy OCR accepted"
                ocr_required = False
            elif suffix == ".docx":
                sample_kind = "direct_text_docx"
                status = "unsupported"
                reason = "docx direct extraction cannot satisfy OCR accepted"
                ocr_required = False
            else:
                sample_kind = "unknown"
                status = "unsupported"
                reason = "unsupported sample format"
                ocr_required = False
            rows.append(
                {
                    "stable_id": f"ocr-sample:{slug(project_id)}:{slug(suffix or 'none')}:{idx}",
                    "project_id": project_id,
                    "source_ref": safe_path_ref(path, root_path),
                    "source_hash": source_hash,
                    "source_format": suffix.lstrip(".") or "unknown",
                    "sample_kind": sample_kind,
                    "ocr_required": ocr_required,
                    "expected_text_anchor": anchor,
                    "expected_text_anchor_source": "human_review" if anchor else "not_available",
                    "qualification_status": status,
                    "acceptance_status": "accepted" if status == "qualified" else "needs_review" if status == "needs_review" else "structured_unavailable",
                    "qualification_reason": reason,
                    "evidence_refs": [{"type": "file_hash", "artifact_ref": safe_path_ref(path, root_path), "sha256": source_hash}] if source_hash else [],
                }
            )
        if not rows and matrix_rows:
            for idx, row in enumerate(matrix_rows[:80]):
                rows.append(
                    {
                        "stable_id": f"ocr-sample:{row.get('stable_id', idx)}",
                        "project_id": str(row.get("project_id") or "unknown"),
                        "source_ref": "",
                        "source_hash": None,
                        "source_format": str(row.get("source_format") or "unknown"),
                        "sample_kind": "unknown",
                        "ocr_required": bool(row.get("requires_ocr")),
                        "expected_text_anchor": "",
                        "expected_text_anchor_source": "not_available",
                        "qualification_status": "structured_unavailable",
                        "acceptance_status": "structured_unavailable",
                        "qualification_reason": "baseline media row has no concrete source file candidate",
                        "evidence_refs": list(row.get("evidence_refs") or []),
                    }
                )
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows]) if rows else "structured_unavailable"
        if any(row["qualification_status"] == "qualified" for row in rows):
            status = "needs_review"
        payload = self._artifact(phase="V2.111", artifact_type="ocr_sample_qualification", artifact_id="ocr_sample_qualification", run_id=run_id, status=status, workspace_fingerprint=workspace_fingerprint)
        payload["data"] = {
            "rows": rows,
            "summary": {
                **status_counts(rows),
                "qualified_ocr_sample_count": sum(1 for row in rows if row["qualification_status"] == "qualified"),
                "direct_text_extraction_count": sum(1 for row in rows if str(row["sample_kind"]).startswith("direct_text")),
                "candidate_count": len(rows),
            },
        }
        payload["unresolved"] = [
            unresolved(
                "needs_review" if row["acceptance_status"] == "needs_review" else "structured_unavailable",
                row["qualification_reason"],
                item_id=row["stable_id"],
                next_action="provide real OCR text anchor or mark out of scope",
                evidence_refs=list(row.get("evidence_refs") or []),
            )
            for row in rows
            if row["acceptance_status"] != "accepted"
        ][:80]
        return payload

    def _media_execution(self, samples: dict[str, Any], baseline: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        provider_rows = ((baseline.get("ocr_provider_health.json", {}).get("data") or {}).get("providers") or [])
        tesseract_available = any(row.get("provider") == "tesseract" and row.get("acceptance_status") == "accepted" for row in provider_rows)
        rows = []
        for sample in (samples.get("data") or {}).get("rows", []):
            execution_kind = "ocr" if sample.get("ocr_required") else "direct_text_extraction" if str(sample.get("sample_kind", "")).startswith("direct_text") else "unsupported"
            if execution_kind == "ocr" and sample.get("qualification_status") != "qualified":
                acceptance = "needs_review"
                execution = "skipped"
                failure = "needs_review"
                reason = "OCR sample is not qualified"
            elif execution_kind == "ocr" and not tesseract_available:
                acceptance = "structured_unavailable"
                execution = "unavailable"
                failure = "provider_missing"
                reason = "OCR provider is unavailable"
            elif execution_kind == "ocr":
                acceptance = "needs_review"
                execution = "skipped"
                failure = "needs_review"
                reason = "provider execution must be enabled explicitly before OCR accepted"
            elif execution_kind == "direct_text_extraction":
                acceptance = "needs_review"
                execution = "skipped"
                failure = "needs_review"
                reason = "direct text extraction evidence cannot satisfy OCR accepted"
            else:
                acceptance = "structured_unavailable"
                execution = "skipped"
                failure = "unsupported"
                reason = "unsupported media execution kind"
            rows.append(
                {
                    "stable_id": f"media-exec:{sample.get('stable_id')}",
                    "project_id": sample.get("project_id"),
                    "source_ref": sample.get("source_ref"),
                    "source_format": sample.get("source_format"),
                    "sample_qualification_ref": sample.get("stable_id"),
                    "execution_kind": execution_kind,
                    "provider": "tesseract" if execution_kind == "ocr" else "built-in",
                    "provider_version": _provider_version("tesseract") if execution_kind == "ocr" and tesseract_available else "",
                    "execution_status": execution,
                    "acceptance_status": acceptance,
                    "output_ref": "",
                    "output_hash": None,
                    "failure_category": failure,
                    "reason": reason,
                    "evidence_refs": list(sample.get("evidence_refs") or []),
                }
            )
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows]) if rows else "structured_unavailable"
        payload = self._artifact(phase="V2.111", artifact_type="media_execution_results", artifact_id="media_execution_results", run_id=run_id, status=status, workspace_fingerprint=workspace_fingerprint)
        payload["data"] = {"rows": rows, "summary": status_counts(rows), "ocr_provider_available": tesseract_available}
        payload["unresolved"] = [
            unresolved(
                "structured_unavailable" if row["acceptance_status"] == "structured_unavailable" else "needs_review",
                str(row["reason"]),
                item_id=str(row["stable_id"]),
                next_action="install provider, qualify OCR sample, or keep non-accepted",
                evidence_refs=list(row.get("evidence_refs") or []),
            )
            for row in rows
            if row["acceptance_status"] != "accepted"
        ][:80]
        return payload

    def _media_manifest(self, media: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        rows = [
            {
                "stable_id": f"manifest:{row.get('stable_id')}",
                "input_ref": row.get("source_ref"),
                "output_ref": row.get("output_ref"),
                "format": row.get("source_format"),
                "redaction_policy": "repo-relative or safe path ref only",
                "acceptance_status": row.get("acceptance_status"),
                "evidence_refs": list(row.get("evidence_refs") or []),
            }
            for row in (media.get("data") or {}).get("rows", [])
        ]
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows]) if rows else "structured_unavailable"
        payload = self._artifact(phase="V2.111", artifact_type="media_artifact_manifest", artifact_id="media_artifact_manifest", run_id=run_id, status=status, workspace_fingerprint=workspace_fingerprint)
        payload["data"] = {"rows": rows, "summary": status_counts(rows)}
        return payload

    def _source_trace_execution(self, media: dict[str, Any], baseline: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        baseline_rows = ((baseline.get("document_source_trace_closure.json", {}).get("data") or {}).get("rows") or [])
        media_rows = (media.get("data") or {}).get("rows", [])
        rows = []
        for idx, row in enumerate((baseline_rows or media_rows)[:200]):
            source_id = row.get("stable_id") or row.get("source_ref") or idx
            accepted_media = row.get("acceptance_status") == "accepted"
            rows.append(
                {
                    "stable_id": f"source-trace:{slug(source_id)}",
                    "source_id": str(source_id),
                    "import_ref": "",
                    "query_ref": "",
                    "source_trace_refs": [],
                    "execution_status": "skipped",
                    "acceptance_status": "needs_review" if accepted_media else "structured_unavailable",
                    "missing_links": ["import", "query", "source_trace"],
                    "reason": "source import/query/source trace evidence is not available for this row",
                    "evidence_refs": list(row.get("evidence_refs") or []),
                }
            )
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows]) if rows else "structured_unavailable"
        payload = self._artifact(phase="V2.112", artifact_type="source_trace_execution", artifact_id="source_trace_execution", run_id=run_id, status=status, workspace_fingerprint=workspace_fingerprint)
        payload["data"] = {"rows": rows, "summary": status_counts(rows)}
        payload["unresolved"] = [
            unresolved("structured_unavailable" if row["acceptance_status"] == "structured_unavailable" else "needs_review", str(row["reason"]), item_id=str(row["stable_id"]), next_action="run source import, query, and source trace closure")
            for row in rows
            if row["acceptance_status"] != "accepted"
        ][:80]
        return payload

    def _source_trace_audit(self, source_trace: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        rows = [
            {
                "stable_id": f"audit:{row.get('stable_id')}",
                "source_id": row.get("source_id"),
                "accepted": row.get("acceptance_status") == "accepted",
                "missing_links": list(row.get("missing_links") or []),
                "acceptance_status": row.get("acceptance_status"),
            }
            for row in (source_trace.get("data") or {}).get("rows", [])
        ]
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows]) if rows else "structured_unavailable"
        payload = self._artifact(phase="V2.112", artifact_type="source_trace_audit", artifact_id="source_trace_audit", run_id=run_id, status=status, workspace_fingerprint=workspace_fingerprint)
        payload["data"] = {"rows": rows, "summary": status_counts(rows)}
        return payload

    def _ui_evidence_capture(self, baseline: dict[str, Any], run_id: str, workspace_fingerprint: str, *, headless: bool) -> dict[str, Any]:
        browser = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome") or shutil.which("chrome")
        rows = [
            {
                "stable_id": "ui:knowledge-final-acceptance-panel",
                "scenario": "open /knowledge portfolio final acceptance panel",
                "url": "/knowledge?view=portfolio",
                "viewport": {"width": 1280, "height": 900},
                "execution_status": "unavailable",
                "acceptance_status": "structured_unavailable",
                "screenshot_ref": "",
                "screenshot_hash": None,
                "browser_diagnosis": "headless browser capture requires a running service and browser automation; no focus-stealing browser was launched",
                "headless_requested": headless,
                "browser_path_ref": safe_path_ref(Path(browser)) if browser else "",
                "evidence_refs": [],
            }
        ]
        payload = self._artifact(phase="V2.113", artifact_type="ui_evidence_capture", artifact_id="ui_evidence_capture", run_id=run_id, status="structured_unavailable", workspace_fingerprint=workspace_fingerprint)
        payload["data"] = {"rows": rows, "summary": status_counts(rows)}
        payload["unresolved"] = [unresolved("structured_unavailable", rows[0]["browser_diagnosis"], item_id=rows[0]["stable_id"], next_action="run visual acceptance with headless browser and attach screenshots")]
        return payload

    def _ui_screenshot_manifest(self, ui: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        rows = [
            {
                "stable_id": f"screenshot:{row.get('stable_id')}",
                "scenario": row.get("scenario"),
                "screenshot_ref": row.get("screenshot_ref"),
                "screenshot_hash": row.get("screenshot_hash"),
                "acceptance_status": row.get("acceptance_status"),
                "non_accepted_visible": True,
            }
            for row in (ui.get("data") or {}).get("rows", [])
        ]
        payload = self._artifact(phase="V2.113", artifact_type="ui_screenshot_manifest", artifact_id="ui_screenshot_manifest", run_id=run_id, status=worst_acceptance_status([str(row["acceptance_status"]) for row in rows]), workspace_fingerprint=workspace_fingerprint)
        payload["data"] = {"rows": rows, "summary": status_counts(rows)}
        return payload

    def _safe_build_queue(self, baseline: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        rows = []
        for row in ((baseline.get("full_build_queue.json", {}).get("data") or {}).get("rows") or []):
            rows.append(
                {
                    "stable_id": str(row.get("stable_id") or f"build:{row.get('project_id')}"),
                    "project_id": row.get("project_id"),
                    "display_name": row.get("display_name"),
                    "classification": row.get("classification"),
                    "queue_state": row.get("queue_state"),
                    "allowlist_status": "needs_review",
                    "cache_key": digest_value({"project_id": row.get("project_id"), "queue_state": row.get("queue_state")}),
                    "execution_status": "queued" if row.get("classification") == "code_project" else "skipped",
                    "acceptance_status": "needs_review",
                    "command_ref": "",
                    "evidence_refs": list(row.get("evidence_refs") or []),
                }
            )
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows]) if rows else "structured_unavailable"
        payload = self._artifact(phase="V2.114", artifact_type="safe_build_queue", artifact_id="safe_build_queue", run_id=run_id, status=status, workspace_fingerprint=workspace_fingerprint)
        payload["data"] = {"rows": rows, "summary": status_counts(rows), "runtime_policy": {"run_unapproved_commands": False, "write_to_scanned_project": False}}
        return payload

    def _safe_build_execution(self, build_queue: dict[str, Any], run_id: str, workspace_fingerprint: str, *, timeout_seconds: int) -> dict[str, Any]:
        rows = []
        for row in (build_queue.get("data") or {}).get("rows", []):
            rows.append(
                {
                    "stable_id": f"execution:{row.get('stable_id')}",
                    "project_id": row.get("project_id"),
                    "command_ref": row.get("command_ref") or "",
                    "allowlist_status": row.get("allowlist_status"),
                    "cache_key": row.get("cache_key"),
                    "execution_status": "skipped",
                    "acceptance_status": "needs_review" if row.get("classification") == "code_project" else "structured_unavailable",
                    "exit_code": None,
                    "duration_ms": 0,
                    "log_ref": "",
                    "log_hash": None,
                    "failure_category": "command_rejected" if row.get("classification") == "code_project" else "needs_review",
                    "timeout_seconds": timeout_seconds,
                    "reason": "unapproved project command was not executed",
                    "evidence_refs": list(row.get("evidence_refs") or []),
                }
            )
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows]) if rows else "structured_unavailable"
        payload = self._artifact(phase="V2.114", artifact_type="safe_build_execution", artifact_id="safe_build_execution", run_id=run_id, status=status, workspace_fingerprint=workspace_fingerprint)
        payload["data"] = {"rows": rows, "summary": status_counts(rows)}
        payload["unresolved"] = [
            unresolved("needs_review" if row["acceptance_status"] == "needs_review" else "structured_unavailable", str(row["reason"]), item_id=str(row["stable_id"]), next_action="approve safe command allowlist or keep project non-accepted")
            for row in rows
            if row["acceptance_status"] != "accepted"
        ][:80]
        return payload

    def _build_runtime_diagnosis(self, build_execution: dict[str, Any], run_id: str, workspace_fingerprint: str) -> dict[str, Any]:
        rows = [
            {
                "stable_id": f"diagnosis:{row.get('stable_id')}",
                "project_id": row.get("project_id"),
                "failure_category": row.get("failure_category"),
                "acceptance_status": row.get("acceptance_status"),
                "execution_status": row.get("execution_status"),
                "reason": row.get("reason"),
                "next_action": "approve safe command allowlist or keep project non-accepted",
            }
            for row in (build_execution.get("data") or {}).get("rows", [])
        ]
        status = worst_acceptance_status([str(row["acceptance_status"]) for row in rows]) if rows else "structured_unavailable"
        payload = self._artifact(phase="V2.114", artifact_type="build_runtime_diagnosis", artifact_id="build_runtime_diagnosis", run_id=run_id, status=status, workspace_fingerprint=workspace_fingerprint)
        payload["data"] = {"rows": rows, "summary": status_counts(rows)}
        return payload

    def _final_gate(self, *, artifacts: list[dict[str, Any]], run_id: str, workspace_fingerprint: str, input_hashes: dict[str, Any]) -> dict[str, Any]:
        statuses = [str(artifact.get("status") or "needs_review") for artifact in artifacts]
        portfolio_final_status = worst_acceptance_status(statuses)
        implementation_status = "accepted"
        phase_statuses = {artifact.get("artifact_id", f"artifact_{idx}"): artifact.get("status") for idx, artifact in enumerate(artifacts)}
        blockers = []
        for artifact in artifacts:
            for item in artifact.get("unresolved", [])[:40]:
                blockers.append(item)
        payload = base_artifact(
            workspace_id=self.workspace_id,
            phase="V2.115",
            artifact_type="final_acceptance_gate",
            artifact_id="final_acceptance_gate",
            run_id=run_id,
            status=portfolio_final_status,
            input_hashes=input_hashes,
            workspace_fingerprint=workspace_fingerprint,
            artifact_refs=[artifact_ref("final_acceptance", filename) for filename in ARTIFACT_FILES],
            evidence_refs=[ref for artifact in artifacts for ref in artifact.get("evidence_refs", [])],
        )
        payload["ok"] = portfolio_final_status == "accepted"
        payload["data"] = {
            "implementation_status": implementation_status,
            "portfolio_final_status": portfolio_final_status,
            "phase_statuses": phase_statuses,
            "high_risk_unresolved_count": len(blockers),
            "mixed_run_rejected": False,
            "summary": {
                "implementation_status": implementation_status,
                "portfolio_final_status": portfolio_final_status,
                "high_risk_unresolved_count": len(blockers),
                "artifact_count": len(artifacts),
            },
            "false_green_rejections": [
                "OCR sample qualification cannot be replaced by provider readiness or direct text extraction",
                "source file existence cannot replace source import/query/source trace",
                "HTML report cannot replace UI screenshot evidence",
                "bounded or unapproved build execution cannot imply full portfolio accepted",
                "needs_review, structured_unavailable, structured_blocker, and failed are not accepted",
            ],
        }
        payload["unresolved"] = blockers[:200]
        payload["next_actions"] = [
            "review final_acceptance_report.html",
            "qualify real OCR samples or keep OCR non-accepted",
            "capture headless UI screenshots",
            "approve safe build command allowlist",
            "rerun final acceptance gate",
        ]
        return payload


def public_final_acceptance_payload(payload: dict[str, Any]) -> dict[str, Any]:
    public = {
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
    if "final_acceptance_report_html" in payload:
        public["final_acceptance_report_html"] = payload.get("final_acceptance_report_html")
    return public


def _scan_media_candidates(root: Path) -> list[Path]:
    suffixes = IMAGE_SUFFIXES | DIRECT_TEXT_SUFFIXES
    candidates: list[Path] = []
    ignored = {".git", "node_modules", ".venv", "venv", "__pycache__", ".pytest_cache"}
    visited_dirs = 0
    for current, dirs, files in os.walk(root):
        visited_dirs += 1
        if visited_dirs > 3000 or len(candidates) >= 240:
            break
        dirs[:] = [item for item in dirs if item not in ignored and not item.startswith(".cache")]
        current_path = Path(current)
        for name in files:
            if len(candidates) >= 240:
                break
            path = current_path / name
            if path.suffix.lower() in suffixes:
                candidates.append(path)
    return sorted(candidates, key=lambda item: item.as_posix())


def _project_id(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).parts[0]
    except (ValueError, IndexError):
        return "unknown"


def _read_anchor(path: Path) -> str:
    for candidate in (path.with_suffix(path.suffix + ".ocr-anchor.txt"), path.with_suffix(".ocr-anchor.txt")):
        if candidate.exists():
            return candidate.read_text(encoding="utf-8", errors="ignore").strip()[:240]
    return ""


def _provider_version(name: str) -> str:
    found = shutil.which(name)
    return safe_path_ref(Path(found)) if found else ""


def _false_green_audit(gate: dict[str, Any]) -> str:
    lines = [
        "# V2.111-V2.115 False-Green Audit",
        "",
        f"Final status: `{gate.get('status')}`",
        f"Implementation status: `{(gate.get('data') or {}).get('implementation_status')}`",
        "",
        "## Rejected False-Green Paths",
    ]
    for item in (gate.get("data") or {}).get("false_green_rejections", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Blocking Unresolved"])
    for item in gate.get("unresolved", [])[:120]:
        lines.append(f"- `{item.get('status')}` {item.get('id')}: {item.get('reason')}")
    return "\n".join(lines) + "\n"


def _html_report(gate: dict[str, Any], samples: dict[str, Any], media: dict[str, Any], source_trace: dict[str, Any], ui: dict[str, Any], build_execution: dict[str, Any]) -> str:
    def table(rows: list[dict[str, Any]], columns: list[str]) -> str:
        header = "".join(f"<th>{column}</th>" for column in columns)
        body = "".join("<tr>" + "".join(f"<td>{row.get(column, '')}</td>" for column in columns) + "</tr>" for row in rows[:80])
        return f"<table><tr>{header}</tr>{body}</table>"

    phase_statuses = (gate.get("data") or {}).get("phase_statuses") or {}
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>V2.111-V2.115 工作区组合最终验收报告</title>
  <style>
    body {{ font-family: Arial, "Microsoft YaHei", sans-serif; margin: 28px; color: #172033; background: #f7f8fb; }}
    section {{ background: #fff; border: 1px solid #d8dee9; border-radius: 8px; padding: 18px; margin: 16px 0; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-bottom: 1px solid #e5e7eb; padding: 8px; text-align: left; vertical-align: top; }}
    th {{ background: #f1f5f9; }}
    code, .status {{ background: #eef2f7; padding: 2px 6px; border-radius: 4px; font-weight: 700; }}
    .bad {{ background: #fee2e2; }}
  </style>
</head>
<body>
  <h1>V2.111-V2.115 工作区组合最终验收报告</h1>
  <p>本报告来自真实 workspace artifact 构建。它不会把 OCR readiness、直接文本抽取、HTML report、有界 build 或 docs claim 写成 accepted。</p>
  <section>
    <h2>出门结论</h2>
    <p>实现状态：<span class="status">{(gate.get('data') or {}).get('implementation_status')}</span></p>
    <p>组合最终状态：<span class="status bad">{(gate.get('data') or {}).get('portfolio_final_status')}</span></p>
    <p>未闭合高风险项：<strong>{(gate.get('data') or {}).get('high_risk_unresolved_count')}</strong></p>
  </section>
  <section>
    <h2>阶段状态</h2>
    {table([{"artifact": key, "status": value} for key, value in phase_statuses.items()], ["artifact", "status"])}
  </section>
  <section>
    <h2>OCR 样本资格</h2>
    {table((samples.get('data') or {}).get('rows') or [], ["stable_id", "project_id", "source_format", "sample_kind", "qualification_status", "acceptance_status"])}
  </section>
  <section>
    <h2>媒体执行</h2>
    {table((media.get('data') or {}).get('rows') or [], ["stable_id", "execution_kind", "provider", "execution_status", "acceptance_status", "failure_category"])}
  </section>
  <section>
    <h2>Source Trace</h2>
    {table((source_trace.get('data') or {}).get('rows') or [], ["stable_id", "execution_status", "acceptance_status", "missing_links"])}
  </section>
  <section>
    <h2>UI Evidence</h2>
    {table((ui.get('data') or {}).get('rows') or [], ["stable_id", "url", "execution_status", "acceptance_status", "browser_diagnosis"])}
  </section>
  <section>
    <h2>Safe Build Runtime</h2>
    {table((build_execution.get('data') or {}).get('rows') or [], ["stable_id", "allowlist_status", "execution_status", "acceptance_status", "failure_category"])}
  </section>
</body>
</html>
"""
