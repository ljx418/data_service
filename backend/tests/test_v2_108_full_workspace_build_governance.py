from data_service.workspace_portfolio_final_evidence import WorkspacePortfolioFinalEvidenceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2108_full_build_queue_keeps_all_projects_and_records_bounded_execution(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioFinalEvidenceService(managed, workspace_id="v2108").build(root=root, max_code_projects=1)

    queue = payload["data"]["full_build_queue"]
    diagnosis = payload["data"]["project_build_diagnosis"]
    rows = queue["data"]["rows"]

    assert {row["display_name"] for row in rows} >= {"data_service", "技术分享"}
    assert queue["data"]["security_model"]["external_build_scripts_executed"] is False
    assert queue["data"]["security_model"]["workspace_mutation_allowed"] is False
    assert any(row["acceptance_status"] == "accepted" for row in rows if row["classification"] == "code_project")
    assert any(row["acceptance_status"] != "accepted" for row in rows if row["classification"] != "code_project")
    assert len(diagnosis["data"]["rows"]) == len(rows)
