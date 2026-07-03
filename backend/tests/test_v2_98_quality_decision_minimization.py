from data_service.code_assets.automated_evidence_closure.quality_workbench import QualityDecisionWorkbench
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v298"):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# quality repo\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V298")["asset"].codebase_id
    return workspace, codebase_id


def test_v298_high_risk_quality_recommendation_requires_human_decision(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    service = QualityDecisionWorkbench(workspace, workspace_id="v298")
    payload = service.build_quality_workbench(
        codebase_id,
        {"recommendations": [{"recommendation_id": "source_trace_quality", "risk_level": "high", "recommended_decision": "approve", "evidence_refs": ["artifact://quality/source_trace"]}]},
    )
    assert payload["status"] == "needs_review"
    assert any(item["id"] == "source_trace_quality" for item in payload["unresolved"])

    accepted = service.build_quality_workbench(
        codebase_id,
        {
            "recommendations": [{"recommendation_id": "source_trace_quality", "risk_level": "high", "recommended_decision": "approve", "evidence_refs": ["artifact://quality/source_trace"]}],
            "human_decisions": [{"recommendation_id": "source_trace_quality", "decision": "approved", "evidence_refs": ["review://source_trace_quality"]}],
        },
    )
    assert accepted["status"] == "accepted"

