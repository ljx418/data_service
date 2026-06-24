"""Multi-project regression expansion for V2.57."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    artifact_diff_path,
    chart_audit_path,
    doc_code_evidence_loop_artifact_refs,
    evidence_loop_path,
    expanded_matrix_path,
    failure_diagnosis_path,
    project_story_path,
    read_artifact_diff,
    read_expanded_matrix,
    read_failure_diagnosis,
    read_regression_report,
    regression_expansion_artifact_refs,
    regression_report_path,
    risk_priority_path,
    stop_conditions_path,
    task_workflow_suggested_tests_path,
    workflow_bundle_path,
    write_regression_expansion,
)
from .shared import base_artifact, redaction_findings


PHASE = "V2.57"
PROJECTS = ["data_service", "HarnessOS", "Navia", "codexPat"]
ALLOWED_STATUSES = {"accepted", "needs_review", "structured_unavailable", "structured_blocker"}
FAILURE_CATEGORIES = {"dependency_drift", "sandbox_limit", "artifact_missing", "public_surface_drift", "real_regression", "needs_review"}


class MultiProjectRegressionService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_regression(self, codebase_id: str, *, projects: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = regression_expansion_artifact_refs(codebase_id)
        project_specs = _normalize_projects(projects)
        results = [self._evaluate_project(spec) for spec in project_specs]
        matrix = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase=PHASE,
            artifact_type="multi_project_regression_expanded_matrix",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=[ref for row in results for ref in row.get("artifact_refs", [])],
        )
        accepted = [row for row in results if row["status"] == "accepted"]
        matrix.update(
            {
                "projects": PROJECTS,
                "results": results,
                "summary": {
                    "project_count": len(results),
                    "accepted_count": len(accepted),
                    "structured_unavailable_count": sum(1 for row in results if row["status"] == "structured_unavailable"),
                    "structured_blocker_count": sum(1 for row in results if row["status"] == "structured_blocker"),
                    "needs_review_count": sum(1 for row in results if row["status"] == "needs_review"),
                },
            }
        )
        artifact_diff = _artifact_diff(self.workspace_id, codebase_id, generated_at, refs, results)
        failure_diagnosis = _failure_diagnosis(self.workspace_id, codebase_id, generated_at, refs, results)
        unresolved = redaction_findings(matrix) + redaction_findings(artifact_diff) + redaction_findings(failure_diagnosis)
        matrix["unresolved"].extend(unresolved)
        report = _render_report(matrix, artifact_diff, failure_diagnosis)
        write_regression_expansion(self.workspace, codebase_id, matrix, artifact_diff, failure_diagnosis, report)
        return _bundle(self.workspace_id, codebase_id, matrix, artifact_diff, failure_diagnosis, report, refs)

    def read_regression(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = regression_expansion_artifact_refs(codebase_id)
        matrix = read_expanded_matrix(self.workspace, codebase_id)
        artifact_diff = read_artifact_diff(self.workspace, codebase_id)
        failure_diagnosis = read_failure_diagnosis(self.workspace, codebase_id)
        report = read_regression_report(self.workspace, codebase_id)
        return _bundle(self.workspace_id, codebase_id, matrix, artifact_diff, failure_diagnosis, report, refs)

    def _evaluate_project(self, spec: dict[str, Any]) -> dict[str, Any]:
        name = spec["name"]
        path_text = spec.get("path") or ""
        evidence_mode = spec.get("evidence_mode") or "real"
        if evidence_mode == "structured_unavailable":
            return _project_result(name, "structured_unavailable", spec.get("reason") or "project unavailable for this E2E run", "artifact_missing", [])
        if evidence_mode == "mock":
            return _project_result(name, "needs_review", "mock-only evidence rejected", "needs_review", [])
        if not path_text:
            return _project_result(name, "structured_unavailable", "project path not provided", "artifact_missing", [])
        project_path = Path(path_text).expanduser()
        if not project_path.exists() or not project_path.is_dir():
            return _project_result(name, "structured_unavailable", "project directory unavailable", "artifact_missing", [])
        try:
            asset = self.registry.import_codebase(path=str(project_path), name=name)["asset"]
        except Exception:
            return _project_result(name, "structured_blocker", "project import failed", "real_regression", [])
        project_codebase_id = str(asset.codebase_id)
        artifact_refs, missing = _project_artifacts(self.workspace, project_codebase_id)
        if missing:
            return _project_result(name, "needs_review", "required regression artifacts missing", "artifact_missing", artifact_refs, missing_refs=missing, codebase_id=project_codebase_id)
        return _project_result(name, "accepted", "", "needs_review", artifact_refs, codebase_id=project_codebase_id)


def public_regression_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "multi_project_regression",
        "expanded_matrix": payload.get("expanded_matrix") or {},
        "artifact_diff": payload.get("artifact_diff") or {},
        "failure_diagnosis": payload.get("failure_diagnosis") or {},
        "report": {"format": "markdown", "content": payload.get("report") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _bundle(workspace_id: str, codebase_id: str, matrix: dict[str, Any], artifact_diff: dict[str, Any], failure_diagnosis: dict[str, Any], report: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    return {
        "schema_version": "v2.54-58",
        "artifact_type": "multi_project_regression",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "expanded_matrix": matrix,
        "artifact_diff": artifact_diff,
        "failure_diagnosis": failure_diagnosis,
        "report": report,
        "summary": dict(matrix.get("summary") or {}),
        "artifact_refs": refs,
        "warnings": list(matrix.get("warnings") or []) + list(artifact_diff.get("warnings") or []) + list(failure_diagnosis.get("warnings") or []),
        "unresolved": list(matrix.get("unresolved") or []) + list(artifact_diff.get("unresolved") or []) + list(failure_diagnosis.get("unresolved") or []),
        "next_actions": ["knowledge_code_human_agent_deepening_regression_read"],
    }


def _normalize_projects(projects: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    by_name = {str(item.get("name") or item.get("display_name") or ""): dict(item) for item in list(projects or [])}
    rows = []
    for name in PROJECTS:
        item = by_name.get(name) or {}
        evidence_mode = item.get("evidence_mode") or "real"
        rows.append({"name": name, "path": item.get("path") or item.get("repo_path") or ("" if evidence_mode == "structured_unavailable" else _default_path(name)), "evidence_mode": evidence_mode, "reason": item.get("reason") or ""})
    return rows


def _default_path(name: str) -> str:
    candidates = {
        "data_service": ["/mnt/c/workSpace/data_service"],
        "HarnessOS": ["/mnt/c/workSpace/HarnessOS", "/mnt/c/workSpace/harnessOS"],
        "Navia": ["/mnt/c/workSpace/Navia", "/mnt/c/workSpace/navia"],
        "codexPat": ["/mnt/c/workSpace/codexPat"],
    }
    for item in candidates.get(name, []):
        if Path(item).exists():
            return item
    return candidates.get(name, [""])[0]


def _project_artifacts(workspace: Path, codebase_id: str) -> tuple[list[dict[str, str]], list[str]]:
    checks = [
        ("project_story", project_story_path(workspace, codebase_id)),
        ("risk_priority", risk_priority_path(workspace, codebase_id)),
        ("chart_audit", chart_audit_path(workspace, codebase_id)),
        ("workflow_bundle", _first_task_artifact(workspace, codebase_id, "workflow_bundle.json")),
        ("stop_conditions", _first_task_artifact(workspace, codebase_id, "stop_conditions.json")),
        ("suggested_tests", _first_task_artifact(workspace, codebase_id, "suggested_tests.json")),
        ("evidence_loop", evidence_loop_path(workspace, codebase_id)),
    ]
    refs = []
    missing = []
    for artifact_type, path in checks:
        if path and path.exists():
            refs.append({"type": artifact_type, "artifact_ref": _artifact_ref(codebase_id, artifact_type, path)})
        else:
            missing.append(artifact_type)
    return refs, missing


def _first_task_artifact(workspace: Path, codebase_id: str, filename: str) -> Path | None:
    root = workflow_bundle_path(workspace, codebase_id, "TASK").parents[1]
    if not root.exists():
        return None
    for item in sorted(root.iterdir()):
        if item.is_dir() and (item / filename).exists():
            return item / filename
    return None


def _artifact_ref(codebase_id: str, artifact_type: str, path: Path) -> str:
    parts = list(path.parts)
    if "human_agent_deepening" in parts:
        index = parts.index("human_agent_deepening")
        suffix = "/".join(parts[index + 1 :])
        return f"human_agent_deepening://{codebase_id}/{suffix}"
    return f"human_agent_deepening://{codebase_id}/{artifact_type}"


def _project_result(name: str, status: str, reason: str, category: str, artifact_refs: list[dict[str, str]], *, missing_refs: list[str] | None = None, codebase_id: str | None = None) -> dict[str, Any]:
    if status not in ALLOWED_STATUSES:
        status = "needs_review"
    return {
        "project": name,
        "codebase_id": codebase_id,
        "status": status,
        "reason": reason,
        "test_command": "V2.57 artifact availability and regression expansion inspection",
        "artifact_refs": artifact_refs,
        "evidence_refs": artifact_refs,
        "missing_refs": list(missing_refs or []),
        "failure_category": category if category in FAILURE_CATEGORIES else "needs_review",
        "accepted_evidence_ok": status != "accepted" or bool(artifact_refs),
    }


def _artifact_diff(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], results: list[dict[str, Any]]) -> dict[str, Any]:
    diff_items = []
    for row in results:
        diff_items.append(
            {
                "project": row["project"],
                "baseline_ref": "V2.52 closure matrix",
                "current_ref": "V2.54-V2.56 human_agent_deepening artifacts",
                "status": row["status"],
                "missing_refs": row.get("missing_refs", []),
                "artifact_ref_count": len(row.get("artifact_refs", [])),
            }
        )
    false_green = [row["project"] for row in results if row["status"] == "accepted" and not row.get("artifact_refs")]
    return {
        **base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="multi_project_artifact_diff", generated_at=generated_at, artifact_refs=refs, evidence_refs=[ref for row in results for ref in row.get("artifact_refs", [])]),
        "baseline_ref": "agent_productization://closure/real_repo_matrix.json",
        "current_ref": "human_agent_deepening://regression_expansion/expanded_matrix.json",
        "diff_items": diff_items,
        "status": "accepted" if not false_green else "needs_review",
        "false_green_risk": {"accepted_without_artifacts": false_green, "semantic_equivalence_claimed": False},
    }


def _failure_diagnosis(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], results: list[dict[str, Any]]) -> dict[str, Any]:
    failures = []
    for row in results:
        if row["status"] == "accepted":
            continue
        failures.append(
            {
                "project": row["project"],
                "command": row["test_command"],
                "category": row["failure_category"],
                "reason": row["reason"],
                "evidence_refs": row.get("artifact_refs", []),
            }
        )
    return {
        **base_artifact(workspace_id=workspace_id, codebase_id=codebase_id, phase=PHASE, artifact_type="multi_project_failure_diagnosis", generated_at=generated_at, artifact_refs=refs, evidence_refs=[ref for row in results for ref in row.get("artifact_refs", [])]),
        "failures": failures,
        "allowed_categories": sorted(FAILURE_CATEGORIES),
        "summary": {"failure_count": len(failures)},
    }


def _render_report(matrix: dict[str, Any], artifact_diff: dict[str, Any], failure_diagnosis: dict[str, Any]) -> str:
    lines = [
        "# Multi-project Regression Expansion",
        "",
        f"- project_count: `{matrix['summary']['project_count']}`",
        f"- accepted_count: `{matrix['summary']['accepted_count']}`",
        f"- structured_unavailable_count: `{matrix['summary']['structured_unavailable_count']}`",
        f"- needs_review_count: `{matrix['summary']['needs_review_count']}`",
        "",
        "## Project Results",
    ]
    for row in matrix.get("results", []):
        lines.append(f"- `{row['project']}`: `{row['status']}` artifacts={len(row.get('artifact_refs', []))} missing={len(row.get('missing_refs', []))}")
    lines.extend(["", "## Artifact Diff"])
    for item in artifact_diff.get("diff_items", []):
        lines.append(f"- `{item['project']}`: `{item['status']}` missing={len(item.get('missing_refs', []))}")
    lines.extend(["", "## Failure Diagnosis"])
    if not failure_diagnosis.get("failures"):
        lines.append("- no failure diagnosed")
    for item in failure_diagnosis.get("failures", []):
        lines.append(f"- `{item['project']}` {item['category']}: {item['reason']}")
    return "\n".join(lines) + "\n"
