from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.stabilization_e2e_portal.e2e_expansion import RealProjectE2EExpansionService


WORKSPACE_ID = "v260-real-e2e"
WORKSPACE_ROOT = Path(".tmp/v260-real-workspace")
PROJECT = Path("/mnt/c/workSpace/data_service")
SIBLINGS = {
    "codexPat": Path("/mnt/c/workSpace/codexPat"),
    "HarnessOS": Path("/mnt/c/workSpace/HarnessOS"),
    "Navia": Path("/mnt/c/workSpace/navia"),
}


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
    projects = [{"name": "data_service", "path": str(PROJECT)}]
    for name, path in SIBLINGS.items():
        projects.append(
            {
                "name": name,
                "status": "structured_unavailable",
                "evidence_mode": "structured_unavailable",
                "path": str(path),
                "reason": "full external project artifact preparation not executed in bounded V2.60 E2E run",
            }
        )
    service = RealProjectE2EExpansionService(workspace, workspace_id=WORKSPACE_ID)
    built = service.build_e2e(codebase_id, projects=projects)
    rows = built["project_e2e_matrix"]["projects"]
    data_service_status = next(row["status"] for row in rows if row["name"] == "data_service")
    unavailable_accepted_count = sum(1 for row in rows if row["status"] == "structured_unavailable" and row["status"] == "accepted")
    mock_only_accepted_count = built["summary"]["mock_only_accepted_count"]
    invalid_category_count = sum(1 for item in built["project_failure_diagnosis"]["items"] if item["category"] not in built["project_failure_diagnosis"]["categories"])
    status = "accepted" if data_service_status == "accepted" and unavailable_accepted_count == 0 and mock_only_accepted_count == 0 and invalid_category_count == 0 else "needs_review"
    payload = {
        "workspace_id": WORKSPACE_ID,
        "project": "data_service",
        "status": status,
        "codebase_id": codebase_id,
        "project_results": rows,
        "unavailable_accepted_count": unavailable_accepted_count,
        "mock_only_accepted_count": mock_only_accepted_count,
        "invalid_category_count": invalid_category_count,
        "artifact_refs": built.get("artifact_refs", []),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if status == "accepted" else 1


if __name__ == "__main__":
    raise SystemExit(main())
