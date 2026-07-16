from data_service.__main__ import _build_knowledge_parser
from data_service.workspace_portfolio_final_acceptance import WorkspacePortfolioFinalAcceptanceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2115_final_gate_accepts_implementation_but_rejects_portfolio_false_green(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioFinalAcceptanceService(managed, workspace_id="v2115").build(root=root, max_code_projects=1)
    gate = payload["data"]["final_acceptance_gate"]

    assert gate["data"]["implementation_status"] == "accepted"
    assert gate["data"]["portfolio_final_status"] != "accepted"
    assert gate["data"]["high_risk_unresolved_count"] > 0
    assert "OCR sample qualification cannot be replaced by provider readiness or direct text extraction" in gate["data"]["false_green_rejections"]
    assert payload["status"] == gate["status"]


def test_v2115_default_cli_exposes_portfolio_final_acceptance_command():
    parser = _build_knowledge_parser()

    args = parser.parse_args(["portfolio-final-acceptance", "read", "--workspace-id", "demo"])

    assert args.command == "portfolio-final-acceptance"
    assert args.portfolio_final_acceptance_command == "read"
