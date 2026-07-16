from data_service.workspace_portfolio_final_evidence import WorkspacePortfolioFinalEvidenceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2106_coverage_and_architecture_closure_use_real_baseline(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioFinalEvidenceService(managed, workspace_id="v2106").build(root=root, max_code_projects=1)

    coverage = payload["data"]["coverage_state_closure"]
    architecture = payload["data"]["architecture_state_closure"]
    baseline = payload["data"]["baseline_evidence_manifest"]

    assert baseline["data"]["rows"]
    assert all(row["hash"] for row in baseline["data"]["rows"] if row["stable_id"].startswith("baseline:"))
    assert coverage["data"]["rows"]
    assert any(row["acceptance_status"] != "accepted" for row in coverage["data"]["rows"])
    assert any(row["entity"] == "workspace_portfolio_final_evidence.service.WorkspacePortfolioFinalEvidenceService" for row in architecture["data"]["rows"])
    assert architecture["data"]["summary"]["accepted_count"] >= 1
