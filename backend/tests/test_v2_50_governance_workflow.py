import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.agent_productization.governance import AgentProductizationGovernanceService
from data_service.code_assets.agent_productization.human_portal import AgentHumanPortalService
from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService
from data_service.code_assets.agent_productization.persistence import governance_feedback_path, governance_overlay_path, governance_rules_path
from data_service.code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_tool_registry import all_tool_specs
from data_service.mcp_workspace_runtime import WorkspaceRuntime


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _write_repo(repo: Path) -> None:
    files = {
        "README.md": "# Governance Fixture\n",
        "docs/V2_TARGET_ARCHITECTURE.md": "# Target Architecture\n\n- Portal has profile onboarding section.\n",
        "src/main.py": "def main():\n    return 'ok'\n",
        "tests/test_main.py": "def test_main():\n    assert True\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "governance_fixture_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V50 Governance")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="GovernanceFixture")["asset"]
    AgentMCPProductizationService(workspace, workspace_id=workspace_id).build_mcp_usage(asset.codebase_id, all_tool_specs())
    AgentProfileOnboardingService(workspace, workspace_id=workspace_id).build_profile_onboarding(asset.codebase_id)
    AgentHumanPortalService(workspace, workspace_id=workspace_id).build_portal(asset.codebase_id)
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload: dict, repo: Path, workspace_root: Path) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw


def _assert_overlay(payload: dict, *, expected_applied=None, min_applied=None, repo: Path, workspace_root: Path) -> None:
    overlay = payload["overlay"]
    if expected_applied is not None:
        assert overlay["summary"]["applied_rule_count"] == expected_applied
    if min_applied is not None:
        assert overlay["summary"]["applied_rule_count"] >= min_applied
    assert overlay["summary"]["source_artifact_hash_unchanged"] is True
    assert overlay["artifact_refs"]
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v50_governance_approve_revoke_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    service = AgentProductizationGovernanceService(workspace, workspace_id=workspace_id)
    feedback_payload = service.record_feedback(
        codebase_id,
        target_type="portal_section",
        target_id="profile_onboarding",
        action="clarify",
        reason="Profile onboarding section should be reviewed",
        suggested_value="Mark profile draft as needs review",
    )
    assert governance_feedback_path(workspace, codebase_id).exists()
    rules_payload = service.build_rules(codebase_id)
    assert governance_rules_path(workspace, codebase_id).exists()
    rule_id = rules_payload["rules"][0]["rule_id"]
    approved_payload = service.review_rule(codebase_id, rule_id, status="approved", reviewer="tester", note="ok")
    assert governance_overlay_path(workspace, codebase_id).exists()
    _assert_overlay(approved_payload, expected_applied=1, repo=repo, workspace_root=workspace_root)
    revoked_payload = service.review_rule(codebase_id, rule_id, status="revoked", reviewer="tester", note="revoke")
    _assert_overlay(revoked_payload, expected_applied=0, repo=repo, workspace_root=workspace_root)

    http_feedback = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/governance/feedback",
        json={"target_type": "portal_section", "target_id": "profile_onboarding", "action": "clarify", "reason": "review", "suggested_value": "needs review"},
    )
    assert http_feedback.status_code == 200
    http_rules = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/governance/rules/build")
    assert http_rules.status_code == 200
    http_rule_id = _v2(http_rules.json())["data"]["agent_productization_governance"]["rules"][0]["rule_id"]
    http_review = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/governance/rules/{http_rule_id}/review", json={"status": "approved", "reviewer": "tester"})
    assert http_review.status_code == 200
    http_overlay = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/governance/overlay")
    assert http_overlay.status_code == 200
    http_overlay_data = _v2(http_overlay.json())["data"]["agent_productization_governance"]
    _assert_overlay(http_overlay_data, min_applied=1, repo=repo, workspace_root=workspace_root)

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_feedback = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_governance_feedback", {"workspace_id": workspace_id, "codebase_id": codebase_id, "target_type": "portal_section", "target_id": "profile_onboarding", "action": "clarify"}))
    assert _v2(mcp_feedback)["data"]["agent_productization_governance"]["feedback"]["status"] == "recorded"
    mcp_rules = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_governance_rules_build", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    mcp_rule_id = _v2(mcp_rules)["data"]["agent_productization_governance"]["rules"][0]["rule_id"]
    mcp_review = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_governance_rule_review", {"workspace_id": workspace_id, "codebase_id": codebase_id, "rule_id": mcp_rule_id, "status": "approved"}))
    _assert_overlay(_v2(mcp_review)["data"]["agent_productization_governance"], min_applied=1, repo=repo, workspace_root=workspace_root)

    assert knowledge_main(["code", "agent-productization", "governance-feedback", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--target-type", "portal_section", "--target-id", "profile_onboarding", "--action", "clarify"]) == 0
    cli_feedback = json.loads(capsys.readouterr().out)
    assert _v2(cli_feedback)["data"]["agent_productization_governance"]["feedback"]["status"] == "recorded"
    assert knowledge_main(["code", "agent-productization", "governance-rules-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_rules = json.loads(capsys.readouterr().out)
    cli_rule_id = _v2(cli_rules)["data"]["agent_productization_governance"]["rules"][0]["rule_id"]
    assert knowledge_main(["code", "agent-productization", "governance-rule-review", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--rule-id", cli_rule_id, "--status", "approved"]) == 0
    capsys.readouterr()
    assert knowledge_main(["code", "agent-productization", "governance-overlay", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_overlay = json.loads(capsys.readouterr().out)
    _assert_overlay(_v2(cli_overlay)["data"]["agent_productization_governance"], min_applied=1, repo=repo, workspace_root=workspace_root)


def test_v50_governance_invalid_target_rejected(tmp_path, monkeypatch):
    client, _workspace_root, _workspace, workspace_id, codebase_id, _repo = _prepare(tmp_path, monkeypatch)
    response = client.post(
        f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/governance/feedback",
        json={"target_type": "portal_section", "target_id": "missing", "action": "clarify"},
    )
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "AGENT_PRODUCTIZATION_GOVERNANCE_TARGET_NOT_FOUND"
