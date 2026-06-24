import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import knowledge_main
from data_service.code_assets.human_agent_deepening.persistence import onboarding_report_path, restore_checklist_path, troubleshooting_path
from data_service.code_assets.human_agent_deepening.restore_ux import CANONICAL_RUNNER, FAILURE_CATEGORIES, RestoreUXService
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
        "README.md": "# Restore UX Fixture\n",
        "src/main.py": "def main():\n    return 'ok'\n",
        "tests/test_main.py": "def test_main():\n    assert True\n",
    }
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "restore_ux_repo"
    repo.mkdir()
    _write_repo(repo)
    workspace_root = tmp_path / "managed"
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(repo))
    client = TestClient(app)
    workspace_id = _create_workspace(client, "V58 Restore UX")
    workspace = workspace_root / workspace_id
    asset = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="RestoreUXFixture")["asset"]
    return client, workspace_root, workspace, workspace_id, asset.codebase_id


def _v2(payload: dict) -> dict:
    if "v2" in payload:
        return payload["v2"]
    return payload["data"]["v2"]


def _assert_no_absolute_path(payload, workspace_root: Path) -> None:
    raw = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    assert str(workspace_root) not in raw
    assert "Traceback (most recent call last)" not in raw


def _assert_restore_payload(payload: dict, workspace_root: Path) -> None:
    assert payload["schema_version"] == "v2.54-58"
    assert payload["artifact_type"] == "restore_ux"
    checklist = payload["restore_checklist"]["content"] if isinstance(payload["restore_checklist"], dict) else payload["restore_checklist"]
    troubleshooting = payload["troubleshooting"]["content"] if isinstance(payload["troubleshooting"], dict) else payload["troubleshooting"]
    report = payload["onboarding_report"]
    assert CANONICAL_RUNNER in checklist
    assert "TestClient" in checklist
    for category in FAILURE_CATEGORIES:
        assert category in troubleshooting
    assert report["path_redaction_passed"] is True
    assert report["summary"]["canonical_runner_present"] is True
    assert report["dependency_baseline"]["requirements_ref"] == "backend/requirements-test.txt"
    assert len(report["failure_diagnosis"]) == len(FAILURE_CATEGORIES)
    assert not any(item.get("status") == "accepted" for item in payload["unresolved"] if isinstance(item, dict))
    _assert_no_absolute_path(payload, workspace_root)


def test_v58_restore_ux_service_http_mcp_cli(tmp_path, monkeypatch, capsys):
    client, workspace_root, workspace, workspace_id, codebase_id = _prepare(tmp_path, monkeypatch)
    service = RestoreUXService(workspace, workspace_id=workspace_id)
    payload = service.build_restore_ux(codebase_id)
    assert restore_checklist_path(workspace, codebase_id).exists()
    assert troubleshooting_path(workspace, codebase_id).exists()
    assert onboarding_report_path(workspace, codebase_id).exists()
    _assert_restore_payload(payload, workspace_root)

    read_payload = service.read_restore_ux(codebase_id)
    assert read_payload["summary"]["failure_category_count"] == len(FAILURE_CATEGORIES)

    http_build = client.post(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/restore/build")
    assert http_build.status_code == 200
    _assert_restore_payload(_v2(http_build.json())["data"]["human_agent_deepening_restore"], workspace_root)

    http_read = client.get(f"/api/workspaces/{workspace_id}/codebases/{codebase_id}/human-agent-deepening/restore")
    assert http_read.status_code == 200
    assert _v2(http_read.json())["data"]["human_agent_deepening_restore"]["summary"]["canonical_runner_present"] is True

    runtime = WorkspaceRuntime(workspace_root / "_default", workspace_root=workspace_root)
    dispatcher = MCPToolDispatcher(default_workspace=workspace_root / "_default", workspace_runtime=runtime, build_runtime=BuildRuntime(runtime))
    mcp_build = asyncio.run(dispatcher.call_tool("knowledge_code_human_agent_deepening_restore_build", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    _assert_restore_payload(_v2(mcp_build)["data"]["human_agent_deepening_restore"], workspace_root)
    mcp_read = asyncio.run(dispatcher.call_tool("knowledge_code_human_agent_deepening_restore_read", {"workspace_id": workspace_id, "codebase_id": codebase_id}))
    assert _v2(mcp_read)["data"]["human_agent_deepening_restore"]["summary"]["acceptance_command_count"] >= 4

    assert knowledge_main(["code", "human-agent-deepening", "restore-build", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_build = json.loads(capsys.readouterr().out)
    _assert_restore_payload(_v2(cli_build)["data"]["human_agent_deepening_restore"], workspace_root)

    assert knowledge_main(["code", "human-agent-deepening", "restore", "--workspace-root", str(workspace_root), "--workspace-id", workspace_id, "--codebase-id", codebase_id]) == 0
    cli_read = json.loads(capsys.readouterr().out)
    assert _v2(cli_read)["data"]["human_agent_deepening_restore"]["schema_version"] == "v2.54-58"


def test_v58_restore_ux_missing_optional_sources_are_visible(tmp_path, monkeypatch):
    _client, workspace_root, workspace, workspace_id, codebase_id = _prepare(tmp_path, monkeypatch)
    payload = RestoreUXService(workspace, workspace_id=workspace_id).build_restore_ux(codebase_id)
    assert payload["onboarding_report"]["path_redaction_passed"] is True
    assert payload["onboarding_report"]["acceptance_commands"]
    _assert_no_absolute_path(payload, workspace_root)
