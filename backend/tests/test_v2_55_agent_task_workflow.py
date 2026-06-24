import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.agent_productization.human_portal import AgentHumanPortalService
from data_service.code_assets.agent_productization.mcp_usage import AgentMCPProductizationService
from data_service.code_assets.agent_productization.playbooks import AgentProductizationPlaybookService
from data_service.code_assets.agent_productization.profile_onboarding import AgentProfileOnboardingService
from data_service.code_assets.human_agent_deepening.human_portal import HumanPortalDeepeningService
from data_service.code_assets.human_agent_deepening.persistence import (
    stop_conditions_path,
    task_workflow_markdown_path,
    task_workflow_suggested_tests_path,
    workflow_bundle_path,
)
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


def _write_repo(repo: Path) -> None:
    files = {
        "README.md": "# Agent Task Workflow Fixture\n\nPortal and task workflow fixture.\n",
        "docs/V2_TARGET_ARCHITECTURE.md": "# Target Architecture\n\n- Task workflow reads persisted artifacts.\n",
        "docs/V2_SERVICE_PRD.md": "# PRD\n\n- Agents need reading order, impact candidates, tests, and stop conditions.\n",
        "backend/data_service/code_assets/human_agent_deepening/task_workflow.py": "def build_task_workflow():\n    return 'workflow'\n",
        "backend/data_service/code_assets/human_agent_deepening/human_portal.py": "def build_portal():\n    return 'portal'\n",
        "backend/tests/test_v2_55_agent_task_workflow.py": "def test_task_workflow():\n    assert True\n",
        "backend/tests/test_v2_54_human_portal_deepening.py": "def test_portal():\n    assert True\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch, *, with_upstream: bool = True):
    repo = tmp_path / "task_workflow_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V55 Agent Task Workflow")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="TaskWorkflowFixture")["asset"]
    if with_upstream:
        AgentMCPProductizationService(workspace, workspace_id=workspace_id).build_mcp_usage(asset.codebase_id, all_tool_specs())
        AgentProfileOnboardingService(workspace, workspace_id=workspace_id).build_profile_onboarding(asset.codebase_id)
        AgentHumanPortalService(workspace, workspace_id=workspace_id).build_portal(asset.codebase_id)
        AgentProductizationPlaybookService(workspace, workspace_id=workspace_id).build_playbooks(asset.codebase_id, role="coding_agent")
        HumanPortalDeepeningService(workspace, workspace_id=workspace_id).build_portal(asset.codebase_id)
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


def _assert_workflow_payload(payload: dict, *, repo: Path, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.54-58"
    assert payload["artifact_type"] == "agent_task_workflow"
    workflow = payload["workflow_bundle"]
    assert workflow["task_summary"]["task"]
    assert workflow["reading_order"]
    assert workflow["impact_candidates"]
    assert workflow["stop_conditions"]
    assert workflow["recommendations"]
    forbidden = {"runtime_call", "data_flow", "control_flow", "production_topology"}
    for item in workflow["impact_candidates"]:
        candidate_path = item.get("path") or (item.get("debug_paths") or {}).get("path")
        assert candidate_path, item
        assert item["candidate_kind"] == "static_candidate"
        assert item["claim_type"] not in forbidden
        assert not str(candidate_path).startswith(".tmp/")
    for item in workflow["recommendations"]:
        assert item.get("evidence_refs") or item.get("needs_review")
    for item in payload["suggested_tests"]["tests"]:
        assert item["status"] in {"recommended", "needs_review", "structured_unavailable"}
        if not item["evidence_refs"]:
            assert item["status"] == "needs_review"
    assert any(item["id"] == "static_analysis_overclaim" for item in payload["stop_conditions"]["conditions"])
    assert not any(item.get("status") == "structured_blocker" for item in payload["unresolved"] if isinstance(item, dict))
    assert payload["artifact_refs"]
    assert "runtime topology" not in json.dumps(payload, ensure_ascii=False).lower()
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v55_agent_task_workflow_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    task = "Implement task workflow portal tests"
    service = AgentTaskWorkflowService(workspace, workspace_id=workspace_id)
    payload = service.build_task_workflow(codebase_id, task=task)
    task_id = payload["task_id"]
    assert workflow_bundle_path(workspace, codebase_id, task_id).exists()
    assert stop_conditions_path(workspace, codebase_id, task_id).exists()
    assert task_workflow_suggested_tests_path(workspace, codebase_id, task_id).exists()
    assert task_workflow_markdown_path(workspace, codebase_id, task_id).exists()
    _assert_workflow_payload(payload, repo=repo, workspace_root=workspace_root)

    read_payload = service.read_task_workflow(codebase_id, task_id=task_id)
    assert read_payload["summary"]["suggested_test_count"] >= 1

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/task-workflow/build", json={"task": task})
    assert http_build.status_code == 200
    http_build_data = _v2(http_build.json())["data"]["human_agent_deepening_task_workflow"]
    _assert_workflow_payload(http_build_data, repo=repo, workspace_root=workspace_root)
    http_task_id = http_build_data["task_id"]

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/task-workflow/{http_task_id}")
    assert http_read.status_code == 200
    assert _v2(http_read.json())["data"]["human_agent_deepening_task_workflow"]["task_id"] == http_task_id

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_human_agent_deepening_task_workflow_build", {"workspace_id": workspace_id, "codebase_id": codebase_id, "task": task}))
    mcp_build_data = _v2(mcp_build)["data"]["human_agent_deepening_task_workflow"]
    _assert_workflow_payload(mcp_build_data, repo=repo, workspace_root=workspace_root)

    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_human_agent_deepening_task_workflow_read", {"workspace_id": workspace_id, "codebase_id": codebase_id, "task_id": mcp_build_data["task_id"]}))
    assert _v2(mcp_read)["data"]["human_agent_deepening_task_workflow"]["summary"]["impact_candidate_count"] >= 1

    assert knowledge_main(["code", "human-agent-deepening", "task-workflow-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--task", task]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    cli_build_data = _v2(cli_build)["data"]["human_agent_deepening_task_workflow"]
    _assert_workflow_payload(cli_build_data, repo=repo, workspace_root=workspace_root)

    assert knowledge_main(["code", "human-agent-deepening", "task-workflow", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--task-id", cli_build_data["task_id"]]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    assert _v2(cli_read)["data"]["human_agent_deepening_task_workflow"]["schema_version"] == "v2.54-58"


def test_v55_agent_task_workflow_missing_inputs_and_budget_are_visible(tmp_path, monkeypatch):
    _client, workspace_root, workspace, workspace_id, codebase_id, repo = _prepare(tmp_path, monkeypatch, with_upstream=False)
    payload = AgentTaskWorkflowService(workspace, workspace_id=workspace_id).build_task_workflow(
        codebase_id,
        task="Change task workflow behavior",
        max_tokens=140,
    )
    _assert_workflow_payload(payload, repo=repo, workspace_root=workspace_root)
    assert payload["workflow_bundle"]["omitted_items"]
    assert payload["warnings"]
    assert payload["unresolved"]
    assert not any(item.get("status") == "accepted" for item in payload["unresolved"] if isinstance(item, dict))
