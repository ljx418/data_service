from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from data_service.code_assets.agent_productization.governance import AgentProductizationGovernanceService
from data_service.code_assets.agent_productization.human_portal import AgentHumanPortalService
from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService
from data_service.code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService
from data_service.code_assets.human_agent_deepening.evidence_loop import DocCodeEvidenceLoopService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.mcp_tool_registry import all_tool_specs


WORKSPACE_ID = "v256-real-e2e"
WORKSPACE_ROOT = Path(".tmp/v256-real-workspace")
PROJECTS = {
    "data_service": Path("/mnt/c/workSpace/data_service"),
    "codexPat": Path("/mnt/c/workSpace/codexPat"),
}


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
            governance = AgentProductizationGovernanceService(workspace, workspace_id=WORKSPACE_ID)
            governance.record_feedback(codebase_id, target_type="portal_section", target_id="profile_onboarding", action="clarify", rule_type="read_time_overlay", severity="low", reason="approved evidence loop finding", suggested_value="approved")
            governance.record_feedback(codebase_id, target_type="portal_section", target_id="profile_onboarding", action="clarify", rule_type="read_time_overlay", severity="medium", reason="revoked evidence loop finding", suggested_value="revoked")
            rules = governance.build_rules(codebase_id)["rules"]
            for rule in rules:
                if rule["suggested_value"] == "approved":
                    governance.review_rule(codebase_id, rule["rule_id"], status="approved", reviewer="e2e", note="approve")
                if rule["suggested_value"] == "revoked":
                    governance.review_rule(codebase_id, rule["rule_id"], status="revoked", reviewer="e2e", note="revoke")
            built = DocCodeEvidenceLoopService(workspace, workspace_id=WORKSPACE_ID).build_evidence_loop(codebase_id)
            read_back = DocCodeEvidenceLoopService(workspace, workspace_id=WORKSPACE_ID).read_evidence_loop(codebase_id)
            statuses = {item.get("status") for item in read_back["evidence_loop"].get("findings", [])}
            actions = {item.get("action") for item in read_back.get("decision_history", [])}
            blockers = [item for item in built.get("unresolved", []) if isinstance(item, dict) and item.get("status") == "structured_blocker"]
            status = "accepted"
            reason = ""
            if not read_back["rule_effect"].get("hash_unchanged"):
                status = "needs_review"
                reason = "upstream hash changed"
            if not {"approve", "revoke"} <= actions:
                status = "needs_review"
                reason = "approve/revoke decisions not visible"
            if not {"supported", "contradicted"} <= statuses:
                status = "needs_review"
                reason = "expected finding statuses not visible"
            if blockers:
                status = "needs_review"
                reason = "structured blocker present"
            results.append(
                {
                    "project": name,
                    "status": status,
                    "reason": reason,
                    "codebase_id": codebase_id,
                    "artifact_refs": built.get("artifact_refs", []),
                    "summary": built.get("summary", {}),
                    "visible_statuses": sorted(statuses),
                    "visible_actions": sorted(actions),
                    "structured_blocker_count": len(blockers),
                }
            )
        except Exception as exc:  # noqa: BLE001
            results.append({"project": name, "status": "structured_blocker", "reason": exc.__class__.__name__})

    payload = {"workspace_id": WORKSPACE_ID, "results": results}
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if all(item["status"] in {"accepted", "structured_unavailable"} for item in results) and any(item["status"] == "accepted" for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
