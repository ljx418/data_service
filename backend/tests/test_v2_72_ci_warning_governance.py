from data_service.code_assets.agent_memory_release.ci_warning_governance import CIWarningGovernanceService
from data_service.code_assets.agent_memory_release.shared import FAILURE_CATEGORIES
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# V272\n", encoding="utf-8")
    workspace = tmp_path / "managed" / "v272"
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id="v272").import_codebase(path=str(repo), name="V272")["asset"].codebase_id
    return workspace, codebase_id


def test_v272_warning_over_budget_is_not_accepted(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    payload = CIWarningGovernanceService(workspace, workspace_id="v272").build_ci_warning_governance(
        codebase_id,
        command_results={"observed_warning_count": 500, "warning_budget": 100, "failure_category": "dependency_drift"},
    )

    assert payload["warning_budget"]["status"] == "needs_review"
    assert payload["failure_diagnosis"]["items"][0]["failure_category"] in FAILURE_CATEGORIES
    assert payload["unresolved"]


def test_v272_default_warning_budget_is_accepted(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    payload = CIWarningGovernanceService(workspace, workspace_id="v272").build_ci_warning_governance(codebase_id)

    assert payload["warning_budget"]["status"] == "accepted"
    assert payload["summary"]["observed_warning_count"] <= payload["summary"]["warning_budget"]

