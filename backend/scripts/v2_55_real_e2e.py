from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from data_service.code_assets.agent_productization.human_portal import AgentHumanPortalService
from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService
from data_service.code_assets.agent_productization.playbooks import AgentProductizationPlaybookService
from data_service.code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService
from data_service.code_assets.human_agent_deepening.human_portal import HumanPortalDeepeningService
from data_service.code_assets.human_agent_deepening.task_workflow import AgentTaskWorkflowService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.mcp_tool_registry import all_tool_specs


WORKSPACE_ID = "v255-real-e2e"
WORKSPACE_ROOT = Path(".tmp/v255-real-workspace")
TASK = "Implement agent task workflow hardening and acceptance tests"
PROJECTS = {
    "data_service": Path("/mnt/c/workSpace/data_service"),
    "codexPat": Path("/mnt/c/workSpace/codexPat"),
}
FORBIDDEN_CLAIMS = {"runtime_call", "data_flow", "control_flow", "production_topology"}


def main() -> int:
    os.environ.setdefault("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", "/mnt/c/workSpace")
    workspace = WORKSPACE_ROOT / WORKSPACE_ID
    if workspace.exists():
        shutil.rmtree(workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    results = []
    for name, repo in PROJECTS.items():
        if not repo.exists():
            results.append({"project": name, "status": "structured_unavailable", "reason": "repository directory not available"})
            continue
        try:
            codebase_id = CodebaseRegistry(workspace, workspace_id=WORKSPACE_ID).import_codebase(path=str(repo), name=name)["asset"].codebase_id
            AgentMCPProductizationService(workspace, workspace_id=WORKSPACE_ID).build_mcp_usage(codebase_id, all_tool_specs())
            AgentProfileOnboardingService(workspace, workspace_id=WORKSPACE_ID).build_profile_onboarding(codebase_id)
            AgentHumanPortalService(workspace, workspace_id=WORKSPACE_ID).build_portal(codebase_id)
            AgentProductizationPlaybookService(workspace, workspace_id=WORKSPACE_ID).build_playbooks(codebase_id, role="coding_agent")
            HumanPortalDeepeningService(workspace, workspace_id=WORKSPACE_ID).build_portal(codebase_id)
            built = AgentTaskWorkflowService(workspace, workspace_id=WORKSPACE_ID).build_task_workflow(codebase_id, task=TASK)
            read_back = AgentTaskWorkflowService(workspace, workspace_id=WORKSPACE_ID).read_task_workflow(codebase_id, task_id=built["task_id"])
            impact_claims = {item.get("claim_type") for item in read_back["workflow_bundle"].get("impact_candidates", [])}
            bad_test_status = [
                item
                for item in read_back["suggested_tests"].get("tests", [])
                if item.get("status") not in {"recommended", "needs_review", "structured_unavailable"}
                or (not item.get("evidence_refs") and item.get("status") != "needs_review")
            ]
            status = "accepted"
            reason = ""
            if impact_claims & FORBIDDEN_CLAIMS:
                status = "needs_review"
                reason = "forbidden impact claim type present"
            if bad_test_status:
                status = "needs_review"
                reason = "suggested test status invariant failed"
            structured_blockers = [item for item in built.get("unresolved", []) if isinstance(item, dict) and item.get("status") == "structured_blocker"]
            ephemeral_refs = [
                item
                for item in read_back["workflow_bundle"].get("reading_order", []) + read_back["workflow_bundle"].get("impact_candidates", [])
                if str(item.get("path") or "").startswith(".tmp/")
            ]
            if structured_blockers:
                status = "needs_review"
                reason = "structured blocker present"
            if ephemeral_refs:
                status = "needs_review"
                reason = "ephemeral dependency path included"
            if not built.get("summary", {}).get("reading_item_count") or not built.get("summary", {}).get("suggested_test_count"):
                status = "needs_review"
                reason = "workflow has no effective reading order or suggested tests"
            results.append(
                {
                    "project": name,
                    "status": status,
                    "reason": reason,
                    "codebase_id": codebase_id,
                    "task_id": built["task_id"],
                    "artifact_refs": built.get("artifact_refs", []),
                    "summary": built.get("summary", {}),
                    "forbidden_claim_types": sorted(impact_claims & FORBIDDEN_CLAIMS),
                    "bad_test_status_count": len(bad_test_status),
                    "structured_blocker_count": len(structured_blockers),
                    "ephemeral_ref_count": len(ephemeral_refs),
                    "unresolved_count": len(built.get("unresolved", [])),
                }
            )
        except Exception as exc:  # noqa: BLE001 - script must classify E2E failures without traceback leakage.
            results.append({"project": name, "status": "structured_blocker", "reason": exc.__class__.__name__})

    payload = {"workspace_id": WORKSPACE_ID, "task": TASK, "results": results}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if all(item["status"] in {"accepted", "structured_unavailable"} for item in results) and any(item["status"] == "accepted" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
