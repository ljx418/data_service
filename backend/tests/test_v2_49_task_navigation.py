import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.agent_productization.persistence import suggested_tests_path, task_impact_path, task_reading_order_path
from data_service.code_assets.agent_productization.task_navigation import AgentTaskNavigationService
from data_service.code_assets.registry import CodebaseRegistry
from data_service.mcp_build_runtime import BuildRuntime
from data_service.mcp_dispatcher import MCPToolDispatcher
from data_service.mcp_workspace_runtime import WorkspaceRuntime


def _create_workspace(client: TestClient, name: str) -> str:
    response = client.post("/api/workspaces", json={"name": name})
    assert response.status_code == 200
    return response.json()["workspace_id"]


def _write_repo(repo: Path) -> None:
    files = {
        "README.md": "# Task Fixture\n\nThis repo validates task navigation.\n",
        "docs/api.md": "# API\n\nProfile onboarding API should stay evidence-backed.\n",
        "src/profile_service.py": "def build_profile():\n    return {'ok': True}\n",
        "src/navigation.py": "def reading_order():\n    return []\n",
        "tests/test_profile_service.py": "def test_build_profile():\n    assert True\n",
        "tests/test_navigation.py": "def test_reading_order():\n    assert True\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "task_fixture_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V49 Task Navigation")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="TaskFixture")["asset"]
    return client, workspace_root, workspace, workspace_id, asset.codebase_id, repo


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload: dict, repo: Path, workspace_root: Path) -> None:
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(repo) not in raw
    assert str(workspace_root) not in raw


def _assert_task_payload(payload: dict, *, repo: Path, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.46-52"
    assert payload["artifact_type"] == "task_navigation_and_impact"
    assert payload["summary"]["reading_item_count"] > 0
    assert payload["summary"]["impact_candidate_count"] > 0
    assert payload["summary"]["suggested_test_count"] > 0
    assert payload["summary"]["forbidden_claim_count"] == 0
    for item in payload["task_impact"]["impact_candidates"]:
        assert item["claim_type"] == "heuristic_candidate"
        assert item["claim_type"] not in {"runtime_call", "data_flow", "control_flow", "production_topology"}
        assert item.get("evidence_refs") or item.get("needs_review")
    for item in payload["suggested_tests"]["tests"]:
        assert item.get("evidence_refs") or item.get("needs_review")
    assert payload["artifact_refs"]
    _assert_no_absolute_path(payload, repo, workspace_root)


def test_v49_task_navigation_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    task = "Update profile onboarding API and suggested tests"
    service = AgentTaskNavigationService(workspace, workspace_id=workspace_id)
    payload = service.build_task_navigation(codebase_id, task=task)
    task_id = payload["task_id"]
    assert task_reading_order_path(workspace, codebase_id, task_id).exists()
    assert task_impact_path(workspace, codebase_id, task_id).exists()
    assert suggested_tests_path(workspace, codebase_id, task_id).exists()

    read_payload = service.read_task_navigation(codebase_id, task_id=task_id)
    assert read_payload["summary"]["forbidden_claim_count"] == 0

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/tasks", json={"task": task})
    assert http_build.status_code == 200
    http_build_data = _v2(http_build.json())["data"]["agent_productization_task_navigation"]
    _assert_task_payload(http_build_data, repo=repo, workspace_root=workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/tasks/{task_id}")
    assert http_read.status_code == 200
    http_read_data = _v2(http_read.json())["data"]["agent_productization_task_navigation"]
    assert http_read_data["summary"]["reading_item_count"] == http_build_data["summary"]["reading_item_count"]

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_task_navigation_build", {"workspace_id": workspace_id, "codebase_id": codebase_id, "task": task}))
    mcp_build_data = _v2(mcp_build)["data"]["agent_productization_task_navigation"]
    _assert_task_payload(mcp_build_data, repo=repo, workspace_root=workspace_root)
    task_id = mcp_build_data["task_id"]

    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_agent_productization_task_navigation_read", {"workspace_id": workspace_id, "codebase_id": codebase_id, "task_id": task_id}))
    mcp_read_data = _v2(mcp_read)["data"]["agent_productization_task_navigation"]
    assert mcp_read_data["summary"]["impact_candidate_count"] == mcp_build_data["summary"]["impact_candidate_count"]

    assert knowledge_main(["code", "agent-productization", "task-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--task", task]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    cli_build_data = _v2(cli_build)["data"]["agent_productization_task_navigation"]
    _assert_task_payload(cli_build_data, repo=repo, workspace_root=workspace_root)

    assert knowledge_main(["code", "agent-productization", "task", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id, "--task-id", cli_build_data["task_id"]]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    cli_read_data = _v2(cli_read)["data"]["agent_productization_task_navigation"]
    assert cli_read_data["summary"]["suggested_test_count"] == cli_build_data["summary"]["suggested_test_count"]


def test_v49_task_navigation_missing_returns_structured_error(tmp_path, monkeypatch):
    client, _workspace_root, _workspace, workspace_id, codebase_id, _repo = _prepare(tmp_path, monkeypatch)
    response = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/agent-productization/tasks/task_missing")
    assert response.status_code == 404
    assert response.json()["v2"]["error"]["code"] == "TASK_NAVIGATION_NOT_BUILT"

