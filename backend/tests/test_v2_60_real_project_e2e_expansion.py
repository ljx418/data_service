import json
from pathlib import Path

from data_service.code_assets.registry import CodebaseRegistry
from data_service.code_assets.stabilization_e2e_portal.e2e_expansion import FAILURE_CATEGORIES, RealProjectE2EExpansionService


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V260\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v260"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v260").import_codebase(path=str(repo), name="V260")["asset"].codebase_id
    return tmp_path, workspace, codebase_id


def test_v260_e2e_expansion_rejects_unavailable_and_mock_only(tmp_path, monkeypatch):
    root, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    available = root / "codexPat"
    available.mkdir()
    payload = RealProjectE2EExpansionService(workspace, workspace_id="v260").build_e2e(
        codebase_id,
        projects=[
            {"name": "codexPat", "path": str(available)},
            {"name": "HarnessOS", "evidence_mode": "mock_only"},
            {"name": "Navia", "path": str(root / "missing")},
        ],
    )
    rows = {item["name"]: item for item in payload["project_e2e_matrix"]["projects"]}
    assert rows["data_service"]["status"] == "accepted"
    assert rows["codexPat"]["status"] == "accepted"
    assert rows["HarnessOS"]["status"] == "needs_review"
    assert rows["Navia"]["status"] == "structured_unavailable"
    assert payload["summary"]["mock_only_accepted_count"] == 0
    assert payload["summary"]["unavailable_accepted_count"] == 0
    assert set(payload["project_failure_diagnosis"]["categories"]) == set(FAILURE_CATEGORIES)
    raw = json.dumps(payload, ensure_ascii=False)
    assert str(workspace) not in raw


def test_v260_e2e_readback(tmp_path, monkeypatch):
    _root, workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = RealProjectE2EExpansionService(workspace, workspace_id="v260")
    service.build_e2e(codebase_id)
    read_back = service.read_e2e(codebase_id)
    assert read_back["summary"]["project_count"] == 4
