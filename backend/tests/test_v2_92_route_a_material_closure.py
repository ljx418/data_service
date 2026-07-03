from data_service.code_assets.real_acceptance_closure.route_a_material import RouteAMaterialIntakeReview
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v292"):
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (docs / "route_a.md").write_text("# 用户代表性资料\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V292")["asset"].codebase_id
    return workspace, codebase_id


def test_v292_route_a_missing_materials_remain_needs_review(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)

    payload = RouteAMaterialIntakeReview(workspace, workspace_id="v292").build_route_a_closure(codebase_id)

    assert payload["status"] == "needs_review"
    assert any(item["id"] == "route_a_materials" for item in payload["unresolved"])


def test_v292_route_a_accepts_only_with_material_redaction_and_manual_evidence(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    state = {
        "materials": [{"material_id": "route_a_doc", "source_type": "markdown", "source_ref": "repo://docs/route_a.md", "redaction_status": "accepted"}],
        "redaction": {"status": "accepted", "policy_ref": "manual://redaction-policy"},
        "manual_review": {"reviewer": "maintainer", "decision": "accepted"},
        "evidence_refs": ["repo://docs/route_a.md", "manual://route-a-review", "screenshot://route-a"],
    }

    payload = RouteAMaterialIntakeReview(workspace, workspace_id="v292").build_route_a_closure(codebase_id, state)

    assert payload["status"] == "accepted"
    manifest = payload["data"]["material_manifest"]
    assert manifest["materials"][0]["source_ref"] == "repo://docs/route_a.md"
    assert manifest["manual_review"]["decision"] == "accepted"
