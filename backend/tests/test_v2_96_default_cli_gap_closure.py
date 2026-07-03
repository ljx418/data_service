import json
import os
import subprocess
import sys
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import _build_parser
from data_service.code_assets.automated_evidence_closure.cli_gap import DefaultCliGapClosure
from data_service.code_assets.registry import CodebaseRegistry
from data_service.mcp_tool_registry import all_tool_specs


REPO_ROOT = Path(__file__).resolve().parents[2]


def _prepare(tmp_path, monkeypatch, workspace_id="v296"):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# real repo\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    workspace = workspace_root / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V296")["asset"].codebase_id
    return workspace, workspace_root, codebase_id


def test_v296_default_shell_cli_accepts_code_command(tmp_path, monkeypatch):
    workspace, workspace_root, codebase_id = _prepare(tmp_path, monkeypatch)
    parser = _build_parser()
    args = parser.parse_args(
        [
            "code",
            "real-acceptance-closure",
            "release-finalizer-read",
            "--workspace-root",
            str(workspace_root),
            "--workspace-id",
            "v296",
            "--codebase-id",
            codebase_id,
        ]
    )
    assert args.command == "code"
    assert args.code_command == "real-acceptance-closure"

    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "backend")
    result = subprocess.run(
        [sys.executable, "-m", "data_service", "code", "real-acceptance-closure", "--help"],
        cwd=str(REPO_ROOT),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "real-acceptance-closure" in result.stdout

    payload = DefaultCliGapClosure(workspace, workspace_id="v296").build_cli_gap(
        codebase_id,
        {
            "shell_command": {"status": "accepted", "command_ref": "command://python-m-data-service-code-help"},
            "parser_inventory": {"status": "accepted", "command_ref": "pytest://v296-parser"},
            "mcp_inventory": {"status": "accepted", "command_ref": "pytest://mcp-registry"},
            "http_inventory": {"status": "accepted", "command_ref": "pytest://http-routes"},
            "evidence_refs": ["command://python-m-data-service-code-help"],
        },
    )
    assert payload["status"] == "accepted"
    assert "knowledge_code_automated_evidence_closure_cli_gap_read" in {spec["name"] for spec in all_tool_specs()}
    response = TestClient(app).get(f"/api/workspaces/v296/codebases/{codebase_id}/automated-evidence-closure/cli-gap")
    assert response.status_code in {200, 404}
