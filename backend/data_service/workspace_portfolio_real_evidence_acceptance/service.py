"""V2.116-V2.120 real evidence acceptance closure service."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from data_service.mcp_common import now, read_json
from data_service.workspace_portfolio_final_acceptance import WorkspacePortfolioFinalAcceptanceService

from .decisions import empty_decision_set
from .ocr_anchor import build_anchor_rows
from .ocr_provider import execute_ocr_rows, provider_health
from .persistence import (
    acceptance_dir,
    decision_path,
    read_latest,
    read_run_artifact,
    read_text_artifact,
    run_artifact_path,
    run_dir,
    write_decision_set,
    write_latest,
    write_run_artifact,
    write_text_artifact,
)
from .release_gate import evaluate_gate
from .safe_build import discover_build_proposals, execution_rows_from_proposals
from .shared import (
    SCHEMA_BUNDLE_PATH,
    SCHEMA_VERSION,
    artifact_ref,
    base_artifact,
    digest_value,
    file_hash,
    full_digest,
    public_payload,
    run_id_for,
    safe_path_ref,
    status_counts,
    unresolved,
    worst_status,
)
from .source_trace_batch import build_source_trace_rows
from .ui_capture import capture_ui_evidence


RUN_ARTIFACTS = [
    "input_manifest.json",
    "ocr_anchor_registry.json",
    "ocr_provider_execution.json",
    "source_trace_batch_results.json",
    "source_trace_evidence_index.json",
    "ui_capture_results.json",
    "ui_screenshot_manifest.json",
    "safe_build_allowlist.json",
    "safe_build_execution_results.json",
    "evidence_decision_snapshot.json",
    "final_portfolio_acceptance_gate.json",
]


class WorkspacePortfolioRealEvidenceService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id

    def plan(self, *, root: str | Path = "/mnt/c/workspace", limit: int = 120) -> dict[str, Any]:
        root_path = Path(root).expanduser().resolve()
        return {
            "ok": True,
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "phase": "V2.116-V2.120",
            "status": "needs_review",
            "data": {
                "root_ref": safe_path_ref(root_path),
                "planned_artifacts": [artifact_ref(filename) for filename in RUN_ARTIFACTS],
                "phase_order": ["V2.116", "V2.117", "V2.118", "V2.119", "V2.120"],
                "limit": limit,
                "safe_build_true_execution": "blocked_until_managed_sandbox_verified",
            },
            "artifact_refs": [],
            "evidence_refs": [],
            "warnings": ["plan does not execute OCR, browser capture, or external build commands"],
            "unresolved": [
                unresolved(
                    "needs_review",
                    "phase-specific implementation requires focused tests, real E2E, PRD/spec review, and false-green audit",
                    item_id="phase_plan",
                    next_action="run portfolio-real-evidence build",
                )
            ],
            "next_actions": ["knowledge_workspace_portfolio_real_evidence_build"],
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
        self._ensure_upstream(root_path=root_path, limit=limit, max_code_projects=max_code_projects, timeout_seconds=timeout_seconds)
        input_hashes = self._input_hashes(root_path)
        lineage_root_id = digest_value({"workspace_id": self.workspace_id, "root": safe_path_ref(root_path), "input_hashes": input_hashes}, length=24)
        proposal_run_id = run_id_for(workspace_id=self.workspace_id, run_type="proposal", lineage_root_id=lineage_root_id, input_hashes=input_hashes)
        execution_run_id = run_id_for(workspace_id=self.workspace_id, run_type="execution", lineage_root_id=lineage_root_id, input_hashes={**input_hashes, "proposal_run_id": proposal_run_id})
        final_run_id = run_id_for(workspace_id=self.workspace_id, run_type="final_gate", lineage_root_id=lineage_root_id, input_hashes={**input_hashes, "execution_run_id": execution_run_id})
        decision_set_id = f"decision-{digest_value({'proposal_run_id': proposal_run_id}, length=16)}"

        input_manifest_ref = f"runs/{final_run_id}/input_manifest.json"
        input_manifest = self._input_manifest(
            root_path=root_path,
            run_id=final_run_id,
            lineage_root_id=lineage_root_id,
            parent_run_ids=[proposal_run_id, execution_run_id],
            source_run_refs=[],
            input_hashes=input_hashes,
        )
        write_run_artifact(self.workspace, final_run_id, "input_manifest.json", input_manifest)

        decision_set = empty_decision_set(workspace_id=self.workspace_id, decision_set_id=decision_set_id, proposal_run_id=proposal_run_id)
        write_decision_set(self.workspace, decision_set_id, decision_set)
        decision_hash = file_hash(decision_path(self.workspace, decision_set_id)) or digest_value(decision_set, length=64)

        anchor_rows = build_anchor_rows(root_path, limit=limit)
        anchor_status = worst_status([str(row["row_acceptance_status"]) for row in anchor_rows])
        if not anchor_rows:
            anchor_status = "structured_unavailable"
        ocr_anchor = self._artifact(
            run_id=final_run_id,
            lineage_root_id=lineage_root_id,
            parent_run_ids=[proposal_run_id, execution_run_id],
            artifact_id="ocr_anchor_registry",
            artifact_type="ocr_anchor_registry",
            phase="V2.116",
            artifact_status=anchor_status,
            input_manifest_ref=input_manifest_ref,
            input_hashes=input_hashes,
            data={"rows": anchor_rows},
            unresolved_items=_row_unresolved(anchor_rows, "ocr_anchor"),
        )

        provider_rows = execute_ocr_rows(root_path, anchor_rows, run_dir(self.workspace, final_run_id))
        health = provider_health()
        provider_status = worst_status([str(row["row_acceptance_status"]) for row in provider_rows] + [str(row["row_acceptance_status"]) for row in health])
        if not provider_rows:
            provider_status = "structured_unavailable"
        ocr_execution = self._artifact(
            run_id=final_run_id,
            lineage_root_id=lineage_root_id,
            parent_run_ids=[proposal_run_id, execution_run_id],
            artifact_id="ocr_provider_execution",
            artifact_type="ocr_provider_execution",
            phase="V2.116",
            artifact_status=provider_status,
            input_manifest_ref=input_manifest_ref,
            input_hashes=input_hashes,
            data={"provider_health": health, "rows": provider_rows},
            unresolved_items=_row_unresolved(provider_rows, "ocr_provider"),
        )

        source_rows, source_index_rows = build_source_trace_rows(root_path, limit=limit)
        source_status = worst_status([str(row["row_acceptance_status"]) for row in source_rows]) if source_rows else "structured_unavailable"
        source_batch = self._artifact(
            run_id=final_run_id,
            lineage_root_id=lineage_root_id,
            parent_run_ids=[proposal_run_id, execution_run_id],
            artifact_id="source_trace_batch_results",
            artifact_type="source_trace_batch_results",
            phase="V2.117",
            artifact_status=source_status,
            input_manifest_ref=input_manifest_ref,
            input_hashes=input_hashes,
            data={"rows": source_rows},
            unresolved_items=_row_unresolved(source_rows, "source_trace_batch"),
        )
        source_index = self._artifact(
            run_id=final_run_id,
            lineage_root_id=lineage_root_id,
            parent_run_ids=[proposal_run_id, execution_run_id],
            artifact_id="source_trace_evidence_index",
            artifact_type="source_trace_evidence_index",
            phase="V2.117",
            artifact_status=source_status,
            input_manifest_ref=input_manifest_ref,
            input_hashes=input_hashes,
            data={"rows": source_index_rows},
            unresolved_items=_row_unresolved(source_index_rows, "source_trace_index"),
        )

        ui_scenarios, screenshots = capture_ui_evidence(run_dir(self.workspace, final_run_id), headless=headless)
        ui_status = worst_status([str(row["row_acceptance_status"]) for row in ui_scenarios]) if ui_scenarios else "structured_unavailable"
        ui_capture = self._artifact(
            run_id=final_run_id,
            lineage_root_id=lineage_root_id,
            parent_run_ids=[proposal_run_id, execution_run_id],
            artifact_id="ui_capture_results",
            artifact_type="ui_capture_results",
            phase="V2.118",
            artifact_status=ui_status,
            input_manifest_ref=input_manifest_ref,
            input_hashes=input_hashes,
            data={"scenarios": ui_scenarios},
            unresolved_items=_row_unresolved(ui_scenarios, "ui_capture"),
        )
        screenshot_status = worst_status([str(row["row_acceptance_status"]) for row in screenshots]) if screenshots else ui_status
        ui_manifest = self._artifact(
            run_id=final_run_id,
            lineage_root_id=lineage_root_id,
            parent_run_ids=[proposal_run_id, execution_run_id],
            artifact_id="ui_screenshot_manifest",
            artifact_type="ui_screenshot_manifest",
            phase="V2.118",
            artifact_status=screenshot_status,
            input_manifest_ref=input_manifest_ref,
            input_hashes=input_hashes,
            data={"screenshots": screenshots},
            unresolved_items=_row_unresolved(screenshots, "ui_screenshot"),
        )

        proposals = discover_build_proposals(root_path, limit=max_code_projects)
        for command in proposals:
            command["proposal_run_id"] = proposal_run_id
            command["decision_set_id"] = decision_set_id
        allowlist_status = "needs_review" if proposals else "structured_unavailable"
        allowlist = self._artifact(
            run_id=final_run_id,
            lineage_root_id=lineage_root_id,
            parent_run_ids=[proposal_run_id, execution_run_id],
            artifact_id="safe_build_allowlist",
            artifact_type="safe_build_allowlist",
            phase="V2.119",
            artifact_status=allowlist_status,
            input_manifest_ref=input_manifest_ref,
            input_hashes=input_hashes,
            data={"commands": proposals},
            unresolved_items=_row_unresolved(proposals, "safe_build_allowlist", status_field="approval_status"),
        )
        execution_rows = execution_rows_from_proposals(proposals, sandbox_verified=False)
        execution_status = worst_status([str(row["row_acceptance_status"]) for row in execution_rows]) if execution_rows else "structured_unavailable"
        build_execution = self._artifact(
            run_id=final_run_id,
            lineage_root_id=lineage_root_id,
            parent_run_ids=[proposal_run_id, execution_run_id],
            artifact_id="safe_build_execution_results",
            artifact_type="safe_build_execution_results",
            phase="V2.119",
            artifact_status=execution_status,
            input_manifest_ref=input_manifest_ref,
            input_hashes=input_hashes,
            data={"commands": execution_rows},
            unresolved_items=_row_unresolved(execution_rows, "safe_build_execution"),
        )

        decision_snapshot = self._artifact(
            run_id=final_run_id,
            lineage_root_id=lineage_root_id,
            parent_run_ids=[proposal_run_id, execution_run_id],
            artifact_id="evidence_decision_snapshot",
            artifact_type="evidence_decision_snapshot",
            phase="V2.120",
            artifact_status="needs_review",
            input_manifest_ref=input_manifest_ref,
            input_hashes=input_hashes,
            data={
                "decision_set_ref": f"decisions/{decision_set_id}.json",
                "decision_set_hash": decision_hash,
                "evaluated_at": now(),
                "effective_decision_ids": [],
                "revoked_or_expired_decision_ids": [],
                "scope_validation": "matched",
                "approval_binding_validation": "matched",
            },
            unresolved_items=[
                unresolved("needs_review", "no approved high-risk decision set has been provided", item_id="decision_set", next_action="human review decision set")
            ],
        )

        artifacts = [ocr_anchor, ocr_execution, source_batch, source_index, ui_capture, ui_manifest, allowlist, build_execution, decision_snapshot]
        schema_errors: list[str] = []
        for filename, payload in [
            ("ocr_anchor_registry.json", ocr_anchor),
            ("ocr_provider_execution.json", ocr_execution),
            ("source_trace_batch_results.json", source_batch),
            ("source_trace_evidence_index.json", source_index),
            ("ui_capture_results.json", ui_capture),
            ("ui_screenshot_manifest.json", ui_manifest),
            ("safe_build_allowlist.json", allowlist),
            ("safe_build_execution_results.json", build_execution),
            ("evidence_decision_snapshot.json", decision_snapshot),
        ]:
            schema_errors.extend(self.validate_artifact(filename, payload))
            write_run_artifact(self.workspace, final_run_id, filename, payload)

        input_manifest_hash = file_hash(run_artifact_path(self.workspace, final_run_id, "input_manifest.json")) or digest_value(input_manifest, length=64)
        gate_data = evaluate_gate(artifacts, schema_errors=schema_errors, decision_set_ids=[decision_set_id], input_manifest_hash=input_manifest_hash)
        gate_status = str(gate_data["portfolio_final_status"])
        gate = self._artifact(
            run_id=final_run_id,
            lineage_root_id=lineage_root_id,
            parent_run_ids=[proposal_run_id, execution_run_id],
            artifact_id="final_portfolio_acceptance_gate",
            artifact_type="final_portfolio_acceptance_gate",
            phase="V2.120",
            artifact_status=gate_status,
            input_manifest_ref=input_manifest_ref,
            input_hashes=input_hashes,
            data=gate_data,
            unresolved_items=_gate_unresolved(gate_data),
            warnings=schema_errors[:20],
        )
        schema_errors.extend(self.validate_artifact("final_portfolio_acceptance_gate.json", gate))
        if schema_errors:
            gate["artifact_status"] = "failed"
            gate["data"]["implementation_delivery_status"] = "failed"
            gate["data"]["portfolio_final_status"] = "failed"
            gate["warnings"] = schema_errors[:20]
        write_run_artifact(self.workspace, final_run_id, "final_portfolio_acceptance_gate.json", gate)
        write_text_artifact(self.workspace, final_run_id, "final_portfolio_false_green_audit.md", _false_green_audit(gate))
        write_text_artifact(self.workspace, final_run_id, "final_portfolio_acceptance_report.html", _html_report(gate, artifacts))
        current_hash = file_hash(run_artifact_path(self.workspace, final_run_id, "final_portfolio_acceptance_gate.json")) or digest_value(gate, length=64)
        write_latest(
            self.workspace,
            {
                "schema_version": SCHEMA_VERSION,
                "workspace_id": self.workspace_id,
                "current_run_id": final_run_id,
                "current_run_type": "final_gate",
                "current_run_ref": f"runs/{final_run_id}/final_portfolio_acceptance_gate.json",
                "current_run_hash": current_hash,
                "updated_at": now(),
                "completeness_check_ref": f"runs/{final_run_id}/final_portfolio_false_green_audit.md",
            },
        )
        return self.read()

    def read(self) -> dict[str, Any]:
        latest = read_latest(self.workspace)
        run_id = str(latest["current_run_id"])
        data: dict[str, Any] = {}
        for filename in RUN_ARTIFACTS:
            try:
                data[filename.removesuffix(".json")] = read_run_artifact(self.workspace, run_id, filename)
            except FileNotFoundError:
                data[filename.removesuffix(".json")] = None
        gate = data.get("final_portfolio_acceptance_gate") or {}
        status = str(gate.get("artifact_status") or "needs_review")
        return {
            "ok": status == "accepted",
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "phase": "V2.116-V2.120",
            "status": status,
            "implementation_delivery_status": (gate.get("data") or {}).get("implementation_delivery_status", "needs_review"),
            "portfolio_final_status": (gate.get("data") or {}).get("portfolio_final_status", status),
            "run_id": run_id,
            "latest": latest,
            "data": data,
            "artifact_refs": [artifact_ref(filename, run_id=run_id) for filename in RUN_ARTIFACTS],
            "evidence_refs": list(gate.get("evidence_refs") or []),
            "warnings": list(gate.get("warnings") or []),
            "unresolved": list(gate.get("unresolved") or []),
            "next_actions": ["knowledge_workspace_portfolio_real_evidence_report"],
        }

    def report(self) -> dict[str, Any]:
        payload = self.read()
        payload["final_portfolio_acceptance_report_html"] = read_text_artifact(self.workspace, str(payload["run_id"]), "final_portfolio_acceptance_report.html")
        payload["final_portfolio_false_green_audit_md"] = read_text_artifact(self.workspace, str(payload["run_id"]), "final_portfolio_false_green_audit.md")
        return payload

    def validate_artifact(self, filename: str, payload: dict[str, Any]) -> list[str]:
        bundle = read_json(SCHEMA_BUNDLE_PATH, {})
        schemas = bundle.get("schemas") or {}
        schema_name = filename.replace(".json", ".schema.json")
        if schema_name not in schemas:
            return [f"schema missing for {filename}"]
        schema = dict(schemas[schema_name])
        schema["$defs"] = bundle.get("$defs") or {}
        errors = []
        validator = Draft202012Validator(schema)
        for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.path)):
            path = ".".join(str(part) for part in error.path) or "<root>"
            errors.append(f"{filename}:{path}:{error.message}")
        return errors

    def _ensure_upstream(self, *, root_path: Path, limit: int, max_code_projects: int, timeout_seconds: int) -> None:
        expected = self.workspace / "portfolio_final_acceptance" / "final_acceptance_gate.json"
        if not expected.exists():
            WorkspacePortfolioFinalAcceptanceService(self.workspace, workspace_id=self.workspace_id).build(
                root=root_path,
                limit=limit,
                max_code_projects=max_code_projects,
                timeout_seconds=timeout_seconds,
                headless=True,
            )

    def _input_hashes(self, root_path: Path) -> dict[str, Any]:
        upstream = self.workspace / "portfolio_final_acceptance"
        baseline_hashes = {path.name: file_hash(path) for path in sorted(upstream.glob("*.json")) if path.is_file()}
        doc_hashes = {
            str(path): file_hash(path)
            for path in [
                Path("docs/V2.x/V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_PRD.md"),
                Path("docs/V2.x/V2_116_120_REAL_EVIDENCE_ACCEPTANCE_CLOSURE_TARGET_ARCHITECTURE.md"),
                SCHEMA_BUNDLE_PATH,
            ]
            if path.exists()
        }
        return {"root_ref": safe_path_ref(root_path), "upstream_final_acceptance": baseline_hashes, "documents": doc_hashes}

    def _input_manifest(
        self,
        *,
        root_path: Path,
        run_id: str,
        lineage_root_id: str,
        parent_run_ids: list[str],
        source_run_refs: list[dict[str, Any]],
        input_hashes: dict[str, Any],
    ) -> dict[str, Any]:
        root_ref = safe_path_ref(root_path)
        return base_artifact(
            workspace_id=self.workspace_id,
            run_id=run_id,
            run_type="final_gate",
            lineage_root_id=lineage_root_id,
            parent_run_ids=parent_run_ids,
            source_run_refs=source_run_refs,
            artifact_id="input_manifest",
            artifact_type="input_manifest",
            phase="Shared",
            artifact_status="accepted",
            input_manifest_ref=f"runs/{run_id}/input_manifest.json",
            input_hashes=input_hashes,
            artifact_refs=[artifact_ref("input_manifest.json", run_id=run_id)],
            data={
                "root_ref": root_ref,
                "root_fingerprint": digest_value({"root_ref": root_ref, "input_hashes": input_hashes}, length=64),
                "upstream_runs": list((input_hashes.get("upstream_final_acceptance") or {}).keys()),
                "document_hashes": dict(input_hashes.get("documents") or {}),
            },
        )

    def _artifact(self, **kwargs: Any) -> dict[str, Any]:
        artifact_id = str(kwargs["artifact_id"])
        run_id = str(kwargs["run_id"])
        kwargs.setdefault("run_type", "final_gate")
        kwargs.setdefault("workspace_id", self.workspace_id)
        kwargs.setdefault("source_run_refs", [])
        kwargs.setdefault("artifact_refs", [artifact_ref(f"{artifact_id}.json", run_id=run_id)])
        return base_artifact(**kwargs)


def public_real_evidence_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)


def _row_unresolved(rows: list[dict[str, Any]], prefix: str, *, status_field: str = "row_acceptance_status") -> list[dict[str, Any]]:
    items = []
    for idx, row in enumerate(rows):
        status = str(row.get(status_field) or row.get("row_acceptance_status") or "needs_review")
        if status in {"accepted", "approved"}:
            continue
        item_id = str(row.get("media_id") or row.get("document_id") or row.get("scenario_id") or row.get("command_id") or f"{prefix}_{idx}")
        kind = status if status in {"needs_review", "structured_unavailable", "structured_blocker"} else "needs_review"
        items.append(unresolved(kind, str(row.get("reason") or row.get("failure_category") or f"{prefix} row is not accepted"), item_id=item_id, next_action=f"review {prefix} evidence"))
    if not rows:
        items.append(unresolved("structured_unavailable", f"{prefix} has no rows from real workspace input", item_id=prefix, next_action="provide real workspace input"))
    return items


def _gate_unresolved(gate_data: dict[str, Any]) -> list[dict[str, Any]]:
    if gate_data.get("portfolio_final_status") == "accepted":
        return []
    return [
        unresolved(
            "needs_review",
            "; ".join(gate_data.get("gate_reasons") or ["portfolio final status is not accepted"]),
            item_id="final_portfolio_acceptance_gate",
            next_action="resolve non-accepted evidence rows and rerun final gate",
        )
    ]


def _false_green_audit(gate: dict[str, Any]) -> str:
    data = gate.get("data") or {}
    lines = [
        "# V2.116-V2.120 False-Green Audit",
        "",
        f"- portfolio_final_status: {data.get('portfolio_final_status')}",
        f"- implementation_delivery_status: {data.get('implementation_delivery_status')}",
        f"- high_risk_unresolved_count: {data.get('high_risk_unresolved_count')}",
        "",
        "## Rejections",
    ]
    for item in data.get("false_green_rejected") or []:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def _html_report(gate: dict[str, Any], artifacts: list[dict[str, Any]]) -> str:
    data = gate.get("data") or {}
    rows = "".join(
        f"<tr><td>{artifact.get('artifact_id')}</td><td>{artifact.get('phase')}</td><td>{artifact.get('artifact_status')}</td><td>{len(artifact.get('unresolved') or [])}</td></tr>"
        for artifact in artifacts
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>V2.116-V2.120 Real Evidence Acceptance</title>
<style>body{{font-family:Arial,sans-serif;margin:32px;color:#172033}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #d8dee9;padding:8px}}.status{{font-size:24px;font-weight:700}}</style></head>
<body>
<h1>V2.116-V2.120 真实证据验收报告</h1>
<p class="status">Portfolio Final Status: {data.get('portfolio_final_status')}</p>
<p>Implementation Delivery Status: {data.get('implementation_delivery_status')}</p>
<p>High-risk unresolved: {data.get('high_risk_unresolved_count')}</p>
<table><thead><tr><th>Artifact</th><th>Phase</th><th>Status</th><th>Unresolved</th></tr></thead><tbody>{rows}</tbody></table>
<h2>False-green Rejections</h2>
<ul>{''.join(f'<li>{item}</li>' for item in data.get('false_green_rejected') or [])}</ul>
</body></html>"""
