"""HTTP routes for V2.86-V2.90 full corpus release hardening."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.code_assets.real_document_full_corpus_release.external_project_closure import ExternalProjectE2EClosureService, public_external_project_payload
from data_service.code_assets.real_document_full_corpus_release.full_corpus import FullCorpusE2EHardeningService, public_full_corpus_payload
from data_service.code_assets.real_document_full_corpus_release.quality_review import QualityReviewClosureService, public_quality_review_payload
from data_service.code_assets.real_document_full_corpus_release.release_gate import ReleaseGateRestoreHygieneService, public_release_gate_payload
from data_service.code_assets.real_document_full_corpus_release.route_a_acceptance import RouteAAcceptanceService, public_route_a_payload
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Real Document Full Corpus Release"], dependencies=[Depends(verify_knowledge_access)])


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/full-corpus/build")
async def build_full_corpus(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "real_document_full_corpus", "knowledge_code_real_document_full_corpus_release_full_corpus_read", lambda workspace, meta: FullCorpusE2EHardeningService(workspace, workspace_id=str(meta["workspace_id"])).build_full_corpus(codebase_id, options=dict((payload or {}).get("options") or {})), public_full_corpus_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/full-corpus")
async def read_full_corpus(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_full_corpus", None, lambda workspace, meta: FullCorpusE2EHardeningService(workspace, workspace_id=str(meta["workspace_id"])).read_full_corpus(codebase_id), public_full_corpus_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/route-a/build")
async def build_route_a(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "real_document_route_a_acceptance", "knowledge_code_real_document_full_corpus_release_route_a_read", lambda workspace, meta: RouteAAcceptanceService(workspace, workspace_id=str(meta["workspace_id"])).build_route_a(codebase_id, acceptance_state=dict((payload or {}).get("acceptance_state") or {})), public_route_a_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/route-a")
async def read_route_a(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_route_a_acceptance", None, lambda workspace, meta: RouteAAcceptanceService(workspace, workspace_id=str(meta["workspace_id"])).read_route_a(codebase_id), public_route_a_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/quality-review/build")
async def build_quality_review(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "real_document_quality_review", "knowledge_code_real_document_full_corpus_release_quality_review_read", lambda workspace, meta: QualityReviewClosureService(workspace, workspace_id=str(meta["workspace_id"])).build_quality_review(codebase_id, review_state=dict((payload or {}).get("review_state") or {})), public_quality_review_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/quality-review")
async def read_quality_review(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_quality_review", None, lambda workspace, meta: QualityReviewClosureService(workspace, workspace_id=str(meta["workspace_id"])).read_quality_review(codebase_id), public_quality_review_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/external-project/build")
async def build_external_project(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "real_document_external_project", "knowledge_code_real_document_full_corpus_release_external_project_read", lambda workspace, meta: ExternalProjectE2EClosureService(workspace, workspace_id=str(meta["workspace_id"])).build_external_project(codebase_id, project_paths=dict((payload or {}).get("project_paths") or {})), public_external_project_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/external-project")
async def read_external_project(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_external_project", None, lambda workspace, meta: ExternalProjectE2EClosureService(workspace, workspace_id=str(meta["workspace_id"])).read_external_project(codebase_id), public_external_project_payload)


@router.post("/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/release-gate/build")
async def build_release_gate(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "real_document_release_gate", "knowledge_code_real_document_full_corpus_release_release_gate_read", lambda workspace, meta: ReleaseGateRestoreHygieneService(workspace, workspace_id=str(meta["workspace_id"])).build_release_gate(codebase_id, gate_state=dict((payload or {}).get("gate_state") or {})), public_release_gate_payload)


@router.get("/{workspace_id}/codebases/{codebase_id}/real-document-full-corpus-release/release-gate")
async def read_release_gate(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_release_gate", None, lambda workspace, meta: ReleaseGateRestoreHygieneService(workspace, workspace_id=str(meta["workspace_id"])).read_release_gate(codebase_id), public_release_gate_payload)


def _run(workspace_id: str, codebase_id: str, key: str, next_action: str | None, callback, public):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = callback(workspace, meta)
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), _next_action_for(str(exc)))
    data = {key: public(result)}
    next_actions = [next_action] if next_action else None
    return envelope(workspace_id=str(meta["workspace_id"]), artifact_refs=result.get("artifact_refs", []), next_actions=next_actions, data=_with_v2(str(meta["workspace_id"]), codebase_id, data, result))


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body


def _error(status_code: int, workspace_id: str, codebase_id: str, error: str, next_action: str):
    payload = {"v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=error, message=error, next_actions=[next_action])}
    return JSONResponse(status_code=status_code, content=payload)


def _next_action_for(message: str) -> str:
    if "FULL_CORPUS" in message:
        return "knowledge_code_real_document_full_corpus_release_full_corpus_build"
    if "ROUTE_A" in message:
        return "knowledge_code_real_document_full_corpus_release_route_a_build"
    if "QUALITY_REVIEW" in message:
        return "knowledge_code_real_document_full_corpus_release_quality_review_build"
    if "EXTERNAL_PROJECT" in message:
        return "knowledge_code_real_document_full_corpus_release_external_project_build"
    return "knowledge_code_real_document_full_corpus_release_release_gate_build"
