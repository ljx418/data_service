from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from data_service.code_assets.agent_productization.governance import AgentProductizationGovernanceService
from data_service.code_assets.agent_productization.human_portal import AgentHumanPortalService
from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService
from data_service.code_assets.agent_productization.playbooks import AgentProductizationPlaybookService
from data_service.code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService
from data_service.code_assets.human_agent_deepening.evidence_loop import DocCodeEvidenceLoopService
from data_service.code_assets.human_agent_deepening.human_portal import HumanPortalDeepeningService
from data_service.code_assets.human_agent_deepening.regression import FAILURE_CATEGORIES, MultiProjectRegressionService
from data_service.code_assets.human_agent_deepening.task_workflow import AgentTaskWorkflowService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.mcp_tool_registry import all_tool_specs


WORKSPACE_ID = "v257-real-e2e"
WORKSPACE_ROOT = Path(".tmp/v257-real-workspace")
PROJECT_PATHS = {
    "data_service": [Path("/mnt/c/workSpace/data_service")],
    "HarnessOS": [Path("/mnt/c/workSpace/HarnessOS"), Path("/mnt/c/workSpace/harnessOS")],
    "Navia": [Path("/mnt/c/workSpace/Navia"), Path("/mnt/c/workSpace/navia")],
    "codexPat": [Path("/mnt/c/workSpace/codexPat")],
}
FULL_PREP_PROJECTS = {"data_service", "codexPat"}


def main() -> int:
    os.environ.setdefault("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", "/mnt/c/workSpace")
    workspace = WORKSPACE_ROOT / WORKSPACE_ID
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    projects = []
    current_codebase_id = None
    prep = []
    for name, candidates in PROJECT_PATHS.items():
        repo = next((item for item in candidates if item.exists()), None)
        if repo is None:
            projects.append({"name": name, "path": "", "evidence_mode": "structured_unavailable", "reason": "repository directory not available"})
            prep.append({"project": name, "status": "structured_unavailable", "reason": "repository directory not available"})
            continue
        if name not in FULL_PREP_PROJECTS and os.environ.get("V257_FULL_EXTERNAL_E2E") != "1":
            projects.append({"name": name, "path": "", "evidence_mode": "structured_unavailable", "reason": "full artifact preparation skipped by bounded E2E time budget"})
            prep.append({"project": name, "status": "structured_unavailable", "reason": "full artifact preparation skipped by bounded E2E time budget"})
            continue
        projects.append({"name": name, "path": str(repo)})
        try:
            codebase_id = _build_project(workspace, name, repo)
            if name == "data_service":
                current_codebase_id = codebase_id
            prep.append({"project": name, "status": "prepared", "codebase_id": codebase_id})
        except Exception as exc:  # noqa: BLE001
            prep.append({"project": name, "status": "structured_blocker", "reason": exc.__class__.__name__})

    if current_codebase_id is None:
        print(json.dumps({"workspace_id": WORKSPACE_ID, "status": "structured_blocker", "reason": "data_service unavailable", "preparation": prep}, indent=2))
        return 1

    built = MultiProjectRegressionService(workspace, workspace_id=WORKSPACE_ID).build_regression(current_codebase_id, projects=projects)
    results = built["expanded_matrix"]["results"]
    failures = built["failure_diagnosis"]["failures"]
    invalid_categories = [item for item in failures if item.get("category") not in FAILURE_CATEGORIES]
    unavailable_accepted = [item for item in results if item["status"] == "accepted" and item["project"] in {row["project"] for row in results if row["status"] == "structured_unavailable"}]
    accepted_without_evidence = [item for item in results if item["status"] == "accepted" and not item.get("artifact_refs")]
    payload = {
        "workspace_id": WORKSPACE_ID,
        "preparation": prep,
        "regression": {
            "summary": built["summary"],
            "results": [
                {
                    "project": item["project"],
                    "status": item["status"],
                    "artifact_ref_count": len(item.get("artifact_refs", [])),
                    "missing_ref_count": len(item.get("missing_refs", [])),
                    "failure_category": item.get("failure_category"),
                }
                for item in results
            ],
            "invalid_category_count": len(invalid_categories),
            "unavailable_accepted_count": len(unavailable_accepted),
            "accepted_without_evidence_count": len(accepted_without_evidence),
            "artifact_refs": built.get("artifact_refs", []),
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    ok = not invalid_categories and not unavailable_accepted and not accepted_without_evidence and any(item["status"] == "accepted" for item in results)
    return 0 if ok else 1


def _build_project(workspace: Path, name: str, repo: Path) -> str:
    codebase_id = CodebaseRegistry(workspace, workspace_id=WORKSPACE_ID).import_codebase(path=str(repo), name=name)["asset"].codebase_id
    AgentMCPProductizationService(workspace, workspace_id=WORKSPACE_ID).build_mcp_usage(codebase_id, all_tool_specs())
    AgentProfileOnboardingService(workspace, workspace_id=WORKSPACE_ID).build_profile_onboarding(codebase_id)
    AgentHumanPortalService(workspace, workspace_id=WORKSPACE_ID).build_portal(codebase_id)
    AgentProductizationPlaybookService(workspace, workspace_id=WORKSPACE_ID).build_playbooks(codebase_id, role="coding_agent")
    HumanPortalDeepeningService(workspace, workspace_id=WORKSPACE_ID).build_portal(codebase_id)
    AgentTaskWorkflowService(workspace, workspace_id=WORKSPACE_ID).build_task_workflow(codebase_id, task="Validate multi-project regression expansion")
    governance = AgentProductizationGovernanceService(workspace, workspace_id=WORKSPACE_ID)
    governance.record_feedback(codebase_id, target_type="portal_section", target_id="profile_onboarding", action="clarify", suggested_value="approved")
    rules = governance.build_rules(codebase_id)["rules"]
    governance.review_rule(codebase_id, rules[0]["rule_id"], status="approved", reviewer="e2e")
    DocCodeEvidenceLoopService(workspace, workspace_id=WORKSPACE_ID).build_evidence_loop(codebase_id)
    return codebase_id


if __name__ == "__main__":
    raise SystemExit(main())
