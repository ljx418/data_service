import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.agent_productization.closure import AgentProductizationClosureService
from data_service.code_assets.agent_productization.governance import AgentProductizationGovernanceService
from data_service.code_assets.agent_productization.human_portal import AgentHumanPortalService
from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService
from data_service.code_assets.agent_productization.persistence import (
    closure_audit_report_path,
    public_contract_parity_path,
    real_repo_matrix_path,
    redaction_audit_path,
)
from data_service.code_assets.agent_productization.playbooks import AgentProductizationPlaybookService
from data_service.code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService
from data_service.code_assets.agent_productization.task_navigation import AgentTaskNavigationService
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
        "README.md": "# Closure Fixture\n\nA project used for productization closure.\n",
        "docs/V2_TARGET_ARCHITECTURE.md": "# Target Architecture\n\n- The portal and playbooks support maintainers and Agents.\n",
        "src/main.py": "def main():\n    return 'ok'\n",
        "tests/test_main.py": "def test_main():\n    assert True\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "closure_fixture_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V52 Closure")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="ClosureFixture")["asset"]
    AgentMCPProductizationService(workspace, workspace_id=workspace_id).build_mcp_usage(asset.codebase_id, all_tool_specs())
    AgentProfileOnboardingService(workspace, workspace_id=workspace_id).build_profile_onboarding(asset.codebase_id)
    AgentHumanPortalService(workspace, workspace_id=workspace_id).build_portal(asset.codebase_id)
    AgentTaskNavigationService(workspace, workspace_id=workspace_id).build_task_navigation(asset.codebase_id, task="review portal playbook tests")
    governance = AgentProductizationGovernanceService(workspace, workspace_id=workspace_id)
    feedback = governance.record_feedback(asset.codebase_id, target_type="portal_section", target_id="profile_onboarding", action="clarify")
    rules = governance.build_rules(asset.codebase_id)
    governance.review_rule(asset.codebase_id, rules["rules"][0]["rule_id"], status="approved", reviewer="tester")
    AgentProductizationPlaybookService(workspace, workspace_id=workspace_id).build_playbooks(asset.codebase_id)
    assert feedback["feedback"]["status"] == "recorded"
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload: dict, repo: Path, workspace_root: Path) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw


def _assert_closure(payload: dict, repo: Path, workspace_root: Path) -> None:
    matrix = payload["real_repo_matrix"]
    assert matrix["project_result"] == "accepted"
    assert matrix["structured_blocker_count"] == 0
    assert all(row["status"] == "accepted" for row in matrix["phase_rows"])
    assert all(row["evidence_refs"] for row in matrix["phase_rows"])
    assert payload["public_contract_parity"]["status"] == "accepted"
    assert payload["redaction_audit"]["status"] == "accepted"
    assert "no fatal or major finding" in payload["closure_audit_report"]["content"]
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v52_closure_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    service = AgentProductizationClosureService(workspace, workspace_id=workspace_id)
    payload = service.build_closure(codebase_id)
    assert real_repo_matrix_path(workspace, codebase_id).exists()
    assert public_contract_parity_path(workspace, codebase_id).exists()
    assert redaction_audit_path(workspace, codebase_id).exists()
    assert closure_audit_report_path(workspace, codebase_id).exists()
    _assert_closure(payload, repo, workspace_root)

    read_payload = service.read_closure(codebase_id)
    _assert_closure(read_payload, repo, workspace_root)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/closure/build")
    assert http_build.status_code == 200
    http_build_data = _v2(http_build.json())["data"]["agent_productization_closure"]
    _assert_closure(http_build_data, repo, workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/closure")
    assert http_read.status_code == 200
    http_read_data = _v2(http_read.json())["data"]["agent_productization_closure"]
    assert http_read_data["real_repo_matrix"]["accepted_row_count"] == http_build_data["real_repo_matrix"]["accepted_row_count"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_closure_build", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_closure(_v2(mcp_build)["data"]["agent_productization_closure"], repo, workspace_root)
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_closure_read", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_read)["data"]["agent_productization_closure"]["real_repo_matrix"]["project_result"] == "accepted"

    assert knowledge_main(["code", "agent-productization", "closure-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    _assert_closure(_v2(cli_build)["data"]["agent_productization_closure"], repo, workspace_root)
    assert knowledge_main(["code", "agent-productization", "closure", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    assert _v2(cli_read)["data"]["agent_productization_closure"]["public_contract_parity"]["status"] == "accepted"


def test_v52_closure_reports_blocker_when_phase_missing(tmp_path, monkeypatch):
    repo = tmp_path / "partial_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed_partial"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V52 Partial")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="PartialClosure")["asset"]
    AgentMCPProductizationService(workspace, workspace_id=workspace_id).build_mcp_usage(asset.codebase_id, all_tool_specs())
    payload = AgentProductizationClosureService(workspace, workspace_id=workspace_id).build_closure(asset.codebase_id)
    assert payload["real_repo_matrix"]["project_result"] == "accepted_with_blockers"
    assert payload["real_repo_matrix"]["structured_blocker_count"] > 0
    assert not any(row["status"] == "accepted" and not row["evidence_refs"] for row in payload["real_repo_matrix"]["phase_rows"])
