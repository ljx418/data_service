import json

from data_service.code_assets.automated_evidence_closure.route_a_evidence import RouteAEvidenceAutomator
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v297"):
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (docs / "route_a.md").write_text("# 用户代表性资料\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    workspace = workspace_root / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V297")["asset"].codebase_id
    return workspace, codebase_id


def test_v297_route_a_missing_real_material_stays_needs_review(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    payload = RouteAEvidenceAutomator(workspace, workspace_id="v297").build_route_a_evidence(codebase_id, {})

    assert payload["status"] == "needs_review"
    assert any(item["id"] == "route_a_materials" for item in payload["unresolved"])


def test_v297_route_a_accepts_only_with_material_redaction_capture_and_manual_confirmation(tmp_path, monkeypatch):
    workspace, codebase_id = _prepare(tmp_path, monkeypatch)
    payload = RouteAEvidenceAutomator(workspace, workspace_id="v297").build_route_a_evidence(
        codebase_id,
        {
            "materials": [{"material_id": "route_a_doc", "source_type": "markdown", "source_ref": "repo://docs/route_a.md", "redaction_status": "accepted", "evidence_refs": ["repo://docs/route_a.md"]}],
            "redaction": {"status": "accepted", "policy_ref": "manual://redaction-policy", "risk": "low"},
            "evidence_capture": {"status": "accepted", "method": "headless", "evidence_refs": ["screenshot://route-a/portal"]},
            "manual_confirmation": {"decision": "accepted", "reviewer": "maintainer", "evidence_refs": ["manual://route-a-confirmation"]},
        },
    )

    assert payload["status"] == "accepted"
    raw = json.dumps(payload, ensure_ascii=False)
    assert "Traceback (most recent call last)" not in raw
    assert "/mnt/" not in raw

