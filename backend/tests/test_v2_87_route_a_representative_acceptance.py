import json

from data_service.code_assets.real_document_full_corpus_release.route_a_acceptance import RouteAAcceptanceService
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v287"):
    repo = tmp_path / "repo"
    docs = repo / "docs" / "V2.x"
    docs.mkdir(parents=True)
    (docs / "representative.md").write_text("# 用户代表性资料\n\n真实脱敏资料。\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V287")["asset"].codebase_id
    return workspace, codebase_id


def test_v287_route_a_missing_material_remains_needs_review(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)

    payload = RouteAAcceptanceService(workspace, workspace_id="v287").build_route_a(codebase_id)
    contract = payload["data"]["sample_pack_contract"]

    assert payload["status"] == "needs_review"
    assert contract["route"] == "Route A"
    assert contract["status"] == "needs_review"
    assert any(item["id"] == "route_a_materials" for item in payload["unresolved"])


def test_v287_route_a_accepts_only_with_manual_evidence(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    state = {
        "sample_pack_ref": "repo://docs/V2.x/representative.md",
        "manual_review_state": "accepted",
        "evidence_refs": ["repo://docs/V2.x/representative.md", "headless://route-a-screenshot"],
        "redaction_policy": "manual_redacted",
    }

    payload = RouteAAcceptanceService(workspace, workspace_id="v287").build_route_a(codebase_id, state)
    contract = payload["data"]["sample_pack_contract"]

    assert payload["status"] == "accepted"
    assert contract["sample_pack_ref"] == "repo://docs/V2.x/representative.md"
    assert contract["route"] == "Route A"
    assert str(tmp_path) not in json.dumps(payload, ensure_ascii=False)
