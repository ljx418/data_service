from data_service.__main__ import _build_knowledge_parser
from data_service.workspace_portfolio_real_evidence_acceptance import WorkspacePortfolioRealEvidenceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2120_final_gate_preserves_non_accepted_real_evidence_instead_of_false_green(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)
    monkeypatch.setattr("data_service.workspace_portfolio_real_evidence_acceptance.ocr_provider.shutil.which", lambda name: None)
    monkeypatch.setattr("data_service.workspace_portfolio_real_evidence_acceptance.ui_capture.shutil.which", lambda name: None)

    payload = WorkspacePortfolioRealEvidenceService(managed, workspace_id="v2120").build(root=root, max_code_projects=1)
    gate = payload["data"]["final_portfolio_acceptance_gate"]

    assert payload["implementation_delivery_status"] == "accepted"
    assert payload["portfolio_final_status"] != "accepted"
    assert gate["data"]["high_risk_unresolved_count"] > 0
    assert "safe build proposals do not imply external build acceptance" in gate["data"]["false_green_rejected"]
    assert gate["parent_run_ids"]


def test_v2120_default_cli_exposes_portfolio_real_evidence_command():
    parser = _build_knowledge_parser()

    args = parser.parse_args(["portfolio-real-evidence", "read", "--workspace-id", "demo"])

    assert args.command == "portfolio-real-evidence"
    assert args.portfolio_real_evidence_command == "read"
