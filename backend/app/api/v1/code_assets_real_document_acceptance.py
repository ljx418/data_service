"""HTTP routes for V2.81-V2.85 real document acceptance stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from data_service.code_assets.envelope import v2_error_envelope, v2_success_envelope
from data_service.code_assets.real_document_acceptance.service import RealDocumentAcceptanceService, public_real_document_payload
from data_service.mcp_common import envelope
from data_service.mcp_workspace_runtime import WorkspaceRuntime

from .data_service import verify_knowledge_access


router = APIRouter(prefix="/workspaces", tags=["Real Document Acceptance"], dependencies=[Depends(verify_knowledge_access)])


def _runtime() -> WorkspaceRuntime:
    return WorkspaceRuntime(Path.cwd() / "workspace")


def _workspace_for(workspace_id: str) -> tuple[Path, dict[str, Any]]:
    runtime = _runtime()
    workspace = runtime.resolve_workspace(workspace_id, None)
    meta = runtime.ensure_workspace_meta(workspace)
    return workspace, meta


@router.post("/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/sample-contract/build")
async def build_sample_contract(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "real_document_acceptance_sample_contract", "knowledge_code_real_document_acceptance_sample_contract_read", lambda service: service.build_sample_contract(codebase_id, sample_config=dict((payload or {}).get("sample_config") or {})))


@router.get("/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/sample-contract")
async def read_sample_contract(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_acceptance_sample_contract", None, lambda service: service.read_sample_contract(codebase_id))


@router.post("/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/real-e2e/build")
async def build_real_e2e(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_acceptance_real_e2e", "knowledge_code_real_document_acceptance_real_e2e_read", lambda service: service.build_real_e2e(codebase_id))


@router.get("/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/real-e2e")
async def read_real_e2e(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_acceptance_real_e2e", None, lambda service: service.read_real_e2e(codebase_id))


@router.post("/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/retrieval-trace/build")
async def build_retrieval_trace(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_acceptance_retrieval_trace", "knowledge_code_real_document_acceptance_retrieval_trace_read", lambda service: service.build_retrieval_trace(codebase_id))


@router.get("/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/retrieval-trace")
async def read_retrieval_trace(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_acceptance_retrieval_trace", None, lambda service: service.read_retrieval_trace(codebase_id))


@router.post("/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/quality/build")
async def build_quality(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_acceptance_quality", "knowledge_code_real_document_acceptance_quality_read", lambda service: service.build_quality(codebase_id))


@router.get("/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/quality")
async def read_quality(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_acceptance_quality", None, lambda service: service.read_quality(codebase_id))


@router.post("/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/release-closure/build")
async def build_release_closure(workspace_id: str, codebase_id: str, payload: dict[str, Any] | None = None):
    return _run(workspace_id, codebase_id, "real_document_acceptance_release_closure", "knowledge_code_real_document_acceptance_release_closure_read", lambda service: service.build_release_closure(codebase_id, approval_state=dict((payload or {}).get("approval_state") or {})))


@router.get("/{workspace_id}/codebases/{codebase_id}/real-document-acceptance/release-closure")
async def read_release_closure(workspace_id: str, codebase_id: str):
    return _run(workspace_id, codebase_id, "real_document_acceptance_release_closure", None, lambda service: service.read_release_closure(codebase_id))


def _run(workspace_id: str, codebase_id: str, key: str, next_action: str | None, callback):
    workspace, meta = _workspace_for(workspace_id)
    try:
        result = callback(RealDocumentAcceptanceService(workspace, workspace_id=str(meta["workspace_id"])))
    except FileNotFoundError as exc:
        return _error(404, str(meta["workspace_id"]), codebase_id, str(exc), _next_action_for(str(exc)))
    return _ok(str(meta["workspace_id"]), codebase_id, result, key, next_action)


def _ok(workspace_id: str, codebase_id: str, result: dict[str, Any], key: str, next_action: str | None = None):
    data = {key: public_real_document_payload(result)}
    next_actions = [next_action] if next_action else None
    return envelope(workspace_id=workspace_id, artifact_refs=result.get("artifact_refs", []), next_actions=next_actions, data=_with_v2(workspace_id, codebase_id, data, result))


def _with_v2(workspace_id: str, codebase_id: str, data: dict[str, Any], payload: dict[str, Any]) -> dict[str, Any]:
    body = dict(data)
    body["v2"] = v2_success_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, data=data, artifact_refs=payload.get("artifact_refs", []), warnings=payload.get("warnings", []), unresolved=payload.get("unresolved", []), next_actions=payload.get("next_actions", []))
    return body


def _error(status_code: int, workspace_id: str, codebase_id: str, error: str, next_action: str):
    payload = {"v2": v2_error_envelope(workspace_id=workspace_id, codebase_id=codebase_id, snapshot_id=None, code=error, message=error, next_actions=[next_action])}
    return JSONResponse(status_code=status_code, content=payload)


def _next_action_for(message: str) -> str:
    if "REAL_DOCUMENT_SAMPLE" in message:
        return "knowledge_code_real_document_acceptance_sample_contract_build"
    if "REAL_DOCUMENT_E2E" in message:
        return "knowledge_code_real_document_acceptance_real_e2e_build"
    if "RETRIEVAL_TRACE" in message:
        return "knowledge_code_real_document_acceptance_retrieval_trace_build"
    if "QUALITY_ACCEPTANCE" in message:
        return "knowledge_code_real_document_acceptance_quality_build"
    return "knowledge_code_real_document_acceptance_release_closure_build"
