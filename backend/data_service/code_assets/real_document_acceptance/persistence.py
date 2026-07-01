"""Persistence helpers for V2.81-V2.85 real document acceptance artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import read_json, write_json

from ..artifacts import codebase_dir
from .shared import artifact_uri


def stage_dir(workspace: Path, codebase_id: str) -> Path:
    return codebase_dir(workspace, codebase_id) / "real_document_acceptance"


def section_dir(workspace: Path, codebase_id: str, section: str) -> Path:
    return stage_dir(workspace, codebase_id) / section


def _path(workspace: Path, codebase_id: str, section: str, filename: str) -> Path:
    return section_dir(workspace, codebase_id, section) / filename


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _read_json_required(path: Path, code: str) -> dict[str, Any]:
    payload = read_json(path, None)
    if not payload:
        raise FileNotFoundError(code)
    return payload


def _read_text_required(path: Path, code: str) -> str:
    if not path.exists():
        raise FileNotFoundError(code)
    return path.read_text(encoding="utf-8")


def sample_contract_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "sample_contract", "artifact_ref": artifact_uri(codebase_id, "sample_contract", "sample_contract.json")},
        {"type": "manual_scenario_plan", "artifact_ref": artifact_uri(codebase_id, "sample_contract", "manual_scenario_plan.md")},
    ]


def real_e2e_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "import_run", "artifact_ref": artifact_uri(codebase_id, "real_e2e", "import_run.json")},
        {"type": "wiki_artifact_review", "artifact_ref": artifact_uri(codebase_id, "real_e2e", "wiki_artifact_review.json")},
        {"type": "real_document_e2e_report", "artifact_ref": artifact_uri(codebase_id, "real_e2e", "real_document_e2e_report.md")},
    ]


def retrieval_trace_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "query_trace_review", "artifact_ref": artifact_uri(codebase_id, "retrieval_trace", "query_trace_review.json")},
        {"type": "graphrag_review", "artifact_ref": artifact_uri(codebase_id, "retrieval_trace", "graphrag_review.json")},
        {"type": "source_trace_review", "artifact_ref": artifact_uri(codebase_id, "retrieval_trace", "source_trace_review.md")},
    ]


def quality_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "quality_governance_review", "artifact_ref": artifact_uri(codebase_id, "quality", "quality_governance_review.json")},
        {"type": "correction_acceptance_report", "artifact_ref": artifact_uri(codebase_id, "quality", "correction_acceptance_report.md")},
    ]


def release_closure_artifact_refs(codebase_id: str) -> list[dict[str, str]]:
    return [
        {"type": "release_closure_rerun", "artifact_ref": artifact_uri(codebase_id, "release_closure", "release_closure_rerun.json")},
        {"type": "final_manual_acceptance_report", "artifact_ref": artifact_uri(codebase_id, "release_closure", "final_manual_acceptance_report.md")},
    ]


def write_sample_contract(workspace: Path, codebase_id: str, contract: dict[str, Any], plan: str) -> None:
    write_json(_path(workspace, codebase_id, "sample_contract", "sample_contract.json"), contract)
    _write_text(_path(workspace, codebase_id, "sample_contract", "manual_scenario_plan.md"), plan)


def read_sample_contract(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "sample_contract", "sample_contract.json"), "REAL_DOCUMENT_SAMPLE_CONTRACT_NOT_BUILT")


def read_manual_scenario_plan(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "sample_contract", "manual_scenario_plan.md"), "REAL_DOCUMENT_SAMPLE_CONTRACT_NOT_BUILT")


def write_real_e2e(workspace: Path, codebase_id: str, import_run: dict[str, Any], wiki_review: dict[str, Any], report: str) -> None:
    write_json(_path(workspace, codebase_id, "real_e2e", "import_run.json"), import_run)
    write_json(_path(workspace, codebase_id, "real_e2e", "wiki_artifact_review.json"), wiki_review)
    _write_text(_path(workspace, codebase_id, "real_e2e", "real_document_e2e_report.md"), report)


def read_import_run(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "real_e2e", "import_run.json"), "REAL_DOCUMENT_E2E_NOT_BUILT")


def read_wiki_artifact_review(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "real_e2e", "wiki_artifact_review.json"), "REAL_DOCUMENT_E2E_NOT_BUILT")


def read_real_document_e2e_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "real_e2e", "real_document_e2e_report.md"), "REAL_DOCUMENT_E2E_NOT_BUILT")


def write_retrieval_trace(workspace: Path, codebase_id: str, query_review: dict[str, Any], graph_review: dict[str, Any], trace_report: str) -> None:
    write_json(_path(workspace, codebase_id, "retrieval_trace", "query_trace_review.json"), query_review)
    write_json(_path(workspace, codebase_id, "retrieval_trace", "graphrag_review.json"), graph_review)
    _write_text(_path(workspace, codebase_id, "retrieval_trace", "source_trace_review.md"), trace_report)


def read_query_trace_review(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "retrieval_trace", "query_trace_review.json"), "RETRIEVAL_TRACE_NOT_BUILT")


def read_graphrag_review(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "retrieval_trace", "graphrag_review.json"), "RETRIEVAL_TRACE_NOT_BUILT")


def read_source_trace_review(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "retrieval_trace", "source_trace_review.md"), "RETRIEVAL_TRACE_NOT_BUILT")


def write_quality(workspace: Path, codebase_id: str, review: dict[str, Any], report: str) -> None:
    write_json(_path(workspace, codebase_id, "quality", "quality_governance_review.json"), review)
    _write_text(_path(workspace, codebase_id, "quality", "correction_acceptance_report.md"), report)


def read_quality_governance_review(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "quality", "quality_governance_review.json"), "QUALITY_ACCEPTANCE_NOT_BUILT")


def read_correction_acceptance_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "quality", "correction_acceptance_report.md"), "QUALITY_ACCEPTANCE_NOT_BUILT")


def write_release_closure(workspace: Path, codebase_id: str, rerun: dict[str, Any], report: str) -> None:
    write_json(_path(workspace, codebase_id, "release_closure", "release_closure_rerun.json"), rerun)
    _write_text(_path(workspace, codebase_id, "release_closure", "final_manual_acceptance_report.md"), report)


def read_release_closure_rerun(workspace: Path, codebase_id: str) -> dict[str, Any]:
    return _read_json_required(_path(workspace, codebase_id, "release_closure", "release_closure_rerun.json"), "RELEASE_CLOSURE_RERUN_NOT_BUILT")


def read_final_manual_acceptance_report(workspace: Path, codebase_id: str) -> str:
    return _read_text_required(_path(workspace, codebase_id, "release_closure", "final_manual_acceptance_report.md"), "RELEASE_CLOSURE_RERUN_NOT_BUILT")
