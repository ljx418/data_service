from data_service.__main__ import _build_knowledge_parser
from data_service.workspace_portfolio_final_evidence import WorkspacePortfolioFinalEvidenceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2110_final_gate_reports_implementation_done_but_rejects_final_false_green(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioFinalEvidenceService(managed, workspace_id="v2110").build(root=root, max_code_projects=1)
    gate = payload["data"]["final_release_gate"]

    assert gate["data"]["implementation_status"] == "accepted"
    assert gate["data"]["portfolio_final_status"] != "accepted"
    assert gate["unresolved"]
    assert "missing UI screenshot/headless evidence remains structured_unavailable" in gate["data"]["false_green_rejections"]
    assert payload["status"] == gate["status"]


def test_v2110_default_cli_exposes_portfolio_final_evidence_command():
    parser = _build_knowledge_parser()

    args = parser.parse_args(["portfolio-final-evidence", "read", "--workspace-id", "demo"])

    assert args.command == "portfolio-final-evidence"
    assert args.portfolio_final_evidence_command == "read"
