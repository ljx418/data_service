from data_service.workspace_portfolio_real_evidence_acceptance import WorkspacePortfolioRealEvidenceService

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2117_source_trace_rows_require_same_source_identity(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioRealEvidenceService(managed, workspace_id="v2117").build(root=root, max_code_projects=1)
    batch = payload["data"]["source_trace_batch_results"]
    index = payload["data"]["source_trace_evidence_index"]

    assert batch["artifact_status"] == "accepted"
    assert index["artifact_status"] == "accepted"
    row = index["data"]["rows"][0]
    assert row["source_id"] in row["query_result_source_ids"]
    assert row["trace_source_id"] == row["source_id"]
    assert row["same_source_assertion"] == "matched"
    assert row["trace_evidence_refs"]
