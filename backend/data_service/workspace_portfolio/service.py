"""Workspace portfolio service for real project and document corpus readiness."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from data_service.code_assets.inventory import CodebaseInventoryService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.snapshot import CodebaseSnapshotService
from data_service.code_assets.symbols import CodebaseSymbolIndexService
from data_service.mcp_common import now

from .persistence import read_artifact, read_text_artifact, remove_artifacts, write_artifact, write_text_artifact
from .shared import (
    CODE_MARKERS,
    DOC_SUFFIXES,
    IGNORED_DIR_NAMES,
    IMAGE_SUFFIXES,
    MEDIA_SUFFIXES,
    SCHEMA_VERSION,
    artifact_ref,
    path_ref,
    slug,
    status_counts,
    unresolved,
    worst_status,
)


class WorkspacePortfolioService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id

    def scan(self, *, root: str | Path, limit: int = 120) -> dict[str, Any]:
        root_path = Path(root).expanduser().resolve()
        generated_at = now()
        _invalidate_downstream_artifacts(self.workspace)
        refs = [
            artifact_ref("project_registry", "project_registry.json"),
            artifact_ref("discovery_report", "discovery_report.md"),
        ]
        if not root_path.exists() or not root_path.is_dir():
            payload = self._base("V2.101", "project_registry", "structured_blocker", refs, generated_at)
            payload["root_ref"] = path_ref(root_path)
            payload["projects"] = []
            payload["ignored"] = []
            payload["unresolved"] = [unresolved("structured_blocker", "workspace root is not a readable directory", item_id="workspace_root", next_action="provide readable workspace root")]
            write_artifact(self.workspace, "project_registry.json", payload)
            write_text_artifact(self.workspace, "discovery_report.md", _discovery_report(payload))
            return self.read()

        projects: list[dict[str, Any]] = []
        ignored: list[dict[str, Any]] = []
        warnings: list[str] = []
        entries = sorted(root_path.iterdir(), key=lambda item: item.name.lower())
        for entry in entries[:limit]:
            if entry.name in IGNORED_DIR_NAMES or entry.name.startswith("."):
                ignored.append({"display_name": entry.name, "path_ref": path_ref(entry, root_path), "reason": "ignored hidden/cache/generated directory"})
                continue
            if not entry.is_dir():
                ignored.append({"display_name": entry.name, "path_ref": path_ref(entry, root_path), "reason": "ignored non-directory workspace item"})
                continue
            projects.append(self._classify_project(entry, root_path))
        if len(entries) > limit:
            warnings.append(f"workspace scan truncated at {limit} entries")
        payload = self._base("V2.101", "project_registry", "accepted" if projects else "needs_review", refs, generated_at)
        payload.update(
            {
                "root_ref": path_ref(root_path, root_path),
                "projects": projects,
                "ignored": ignored,
                "summary": {
                    "project_count": len(projects),
                    "ignored_count": len(ignored),
                    "classification_counts": dict(Counter(str(item.get("classification")) for item in projects)),
                    **status_counts(projects),
                },
                "warnings": warnings,
                "unresolved": [item for project in projects for item in project.get("unresolved", [])],
            }
        )
        write_artifact(self.workspace, "project_registry.json", payload)
        write_text_artifact(self.workspace, "discovery_report.md", _discovery_report(payload))
        return self.read()

    def build(self, *, root: str | Path | None = None, limit: int = 120, max_code_projects: int = 1) -> dict[str, Any]:
        root_path = Path(root).expanduser().resolve() if root is not None else Path("/mnt/c/workspace")
        try:
            if root is not None:
                self.scan(root=root_path, limit=limit)
            registry = read_artifact(self.workspace, "project_registry.json")
        except FileNotFoundError:
            if root is None:
                raise
            self.scan(root=root_path, limit=limit)
            registry = read_artifact(self.workspace, "project_registry.json")
        generated_at = now()
        projects = list(registry.get("projects") or [])
        source_matrix = self._source_candidate_matrix(projects, generated_at)
        media = self._media_readiness(projects, source_matrix, generated_at)
        runs = self._project_build_runs(projects, generated_at, root_path, max_code_projects=max_code_projects)
        index = self._portfolio_index(projects, runs, generated_at)
        gate = self._release_gate(registry, source_matrix, media, runs, index, generated_at)
        report = _html_report(registry, source_matrix, media, runs, index, gate)

        write_artifact(self.workspace, "source_candidate_matrix.json", source_matrix)
        write_artifact(self.workspace, "media_readiness.json", media)
        write_artifact(self.workspace, "project_build_runs.json", runs)
        write_artifact(self.workspace, "portfolio_index.json", index)
        write_artifact(self.workspace, "release_gate.json", gate)
        write_text_artifact(self.workspace, "false_green_audit.md", _false_green_audit(gate))
        write_text_artifact(self.workspace, "portfolio_report.html", report)
        return self.read()

    def report(self) -> dict[str, Any]:
        portfolio = self.read()
        html = read_text_artifact(self.workspace, "portfolio_report.html")
        return {**portfolio, "portfolio_report_html": html}

    def read(self) -> dict[str, Any]:
        registry = _optional(self.workspace, "project_registry.json")
        source = _optional(self.workspace, "source_candidate_matrix.json")
        media = _optional(self.workspace, "media_readiness.json")
        runs = _optional(self.workspace, "project_build_runs.json")
        index = _optional(self.workspace, "portfolio_index.json")
        gate = _optional(self.workspace, "release_gate.json")
        status = str((gate or registry or {}).get("status") or "needs_review")
        artifact_refs = [
            artifact_ref("project_registry", "project_registry.json"),
            artifact_ref("source_candidate_matrix", "source_candidate_matrix.json"),
            artifact_ref("media_readiness", "media_readiness.json"),
            artifact_ref("project_build_runs", "project_build_runs.json"),
            artifact_ref("portfolio_index", "portfolio_index.json"),
            artifact_ref("release_gate", "release_gate.json"),
            artifact_ref("false_green_audit", "false_green_audit.md"),
            artifact_ref("portfolio_report", "portfolio_report.html"),
        ]
        read_model = _read_model(registry, media, runs, gate)
        return {
            "ok": status == "accepted",
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "phase": "V2.101-V2.105",
            "status": status,
            "data": {
                "project_registry": registry,
                "source_candidate_matrix": source,
                "media_readiness": media,
                "project_build_runs": runs,
                "portfolio_index": index,
                "release_gate": gate,
                "knowledge_portfolio_read_model": read_model,
            },
            "summary": dict((gate or registry or {}).get("summary") or {}),
            "artifact_refs": artifact_refs,
            "evidence_refs": list((gate or registry or {}).get("evidence_refs") or []),
            "warnings": list((gate or registry or {}).get("warnings") or []),
            "unresolved": list((gate or registry or {}).get("unresolved") or []),
            "next_actions": list((gate or {}).get("next_actions") or ["knowledge_workspace_portfolio_build"]),
        }

    def _classify_project(self, path: Path, root: Path) -> dict[str, Any]:
        markers = sorted([marker for marker in CODE_MARKERS if (path / marker).exists()])
        has_git = (path / ".git").exists()
        docs_dir = (path / "docs").exists()
        counts = _scan_counts(path)
        doc_count = sum(counts.get(suffix, 0) for suffix in DOC_SUFFIXES)
        media_count = sum(counts.get(suffix, 0) for suffix in MEDIA_SUFFIXES)
        image_count = sum(counts.get(suffix, 0) for suffix in IMAGE_SUFFIXES)
        classification = "code_project" if has_git or markers else "media_corpus" if media_count and not markers else "doc_project" if doc_count else "needs_review"
        status = "accepted" if classification in {"code_project", "doc_project", "media_corpus"} else "needs_review"
        evidence_refs = []
        if has_git:
            evidence_refs.append({"type": "marker", "artifact_ref": f"{path_ref(path / '.git', root)}"})
        evidence_refs.extend({"type": "marker", "artifact_ref": f"{path_ref(path / marker, root)}"} for marker in markers[:8])
        if docs_dir:
            evidence_refs.append({"type": "marker", "artifact_ref": f"{path_ref(path / 'docs', root)}"})
        row_unresolved = []
        if classification == "needs_review":
            row_unresolved.append(unresolved("needs_review", "no code, docs, or media markers found", item_id=f"{slug(path.name)}_classification", next_action="review workspace directory classification"))
        return {
            "project_id": slug(path.name),
            "display_name": path.name,
            "classification": classification,
            "status": status,
            "path_ref": path_ref(path, root),
            "detected_markers": ["has_git"] * int(has_git) + markers + (["docs_dir"] if docs_dir else []),
            "docs_refs": [{"artifact_ref": path_ref(path / "docs", root), "type": "docs_dir"}] if docs_dir else [],
            "media_summary": {"doc_count": doc_count, "media_count": media_count, "image_count": image_count, "suffix_counts": dict(counts)},
            "evidence_refs": evidence_refs,
            "unresolved": row_unresolved,
            "next_actions": ["portfolio build" if status == "accepted" else "review classification"],
        }

    def _source_candidate_matrix(self, projects: list[dict[str, Any]], generated_at: str) -> dict[str, Any]:
        rows = []
        for project in projects:
            suffix_counts = dict((project.get("media_summary") or {}).get("suffix_counts") or {})
            for suffix, count in sorted(suffix_counts.items()):
                if suffix not in DOC_SUFFIXES and suffix not in MEDIA_SUFFIXES:
                    continue
                extractor = suffix in DOC_SUFFIXES and suffix not in IMAGE_SUFFIXES
                status = "structured_unavailable" if suffix in IMAGE_SUFFIXES else "needs_review"
                reason = (
                    "OCR or vision provider evidence required before accepted"
                    if suffix in IMAGE_SUFFIXES
                    else "extractor readiness recorded; ingest/query/source trace evidence required before accepted"
                )
                rows.append(
                    {
                        "project_id": project.get("project_id"),
                        "source_format": suffix.lstrip(".") or "unknown",
                        "source_count": count,
                        "extractor_available": extractor,
                        "import_plan": "data_service_ingest" if extractor else "provider_readiness_required",
                        "status": status,
                        "unsupported_reason": reason,
                        "evidence_refs": list(project.get("evidence_refs") or [])[:3],
                    }
                )
        payload = self._base("V2.103", "source_candidate_matrix", worst_status([str(row["status"]) for row in rows]) if rows else "needs_review", [artifact_ref("source_candidate_matrix", "source_candidate_matrix.json")], generated_at)
        payload.update({"rows": rows, "summary": status_counts(rows)})
        payload["unresolved"] = [unresolved("structured_unavailable", row["unsupported_reason"], item_id=f"{row['project_id']}_{row['source_format']}", next_action="configure OCR/provider or mark out of scope") for row in rows if row["status"] != "accepted"]
        return payload

    def _media_readiness(self, projects: list[dict[str, Any]], source_matrix: dict[str, Any], generated_at: str) -> dict[str, Any]:
        image_count = sum(int((p.get("media_summary") or {}).get("image_count") or 0) for p in projects)
        pdf_count = sum(int(((p.get("media_summary") or {}).get("suffix_counts") or {}).get(".pdf") or 0) for p in projects)
        ppt_count = sum(int(((p.get("media_summary") or {}).get("suffix_counts") or {}).get(".ppt") or 0) + int(((p.get("media_summary") or {}).get("suffix_counts") or {}).get(".pptx") or 0) for p in projects)
        rows = [
            row for row in source_matrix.get("rows", []) if row.get("status") != "accepted"
        ]
        status = "structured_unavailable" if rows else "accepted"
        payload = self._base("V2.103", "media_readiness", status, [artifact_ref("media_readiness", "media_readiness.json")], generated_at)
        payload.update(
            {
                "image_count": image_count,
                "pdf_count": pdf_count,
                "ppt_pptx_count": ppt_count,
                "docx_yaml_count": sum(1 for row in source_matrix.get("rows", []) if row.get("source_format") in {"docx", "yaml", "yml"}),
                "ocr_provider_health": {"status": "structured_unavailable", "provider": "not_configured", "evidence_refs": []},
                "conversion_provider_health": {"status": "needs_review", "provider": "environment_dependent", "evidence_refs": []},
                "ocr_required_rows": rows,
                "structured_unavailable_rows": rows,
                "summary": status_counts(rows),
                "unresolved": [unresolved("structured_unavailable", "OCR/provider evidence is required before media rows can be accepted", item_id="ocr_provider", next_action="configure local OCR/provider or keep structured unavailable")],
            }
        )
        if not rows:
            payload["unresolved"] = []
        return payload

    def _project_build_runs(self, projects: list[dict[str, Any]], generated_at: str, root_path: Path, *, max_code_projects: int) -> dict[str, Any]:
        rows = []
        registry = CodebaseRegistry(self.workspace, workspace_id=self.workspace_id)
        snapshots = CodebaseSnapshotService(self.workspace, workspace_id=self.workspace_id)
        inventory = CodebaseInventoryService(self.workspace, workspace_id=self.workspace_id)
        symbols = CodebaseSymbolIndexService(self.workspace, workspace_id=self.workspace_id)
        code_builds_completed = 0
        ordered_projects = sorted(projects, key=lambda item: (0 if item.get("display_name") == "data_service" else 1, str(item.get("display_name") or "")))
        for project in ordered_projects:
            row = {"project_id": project.get("project_id"), "classification": project.get("classification"), "status": "needs_review", "build_steps": [], "artifact_refs": [], "command_refs": [], "warnings": [], "unresolved": []}
            if project.get("classification") == "code_project":
                if code_builds_completed >= max(0, max_code_projects):
                    row["status"] = "needs_review"
                    row["build_steps"] = ["classified_as_code_project"]
                    row["unresolved"] = [
                        unresolved(
                            "needs_review",
                            "code project was discovered but not built in this bounded portfolio run",
                            item_id=f"{project.get('project_id')}_build_deferred",
                            next_action="increase max_code_projects or run a project-specific build",
                        )
                    ]
                    rows.append(row)
                    continue
                try:
                    root = _path_from_ref(project.get("path_ref"), root_path)
                    imported = registry.import_codebase(path=str(root), codebase_id=str(project.get("project_id")), name=str(project.get("display_name")), metadata={"source": "workspace_portfolio"})
                    codebase_id = imported["asset"].codebase_id
                    snapshot = snapshots.create_snapshot(codebase_id)
                    snapshot_id = str(snapshot["snapshot"]["snapshot_id"])
                    inventory_payload = inventory.build_inventory(codebase_id, snapshot_id=snapshot_id)
                    symbols_payload = symbols.build_symbol_index(codebase_id, snapshot_id=snapshot_id)
                    brief_ref = _write_project_brief(
                        self.workspace,
                        workspace_id=self.workspace_id,
                        project=project,
                        codebase_id=codebase_id,
                        snapshot_id=snapshot_id,
                        inventory_payload=inventory_payload,
                        symbols_payload=symbols_payload,
                        generated_at=generated_at,
                    )
                    row.update(
                        {
                            "status": "accepted",
                            "codebase_id": codebase_id,
                            "snapshot_id": snapshot_id,
                            "artifact_refs": [
                                {"type": "codebase", "artifact_ref": f"codebase://{codebase_id}"},
                                {"type": "snapshot", "artifact_ref": f"snapshot://{codebase_id}/{snapshot_id}"},
                                {"type": "portfolio_brief", "artifact_ref": brief_ref},
                            ],
                            "command_refs": ["portfolio_build:code_asset_pipeline"],
                            "build_steps": ["import", "snapshot", "inventory", "symbols", "portfolio_brief"],
                            "warnings": ["trace/context pack intentionally not generated by portfolio build; no full call graph claim is made"],
                        }
                    )
                    code_builds_completed += 1
                except Exception as exc:  # keep external projects structured instead of false green
                    row["status"] = "structured_unavailable"
                    row["unresolved"] = [unresolved("structured_unavailable", f"code project build unavailable: {type(exc).__name__}", item_id=f"{project.get('project_id')}_build", next_action="review project path, dependencies, or scan policy")]
            elif project.get("classification") in {"doc_project", "media_corpus"}:
                row["status"] = "needs_review"
                row["build_steps"] = ["source_candidate_matrix", "media_readiness"]
                row["unresolved"] = [unresolved("needs_review", "document/media ingest requires explicit source import acceptance", item_id=f"{project.get('project_id')}_docs", next_action="run source import for accepted text extractable rows")]
            rows.append(row)
        status = worst_status([str(row.get("status")) for row in rows])
        payload = self._base("V2.102", "project_build_runs", status, [artifact_ref("project_build_runs", "project_build_runs.json")], generated_at)
        payload.update({"runs": rows, "summary": status_counts(rows), "unresolved": [item for row in rows for item in row.get("unresolved", [])]})
        return payload

    def _portfolio_index(self, projects: list[dict[str, Any]], runs: dict[str, Any], generated_at: str) -> dict[str, Any]:
        accepted_runs = [row for row in runs.get("runs", []) if row.get("status") == "accepted"]
        payload = self._base("V2.102", "portfolio_index", "accepted" if accepted_runs else "needs_review", [artifact_ref("portfolio_index", "portfolio_index.json")], generated_at)
        payload.update(
            {
                "accepted_project_count": len(accepted_runs),
                "needs_review_count": sum(1 for row in runs.get("runs", []) if row.get("status") == "needs_review"),
                "structured_unavailable_count": sum(1 for row in runs.get("runs", []) if row.get("status") == "structured_unavailable"),
                "query_entrypoints": [{"project_id": row.get("project_id"), "codebase_id": row.get("codebase_id"), "entrypoint": "knowledge_agent_context_pack"} for row in accepted_runs],
                "project_overview_refs": [{"project_id": row.get("project_id"), "artifact_ref": f"overview://{row.get('codebase_id')}"} for row in accepted_runs],
                "portfolio_brief_refs": [ref for row in accepted_runs for ref in row.get("artifact_refs", []) if ref.get("type") == "portfolio_brief"],
                "projects": projects,
                "runs": runs.get("runs", []),
            }
        )
        return payload

    def _release_gate(self, registry: dict[str, Any], source: dict[str, Any], media: dict[str, Any], runs: dict[str, Any], index: dict[str, Any], generated_at: str) -> dict[str, Any]:
        phase_statuses = {
            "V2.101": registry.get("status", "needs_review"),
            "V2.102": runs.get("status", "needs_review"),
            "V2.103": media.get("status", "needs_review"),
            "V2.104": "needs_review",
            "V2.105": "needs_review",
        }
        implementation_status = "accepted" if registry.get("status") == "accepted" and index.get("accepted_project_count", 0) > 0 else "needs_review"
        portfolio_final_status = worst_status([str(item) for item in phase_statuses.values()])
        unresolved_items = [
            *list(registry.get("unresolved") or []),
            *list(source.get("unresolved") or []),
            *list(media.get("unresolved") or []),
            *list(runs.get("unresolved") or []),
        ]
        if portfolio_final_status == "accepted":
            unresolved_items = []
        payload = self._base("V2.105", "release_gate", portfolio_final_status, [artifact_ref("release_gate", "release_gate.json"), artifact_ref("false_green_audit", "false_green_audit.md"), artifact_ref("portfolio_report", "portfolio_report.html")], generated_at)
        payload.update(
            {
                "implementation_status": implementation_status,
                "portfolio_final_status": portfolio_final_status,
                "final_status": portfolio_final_status,
                "phase_statuses": phase_statuses,
                "ui_evidence_status": "needs_review",
                "false_green_audit_status": "accepted",
                "blocker_summary": status_counts([{"status": item} for item in phase_statuses.values()]),
                "summary": {
                    "implementation_status": implementation_status,
                    "portfolio_final_status": portfolio_final_status,
                    "accepted_project_count": index.get("accepted_project_count", 0),
                    **status_counts(runs.get("runs", [])),
                },
                "unresolved": unresolved_items,
                "next_actions": ["open /knowledge portfolio panel", "review OCR/provider readiness", "review non-accepted project rows"],
            }
        )
        return payload

    def _base(self, phase: str, artifact_type: str, status: str, refs: list[dict[str, str]], generated_at: str) -> dict[str, Any]:
        return {
            "ok": status == "accepted",
            "schema_version": SCHEMA_VERSION,
            "workspace_id": self.workspace_id,
            "phase": phase,
            "artifact_type": artifact_type,
            "generated_at": generated_at,
            "status": status,
            "artifact_refs": refs,
            "evidence_refs": [],
            "warnings": [],
            "unresolved": [],
            "next_actions": [],
        }


def public_portfolio_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": payload.get("status") == "accepted",
        "schema_version": payload.get("schema_version"),
        "workspace_id": payload.get("workspace_id"),
        "phase": payload.get("phase"),
        "status": payload.get("status"),
        "summary": dict(payload.get("summary") or {}),
        "data": dict(payload.get("data") or {}),
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "evidence_refs": list(payload.get("evidence_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
        "next_actions": list(payload.get("next_actions") or []),
    }


def _invalidate_downstream_artifacts(workspace: Path) -> None:
    remove_artifacts(
        workspace,
        [
            "source_candidate_matrix.json",
            "media_readiness.json",
            "project_build_runs.json",
            "portfolio_index.json",
            "release_gate.json",
            "false_green_audit.md",
            "portfolio_report.html",
        ],
    )


def _write_project_brief(
    workspace: Path,
    *,
    workspace_id: str,
    project: dict[str, Any],
    codebase_id: str,
    snapshot_id: str,
    inventory_payload: dict[str, Any],
    symbols_payload: dict[str, Any],
    generated_at: str,
) -> str:
    filename = f"project_briefs/{slug(codebase_id)}_{slug(snapshot_id)}.json"
    inventory_summary = dict(inventory_payload.get("summary") or {})
    symbol_summary = dict(symbols_payload.get("summary") or {})
    payload = {
        "schema_version": SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "project_id": project.get("project_id"),
        "display_name": project.get("display_name"),
        "codebase_id": codebase_id,
        "snapshot_id": snapshot_id,
        "generated_at": generated_at,
        "status": "accepted",
        "summary": {
            "surface_count": inventory_summary.get("surface_count", 0),
            "capability_count": inventory_summary.get("capability_count", 0),
            "symbol_count": symbol_summary.get("symbol_count", 0),
            "import_count": symbol_summary.get("import_count", 0),
            "python_file_count": symbol_summary.get("python_file_count", 0),
            "syntax_error_count": symbol_summary.get("syntax_error_count", 0),
            "warnings": list(symbol_summary.get("warnings") or [])[:8],
        },
        "boundaries": [
            "portfolio brief is derived from snapshot, inventory, and symbols artifacts",
            "portfolio brief does not claim full call graph, runtime topology, data/control flow, or type inference",
            "documentation claims remain evidence refs, not code facts",
        ],
        "artifact_refs": [
            {"type": "codebase", "artifact_ref": f"codebase://{codebase_id}"},
            {"type": "snapshot", "artifact_ref": f"snapshot://{codebase_id}/{snapshot_id}"},
            *list(inventory_summary.get("artifact_refs") or []),
            *list(symbol_summary.get("artifact_refs") or []),
        ],
    }
    write_artifact(workspace, filename, payload)
    return artifact_ref("portfolio_brief", filename)["artifact_ref"]


def _scan_counts(root: Path, limit: int = 800) -> Counter[str]:
    counts: Counter[str] = Counter()
    visited = 0
    stack = [root]
    while stack and visited < limit:
        current = stack.pop()
        try:
            children = list(current.iterdir())
        except OSError:
            continue
        for path in children:
            if visited >= limit:
                break
            if path.name in IGNORED_DIR_NAMES or path.name.startswith("."):
                continue
            if path.is_dir():
                stack.append(path)
            elif path.is_file():
                counts[path.suffix.lower()] += 1
                visited += 1
    return counts


def _path_from_ref(ref: Any, root: Path) -> Path:
    text = str(ref or "")
    if text.startswith("<workspace-root>/"):
        suffix = text.removeprefix("<workspace-root>/")
        return root if suffix in {"", "."} else root / suffix
    return Path(text)


def _optional(workspace: Path, filename: str) -> dict[str, Any] | None:
    try:
        return read_artifact(workspace, filename)
    except FileNotFoundError:
        return None


def _read_model(registry: dict[str, Any] | None, media: dict[str, Any] | None, runs: dict[str, Any] | None, gate: dict[str, Any] | None) -> dict[str, Any]:
    projects = list((registry or {}).get("projects") or [])
    run_rows = list((runs or {}).get("runs") or [])
    release = gate or {}
    class_counts = Counter(str(project.get("classification")) for project in projects)
    return {
        "status_header": {
            "final_status": release.get("final_status") or release.get("status") or "needs_review",
            "implementation_status": release.get("implementation_status") or "needs_review",
            "portfolio_final_status": release.get("portfolio_final_status") or "needs_review",
            "accepted_count": sum(1 for row in run_rows if row.get("status") == "accepted"),
            "non_accepted_count": sum(1 for row in run_rows if row.get("status") != "accepted"),
            "blocker_count": len(release.get("unresolved") or []),
            "primary_next_action": (release.get("next_actions") or ["run portfolio build"])[0],
        },
        "registry_summary": {
            "code_project_count": class_counts.get("code_project", 0),
            "doc_project_count": class_counts.get("doc_project", 0),
            "media_corpus_count": class_counts.get("media_corpus", 0),
            "needs_review_count": sum(1 for project in projects if project.get("status") == "needs_review"),
            "structured_unavailable_count": sum(1 for project in projects if project.get("status") == "structured_unavailable"),
        },
        "build_summary": status_counts(run_rows),
        "media_summary": {
            "ocr_provider_status": ((media or {}).get("ocr_provider_health") or {}).get("status", "structured_unavailable"),
            "conversion_provider_status": ((media or {}).get("conversion_provider_health") or {}).get("status", "needs_review"),
            "ocr_required_count": len((media or {}).get("ocr_required_rows") or []),
            "unsupported_format_count": len((media or {}).get("structured_unavailable_rows") or []),
        },
        "project_rows": projects,
        "release_gate": {
            "final_status": release.get("final_status") or release.get("status") or "needs_review",
            "no_go_findings": list(release.get("unresolved") or []),
            "false_green_findings": [],
            "next_actions": list(release.get("next_actions") or []),
        },
    }


def _discovery_report(payload: dict[str, Any]) -> str:
    lines = ["# Workspace Portfolio Discovery", "", f"Status: `{payload.get('status')}`", "", "## Projects"]
    for project in payload.get("projects", []):
        lines.append(f"- `{project.get('display_name')}`: {project.get('classification')} / {project.get('status')}")
    lines.extend(["", "## Ignored"])
    for item in payload.get("ignored", []):
        lines.append(f"- `{item.get('display_name')}`: {item.get('reason')}")
    return "\n".join(lines) + "\n"


def _false_green_audit(gate: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Portfolio False-green Audit",
            "",
            "- scan-only evidence rejected",
            "- UI-only evidence rejected",
            "- OCR-missing media rows kept non-accepted",
            "- docs claim not promoted to code fact",
            "- silent skip rejected through unresolved rows",
            "",
            f"implementation_status: `{gate.get('implementation_status')}`",
            f"portfolio_final_status: `{gate.get('portfolio_final_status')}`",
            "",
        ]
    )


def _html_report(registry: dict[str, Any], source: dict[str, Any], media: dict[str, Any], runs: dict[str, Any], index: dict[str, Any], gate: dict[str, Any]) -> str:
    rows = "\n".join(f"<tr><td>{p.get('display_name')}</td><td>{p.get('classification')}</td><td>{p.get('status')}</td><td>{p.get('path_ref')}</td></tr>" for p in registry.get("projects", []))
    return f"""<!doctype html>
<html lang=\"zh-CN\">
<head><meta charset=\"utf-8\"><title>Workspace Portfolio Report</title>
<style>body{{font-family:Arial,sans-serif;margin:24px;color:#1f2937}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #d1d5db;padding:8px}}.warn{{color:#92400e}}</style></head>
<body>
<h1>Workspace 项目组合验收报告</h1>
<p>implementation_status: <strong>{gate.get('implementation_status')}</strong></p>
<p>portfolio_final_status: <strong>{gate.get('portfolio_final_status')}</strong></p>
<h2>目标架构实体</h2>
<p>Workspace Portfolio Scanner、Project Classifier、Project Build Orchestrator、Document Media Intake Probe、Knowledge Console Portfolio Panel、Portfolio Release Gate。</p>
<h2>当前实现状态</h2>
<p>项目数：{len(registry.get('projects', []))}；accepted build：{index.get('accepted_project_count', 0)}；OCR required：{len(media.get('ocr_required_rows', []))}。</p>
<h2>项目列表</h2>
<table><thead><tr><th>项目</th><th>分类</th><th>状态</th><th>路径引用</th></tr></thead><tbody>{rows}</tbody></table>
<h2>False-green</h2>
<p class=\"warn\">UI 截图、目录存在、README 标题和 OCR 缺失均不能替代真实建库证据。</p>
</body></html>
"""
