from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.stabilization_e2e_portal.public_surface import PublicSurfaceStabilizationService


WORKSPACE_ID = "v259-real-e2e"
WORKSPACE_ROOT = Path(".tmp/v259-real-workspace")
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
    service = PublicSurfaceStabilizationService(workspace, workspace_id=WORKSPACE_ID)
    built = service.build_surface(codebase_id)
    read_back = service.read_surface(codebase_id)
    snapshot = read_back["snapshot"]
    parity = read_back["parity_matrix"]
    raw = json.dumps(read_back, ensure_ascii=False)
    status = (
        "accepted"
        if snapshot.get("discovery_mode") == "registry_inspection"
        and snapshot.get("hardcoded_expected_only") is False
        and len(snapshot.get("mcp_tools") or []) >= 8
        and len(snapshot.get("cli_commands") or []) >= 8
        and len(snapshot.get("http_routes") or []) >= 8
        and all(item.get("parity_status") == "accepted" for item in parity.get("capabilities", []))
        and str(PROJECT) not in raw
        else "needs_review"
    )
    payload = {
        "workspace_id": WORKSPACE_ID,
        "project": "data_service",
        "status": status,
        "codebase_id": codebase_id,
        "discovery_mode": snapshot.get("discovery_mode"),
        "hardcoded_expected_only": snapshot.get("hardcoded_expected_only"),
        "mcp_tool_count": len(snapshot.get("mcp_tools") or []),
        "cli_command_count": len(snapshot.get("cli_commands") or []),
        "http_route_count": len(snapshot.get("http_routes") or []),
        "parity_statuses": [item.get("parity_status") for item in parity.get("capabilities", [])],
        "absolute_path_leak": str(PROJECT) in raw,
        "artifact_refs": built.get("artifact_refs", []),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if status == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
