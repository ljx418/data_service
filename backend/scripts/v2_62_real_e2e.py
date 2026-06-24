from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.stabilization_e2e_portal.e2e_expansion import RealProjectE2EExpansionService
from data_service.code_assets.stabilization_e2e_portal.packaging import AcceptancePackagingService
from data_service.code_assets.stabilization_e2e_portal.portal_integration import PortalUXIntegrationService
from data_service.code_assets.stabilization_e2e_portal.public_surface import PublicSurfaceStabilizationService


WORKSPACE_ID = "v262-real-e2e"
WORKSPACE_ROOT = Path(".tmp/v262-real-workspace")
PROJECT = Path("/mnt/c/workSpace/data_service")


def main() -> int:
    os.environ.setdefault("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", "/mnt/c/workSpace")
    workspace = WORKSPACE_ROOT / WORKSPACE_ID
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    if not PROJECT.exists():
        print(json.dumps({"workspace_id": WORKSPACE_ID, "project": "data_service", "status": "structured_unavailable", "reason": "data_service repository unavailable"}, indent=2))
        return 1
    codebase_id = CodebaseRegistry(workspace, workspace_id=WORKSPACE_ID).import_codebase(path=str(PROJECT), name="data_service")["asset"].codebase_id
    PublicSurfaceStabilizationService(workspace, workspace_id=WORKSPACE_ID).build_surface(codebase_id)
    RealProjectE2EExpansionService(workspace, workspace_id=WORKSPACE_ID).build_e2e(
        codebase_id,
        projects=[
            {"name": "data_service", "path": str(PROJECT)},
            {"name": "codexPat", "status": "structured_unavailable", "evidence_mode": "structured_unavailable", "reason": "full external artifact preparation not executed in bounded V2.62 E2E run"},
            {"name": "HarnessOS", "status": "structured_unavailable", "evidence_mode": "structured_unavailable", "reason": "full external artifact preparation not executed in bounded V2.62 E2E run"},
            {"name": "Navia", "status": "structured_unavailable", "evidence_mode": "structured_unavailable", "reason": "full external artifact preparation not executed in bounded V2.62 E2E run"},
        ],
    )
    AcceptancePackagingService(workspace, workspace_id=WORKSPACE_ID).build_package(codebase_id, repo_root=str(PROJECT))
    built = PortalUXIntegrationService(workspace, workspace_id=WORKSPACE_ID).build_portal(codebase_id)
    state = built["portal_state_summary"]
    panel_statuses = [item["status"] for item in built["portal_acceptance_panel"]["items"]]
    html = built["project_portal_v3_html"]
    status = (
        "accepted"
        if state.get("contract_stability") == "accepted"
        and state.get("e2e_coverage") == "structured_unavailable"
        and state.get("delivery_readiness") == "accepted"
        and "structured_unavailable" in panel_statuses
        and built["summary"]["raw_mermaid_visible"] is False
        else "needs_review"
    )
    payload = {
        "workspace_id": WORKSPACE_ID,
        "project": "data_service",
        "status": status,
        "codebase_id": codebase_id,
        "contract_stability": state.get("contract_stability"),
        "e2e_coverage": state.get("e2e_coverage"),
        "restore_readiness": state.get("restore_readiness"),
        "delivery_readiness": state.get("delivery_readiness"),
        "panel_statuses": panel_statuses,
        "raw_mermaid_visible": built["summary"]["raw_mermaid_visible"],
        "html_contains_status": "structured_unavailable" in html,
        "artifact_refs": built.get("artifact_refs", []),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if status == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
