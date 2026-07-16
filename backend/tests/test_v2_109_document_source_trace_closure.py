from data_service.workspace_portfolio_final_evidence import WorkspacePortfolioFinalEvidenceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2109_source_trace_and_ui_evidence_remain_non_accepted_without_real_chain(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioFinalEvidenceService(managed, workspace_id="v2109").build(root=root, max_code_projects=1)

    trace = payload["data"]["document_source_trace_closure"]
    ui = payload["data"]["ui_evidence_capture"]

    assert trace["data"]["rows"]
    assert any(row["source_trace_present"] is False for row in trace["data"]["rows"])
    assert any(row["acceptance_status"] != "accepted" for row in trace["data"]["rows"])
    assert ui["status"] == "structured_unavailable"
    assert ui["data"]["rows"][0]["screenshot_refs"] == []
