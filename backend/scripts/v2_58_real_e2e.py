from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from data_service.code_assets.human_agent_deepening.restore_ux import CANONICAL_RUNNER, FAILURE_CATEGORIES, RestoreUXService
from data_service.code_assets.registry import CodebaseRegistry


WORKSPACE_ID = "v258-real-e2e"
WORKSPACE_ROOT = Path(".tmp/v258-real-workspace")
PROJECT = Path("/mnt/c/workSpace/data_service")


def main() -> int:
    os.environ.setdefault("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", "/mnt/c/workSpace")
    workspace = WORKSPACE_ROOT / WORKSPACE_ID
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    if not PROJECT.exists():
        print(json.dumps({"workspace_id": WORKSPACE_ID, "status": "structured_unavailable", "reason": "data_service repository unavailable"}, indent=2))
        return 1
    codebase_id = CodebaseRegistry(workspace, workspace_id=WORKSPACE_ID).import_codebase(path=str(PROJECT), name="data_service")["asset"].codebase_id
    built = RestoreUXService(workspace, workspace_id=WORKSPACE_ID).build_restore_ux(codebase_id)
    read_back = RestoreUXService(workspace, workspace_id=WORKSPACE_ID).read_restore_ux(codebase_id)
    checklist = read_back["restore_checklist"]
    troubleshooting = read_back["troubleshooting"]
    report = read_back["onboarding_report"]
    missing_categories = [item for item in FAILURE_CATEGORIES if item not in troubleshooting]
    raw = json.dumps(read_back, ensure_ascii=False)
    payload = {
        "workspace_id": WORKSPACE_ID,
        "project": "data_service",
        "status": "accepted"
        if CANONICAL_RUNNER in checklist and not missing_categories and report.get("path_redaction_passed") is True and str(PROJECT) not in raw
        else "needs_review",
        "codebase_id": codebase_id,
        "canonical_runner_present": CANONICAL_RUNNER in checklist,
        "missing_category_count": len(missing_categories),
        "path_redaction_passed": report.get("path_redaction_passed"),
        "absolute_path_leak": str(PROJECT) in raw,
        "artifact_refs": built.get("artifact_refs", []),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
