from data_service.code_assets.real_acceptance_closure.quality_decision import HumanQualityDecisionRecorder
from data_service.code_assets.real_document_full_corpus_release.persistence import write_quality_review
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v293"):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# real repo\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V293")["asset"].codebase_id
    return workspace, codebase_id


def test_v293_quality_decision_requires_upstream_and_human_evidence(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)

    payload = HumanQualityDecisionRecorder(workspace, workspace_id="v293").build_quality_decision(codebase_id)

    assert payload["status"] == "needs_review"
    assert any(item["id"] == "quality_upstream" for item in payload["unresolved"])


def test_v293_quality_decision_accepts_human_reviewed_recommendations(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    write_quality_review(
        workspace,
        codebase_id,
        {
            "status": "needs_review",
            "artifact_type": "human_quality_review",
            "decisions": [{"recommendation_id": "source_trace_quality", "finding": "human review required"}],
        },
        "",
        "# quality report\n",
    )

    payload = HumanQualityDecisionRecorder(workspace, workspace_id="v293").build_quality_decision(
        codebase_id,
        {"reviewer": "maintainer", "decisions": [{"decision_id": "source_trace_quality", "decision": "approved", "evidence_refs": ["review://source_trace_quality"]}]},
    )

    assert payload["status"] == "accepted"
    closure = payload["data"]["rule_effect_closure"]
    assert closure["upstream_hashes"][0]["hash_unchanged"] is True
    assert closure["decisions"][0]["decision"] == "approved"
