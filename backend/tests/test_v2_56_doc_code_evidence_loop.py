import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.agent_productization.governance import AgentProductizationGovernanceService
from data_service.code_assets.agent_productization.human_portal import AgentHumanPortalService
from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService
from data_service.code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService
from data_service.code_assets.human_agent_deepening.evidence_loop import DocCodeEvidenceLoopService
from data_service.code_assets.human_agent_deepening.persistence import (
    decision_history_path,
    evidence_loop_path,
    evidence_loop_report_path,
    rule_effect_path,
)
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
        "README.md": "# Evidence Loop Fixture\n",
        "docs/V2_TARGET_ARCHITECTURE.md": "# Target Architecture\n\n- Governance overlay is read-time only.\n",
        "src/main.py": "def main():\n    return 'ok'\n",
        "tests/test_main.py": "def test_main():\n    assert True\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "evidence_loop_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V56 Evidence Loop")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="EvidenceLoopFixture")["asset"]
    AgentMCPProductizationService(workspace, workspace_id=workspace_id).build_mcp_usage(asset.codebase_id, all_tool_specs())
    AgentProfileOnboardingService(workspace, workspace_id=workspace_id).build_profile_onboarding(asset.codebase_id)
    AgentHumanPortalService(workspace, workspace_id=workspace_id).build_portal(asset.codebase_id)
    governance = AgentProductizationGovernanceService(workspace, workspace_id=workspace_id)
    governance.record_feedback(asset.codebase_id, target_type="portal_section", target_id="profile_onboarding", action="clarify", rule_type="read_time_overlay", severity="low", reason="approved finding", suggested_value="approved")
    governance.record_feedback(asset.codebase_id, target_type="portal_section", target_id="profile_onboarding", action="clarify", rule_type="read_time_overlay", severity="medium", reason="revoked finding", suggested_value="revoked")
    governance.record_feedback(asset.codebase_id, target_type="portal_section", target_id="profile_onboarding", action="clarify", rule_type="missing_evidence", severity="high", reason="unsupported finding", suggested_value="unsupported")
    rules = governance.build_rules(asset.codebase_id)["rules"]
    for rule in rules:
        if rule["suggested_value"] == "approved":
            governance.review_rule(asset.codebase_id, rule["rule_id"], status="approved", reviewer="tester", note="approve")
        if rule["suggested_value"] == "revoked":
            governance.review_rule(asset.codebase_id, rule["rule_id"], status="revoked", reviewer="tester", note="revoke")
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload, repo: Path, workspace_root: Path) -> None:
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw
    assert "Traceback (most recent call last)" not in raw


def _assert_evidence_loop_payload(payload: dict, *, repo: Path, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.54-58"
    assert payload["artifact_type"] == "doc_code_evidence_loop"
    loop = payload["evidence_loop"]
    statuses = {item["status"] for item in loop["findings"]}
    assert {"supported", "contradicted", "unsupported"} <= statuses
    assert payload["rule_effect"]["hash_unchanged"] is True
    assert payload["rule_effect"]["summary"]["approved_rule_count"] == 1
    assert payload["rule_effect"]["summary"]["revoked_rule_count"] == 1
    assert any(item["action"] == "approve" for item in payload["decision_history"])
    assert any(item["action"] == "revoke" for item in payload["decision_history"])
    assert not any(item.get("status") == "accepted" for item in payload["unresolved"] if isinstance(item, dict))
    assert not any(item.get("status") == "structured_blocker" for item in payload["unresolved"] if isinstance(item, dict))
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v56_doc_code_evidence_loop_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    service = DocCodeEvidenceLoopService(workspace, workspace_id=workspace_id)
    payload = service.build_evidence_loop(codebase_id)
    assert evidence_loop_path(workspace, codebase_id).exists()
    assert decision_history_path(workspace, codebase_id).exists()
    assert rule_effect_path(workspace, codebase_id).exists()
    assert evidence_loop_report_path(workspace, codebase_id).exists()
    _assert_evidence_loop_payload(payload, repo=repo, workspace_root=workspace_root)

    read_payload = service.read_evidence_loop(codebase_id)
    assert read_payload["summary"]["hash_unchanged"] is True

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/evidence-loop/build")
    assert http_build.status_code == 200
    _assert_evidence_loop_payload(_v2(http_build.json())["data"]["human_agent_deepening_evidence_loop"], repo=repo, workspace_root=workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/evidence-loop")
    assert http_read.status_code == 200
    assert _v2(http_read.json())["data"]["human_agent_deepening_evidence_loop"]["summary"]["hash_unchanged"] is True

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_human_agent_deepening_evidence_loop_build", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_evidence_loop_payload(_v2(mcp_build)["data"]["human_agent_deepening_evidence_loop"], repo=repo, workspace_root=workspace_root)
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_human_agent_deepening_evidence_loop_read", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_read)["data"]["human_agent_deepening_evidence_loop"]["summary"]["decision_count"] >= 3

    assert knowledge_main(["code", "human-agent-deepening", "evidence-loop-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    _assert_evidence_loop_payload(_v2(cli_build)["data"]["human_agent_deepening_evidence_loop"], repo=repo, workspace_root=workspace_root)

    assert knowledge_main(["code", "human-agent-deepening", "evidence-loop", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    assert _v2(cli_read)["data"]["human_agent_deepening_evidence_loop"]["schema_version"] == "v2.54-58"


def test_v56_doc_code_evidence_loop_missing_inputs_are_unresolved(tmp_path, monkeypatch):
    repo = tmp_path / "evidence_loop_partial_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed_partial"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V56 Partial")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="PartialEvidenceLoop")["asset"]
    payload = DocCodeEvidenceLoopService(workspace, workspace_id=workspace_id).build_evidence_loop(asset.codebase_id)
    assert payload["warnings"]
    assert payload["unresolved"]
    assert payload["evidence_loop"]["findings"][0]["status"] == "needs_review"
    assert not any(item.get("status") == "accepted" for item in payload["unresolved"] if isinstance(item, dict))
