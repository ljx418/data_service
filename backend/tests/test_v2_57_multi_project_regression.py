import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.agent_productization.governance import AgentProductizationGovernanceService
from data_service.code_assets.agent_productization.human_portal import AgentHumanPortalService
from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService
from data_service.code_assets.agent_productization.playbooks import AgentProductizationPlaybookService
from data_service.code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService
from data_service.code_assets.human_agent_deepening.evidence_loop import DocCodeEvidenceLoopService
from data_service.code_assets.human_agent_deepening.human_portal import HumanPortalDeepeningService
from data_service.code_assets.human_agent_deepening.persistence import artifact_diff_path, expanded_matrix_path, failure_diagnosis_path, regression_report_path
from data_service.code_assets.human_agent_deepening.regression import FAILURE_CATEGORIES, MultiProjectRegressionService
from data_service.code_assets.human_agent_deepening.task_workflow import AgentTaskWorkflowService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_tool_registry import all_tool_specs
from data_service.mcp_workspace_runtime import WorkspaceRuntime


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _write_repo(repo: Path, name: str) -> None:
    files = {
        "README.md": f"# {name}\n",
        "docs/V2_TARGET_ARCHITECTURE.md": f"# Target Architecture\n\n- {name} regression fixture.\n",
        "src/main.py": "def main():\n    return 'ok'\n",
        "tests/test_main.py": "def test_main():\n    assert True\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _build_project_artifacts(workspace: Path, workspace_id: str, repo: Path, name: str) -> str:
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name=name)["asset"]
    codebase_id = asset.codebase_id
    AgentMCPProductizationService(workspace, workspace_id=workspace_id).build_mcp_usage(codebase_id, all_tool_specs())
    AgentProfileOnboardingService(workspace, workspace_id=workspace_id).build_profile_onboarding(codebase_id)
    AgentHumanPortalService(workspace, workspace_id=workspace_id).build_portal(codebase_id)
    AgentProductizationPlaybookService(workspace, workspace_id=workspace_id).build_playbooks(codebase_id, role="coding_agent")
    HumanPortalDeepeningService(workspace, workspace_id=workspace_id).build_portal(codebase_id)
    AgentTaskWorkflowService(workspace, workspace_id=workspace_id).build_task_workflow(codebase_id, task="Implement regression expansion tests")
    governance = AgentProductizationGovernanceService(workspace, workspace_id=workspace_id)
    governance.record_feedback(codebase_id, target_type="portal_section", target_id="profile_onboarding", action="clarify", suggested_value="approved")
    rule = governance.build_rules(codebase_id)["rules"][0]
    governance.review_rule(codebase_id, rule["rule_id"], status="approved", reviewer="tester")
    DocCodeEvidenceLoopService(workspace, workspace_id=workspace_id).build_evidence_loop(codebase_id)
    return codebase_id


def _prepare(tmp_path, monkeypatch):
    workspace_root = tmp_path / "managed"
    repos_root = tmp_path / "repos"
    repos_root.mkdir()
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repos_root))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V57 Regression")
    workspace = workspace_root / workspace_id
    projects = []
    current_codebase_id = ""
    for name in ["data_service", "HarnessOS", "codexPat"]:
        repo = repos_root / name
        repo.mkdir()
        _write_repo(repo, name)
        codebase_id = _build_project_artifacts(workspace, workspace_id, repo, name)
        if name == "data_service":
            current_codebase_id = codebase_id
        projects.append({"name": name, "path": str(repo)})
    projects.append({"name": "Navia", "path": str(repos_root / "missing_navia")})
    return client, workspace_root, workspace, workspace_id, current_codebase_id, projects


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload, workspace_root: Path) -> None:
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    assert str(workspace_root) not in raw
    assert "Traceback (most recent call last)" not in raw


def _assert_regression_payload(payload: dict, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.54-58"
    assert payload["artifact_type"] == "multi_project_regression"
    matrix = payload["expanded_matrix"]
    assert matrix["projects"] == ["data_service", "HarnessOS", "Navia", "codexPat"]
    results = {row["project"]: row for row in matrix["results"]}
    assert results["data_service"]["status"] == "accepted"
    assert results["HarnessOS"]["status"] == "accepted"
    assert results["codexPat"]["status"] == "accepted"
    assert results["Navia"]["status"] == "structured_unavailable"
    assert matrix["summary"]["accepted_count"] == 3
    assert matrix["summary"]["structured_unavailable_count"] == 1
    assert results["Navia"]["status"] != "accepted"
    assert payload["artifact_diff"]["false_green_risk"]["semantic_equivalence_claimed"] is False
    for item in payload["failure_diagnosis"]["failures"]:
        assert item["category"] in FAILURE_CATEGORIES
    assert not any(item.get("status") == "accepted" for item in payload["unresolved"] if isinstance(item, dict))
    _assert_no_absolute_path(payload, workspace_root)


def test_v57_multi_project_regression_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, projects = _prepare(tmp_path, monkeypatch)
    service = MultiProjectRegressionService(workspace, workspace_id=workspace_id)
    payload = service.build_regression(codebase_id, projects=projects)
    assert expanded_matrix_path(workspace, codebase_id).exists()
    assert artifact_diff_path(workspace, codebase_id).exists()
    assert failure_diagnosis_path(workspace, codebase_id).exists()
    assert regression_report_path(workspace, codebase_id).exists()
    _assert_regression_payload(payload, workspace_root)

    read_payload = service.read_regression(codebase_id)
    assert read_payload["summary"]["accepted_count"] == 3

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/regression/build", json={"projects": projects})
    assert http_build.status_code == 200
    _assert_regression_payload(_v2(http_build.json())["data"]["human_agent_deepening_regression"], workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/regression")
    assert http_read.status_code == 200
    assert _v2(http_read.json())["data"]["human_agent_deepening_regression"]["summary"]["structured_unavailable_count"] == 1

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_human_agent_deepening_regression_build", {"workspace_id": workspace_id, "codebase_id": codebase_id, "projects": projects}))
    _assert_regression_payload(_v2(mcp_build)["data"]["human_agent_deepening_regression"], workspace_root)
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_human_agent_deepening_regression_read", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_read)["data"]["human_agent_deepening_regression"]["summary"]["accepted_count"] == 3

    cli_args = ["code", "human-agent-deepening", "regression-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]
    for item in projects:
        cli_args.extend(["--project", f"{item['name']}={item['path']}"])
    assert knowledge_main(cli_args) == 0
    cli_build = json.loads(capsys.readouterr().out)
    _assert_regression_payload(_v2(cli_build)["data"]["human_agent_deepening_regression"], workspace_root)

    assert knowledge_main(["code", "human-agent-deepening", "regression", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    assert _v2(cli_read)["data"]["human_agent_deepening_regression"]["schema_version"] == "v2.54-58"


def test_v57_multi_project_regression_rejects_mock_only_as_accepted(tmp_path, monkeypatch):
    _client, workspace_root, workspace, workspace_id, codebase_id, projects = _prepare(tmp_path, monkeypatch)
    projects = [dict(item) for item in projects]
    projects[0]["evidence_mode"] = "mock"
    payload = MultiProjectRegressionService(workspace, workspace_id=workspace_id).build_regression(codebase_id, projects=projects)
    data_service = next(row for row in payload["expanded_matrix"]["results"] if row["project"] == "data_service")
    assert data_service["status"] == "needs_review"
    assert data_service["failure_category"] == "needs_review"
    assert payload["summary"]["accepted_count"] == 2
    _assert_no_absolute_path(payload, workspace_root)
