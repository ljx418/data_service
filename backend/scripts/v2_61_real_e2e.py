from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.stabilization_e2e_portal.packaging import CANONICAL_RUNNER, FOCUSED_COMMAND, AcceptancePackagingService


WORKSPACE_ID = "v261-real-e2e"
WORKSPACE_ROOT = Path(".tmp/v261-real-workspace")
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
    tmp_exists_before = (PROJECT / ".tmp").exists()
    codebase_id = CodebaseRegistry(workspace, workspace_id=WORKSPACE_ID).import_codebase(path=str(PROJECT), name="data_service")["asset"].codebase_id
    built = AcceptancePackagingService(workspace, workspace_id=WORKSPACE_ID).build_package(codebase_id, repo_root=str(PROJECT))
    tmp_exists_after = (PROJECT / ".tmp").exists()
    manifest = built["package_manifest"]
    entries = manifest.get("entries") or []
    status = (
        "accepted"
        if manifest.get("destructive_action_required") is False
        and tmp_exists_before == tmp_exists_after
        and any(item.get("path") == ".tmp" and item.get("classification") == "local_tmp" for item in entries)
        and CANONICAL_RUNNER in built["handoff_checklist"]
        and FOCUSED_COMMAND in built["handoff_checklist"]
        else "needs_review"
    )
    payload = {
        "workspace_id": WORKSPACE_ID,
        "project": "data_service",
        "status": status,
        "codebase_id": codebase_id,
        "destructive_action_required": manifest.get("destructive_action_required"),
        "tmp_exists_before": tmp_exists_before,
        "tmp_exists_after": tmp_exists_after,
        "tmp_classified": any(item.get("path") == ".tmp" and item.get("classification") == "local_tmp" for item in entries),
        "canonical_runner_present": CANONICAL_RUNNER in built["handoff_checklist"],
        "focused_command_present": FOCUSED_COMMAND in built["handoff_checklist"],
        "artifact_refs": built.get("artifact_refs", []),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if status == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
