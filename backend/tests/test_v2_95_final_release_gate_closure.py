from fastapi.testclient import TestClient

from app.main import app
from data_service.__main__ import _build_knowledge_parser
from data_service.code_assets.real_acceptance_closure.external_project_validator import ExternalProjectPathE2EValidator
from data_service.code_assets.real_acceptance_closure.quality_decision import HumanQualityDecisionRecorder
from data_service.code_assets.real_acceptance_closure.release_finalizer import FinalReleaseGateFinalizer
from data_service.code_assets.real_acceptance_closure.route_a_material import RouteAMaterialIntakeReview
from data_service.code_assets.real_acceptance_closure.runtime_restore import AcceptanceRuntimeRestorer
from data_service.code_assets.real_document_acceptance.persistence import write_real_e2e
from data_service.code_assets.real_document_full_corpus_release.persistence import write_full_corpus, write_quality_review
from data_service.code_assets.registry import CodebaseRegistry
from data_service.mcp_tool_registry import all_tool_specs


def _prepare(tmp_path, monkeypatch, workspace_id="v295"):
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (docs / "route_a.md").write_text("# 用户代表性资料\n", encoding="utf-8")
    workspace_root = tmp_path / "managed"
    workspace = workspace_root / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_WORKSPACE_ROOT", str(workspace_root))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V295")["asset"].codebase_id
    return workspace, codebase_id, repo, workspace_root


def _fake_python(tmp_path):
    script = tmp_path / "fake_python"
    script.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = \"-m\" ] && [ \"$2\" = \"pytest\" ]; then exit 0; fi\n"
        "if [ \"$1\" = \"-m\" ] && [ \"$2\" = \"venv\" ]; then mkdir -p \"$3/bin\"; exit 0; fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return str(script)


def _fake_python_without_venv(tmp_path):
    script = tmp_path / "fake_python_without_venv"
    script.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = \"-m\" ] && [ \"$2\" = \"pytest\" ]; then exit 0; fi\n"
        "if [ \"$1\" = \"-m\" ] && [ \"$2\" = \"venv\" ]; then exit 1; fi\n"
        "exit 0\n",
        encoding="utf-8",
    )
    script.chmod(0o755)
    return str(script)


def _build_all_closure_inputs(workspace, codebase_id, repo, tmp_path):
    AcceptanceRuntimeRestorer(workspace, workspace_id="v295").build_runtime_restore(codebase_id, {"python_command": _fake_python(tmp_path), "focused_command": "true"})
    RouteAMaterialIntakeReview(workspace, workspace_id="v295").build_route_a_closure(
        codebase_id,
        {
            "materials": [{"material_id": "route_a_doc", "source_type": "markdown", "source_ref": "repo://docs/route_a.md", "redaction_status": "accepted"}],
            "redaction": {"status": "accepted", "policy_ref": "manual://redaction-policy"},
            "manual_review": {"reviewer": "maintainer", "decision": "accepted"},
            "evidence_refs": ["repo://docs/route_a.md", "manual://route-a-review"],
        },
    )
    write_quality_review(workspace, codebase_id, {"status": "needs_review", "artifact_type": "human_quality_review", "decisions": [{"recommendation_id": "source_trace_quality"}]}, "", "# quality\n")
    HumanQualityDecisionRecorder(workspace, workspace_id="v295").build_quality_decision(codebase_id, {"reviewer": "maintainer", "decisions": [{"decision_id": "source_trace_quality", "decision": "approved", "evidence_refs": ["review://source_trace_quality"]}]})
    paths = {}
    commands = {}
    for project_id in ["data_service", "codexPat", "HarnessOS", "Navia"]:
        path = repo if project_id == "data_service" else tmp_path / project_id
        path.mkdir(exist_ok=True)
        paths[project_id] = str(path)
        commands[project_id] = "true"
    ExternalProjectPathE2EValidator(workspace, workspace_id="v295").build_external_project_closure(codebase_id, {"project_paths": paths, "smoke_commands": commands})
    write_real_e2e(workspace, codebase_id, {"status": "accepted", "evidence_refs": ["repo://docs/route_a.md"]}, {"status": "accepted"}, "# route b\n")
    write_full_corpus(workspace, codebase_id, {"status": "accepted", "evidence_refs": ["repo://docs/route_a.md"]}, {"status": "accepted"}, "# full corpus\n")


def test_v295_final_release_keeps_missing_inputs_visible(tmp_path, monkeypatch):
    workspace, codebase_id, _, _ = _prepare(tmp_path, monkeypatch)

    payload = FinalReleaseGateFinalizer(workspace, workspace_id="v295").build_release_finalizer(codebase_id)

    assert payload["status"] != "accepted"
    assert any(item["id"] == "human_approval" for item in payload["unresolved"])
    assert payload["data"]["final_gate_summary"]["false_green_audit"]["rejected_claims"]


def test_v295_final_release_accepts_only_when_all_high_risk_checks_pass(tmp_path, monkeypatch):
    workspace, codebase_id, repo, _ = _prepare(tmp_path, monkeypatch)
    _build_all_closure_inputs(workspace, codebase_id, repo, tmp_path)

    payload = FinalReleaseGateFinalizer(workspace, workspace_id="v295").build_release_finalizer(
        codebase_id,
        {
            "dependency_hygiene_state": {"status": "accepted", "evidence_refs": ["audit://dependency"]},
            "restore_smoke_state": {"status": "accepted", "evidence_refs": ["command://restore_smoke"]},
            "public_surface_state": {"status": "accepted", "evidence_refs": ["pytest://public_surface_guard"]},
            "protected_legacy_diff_state": {"status": "accepted", "evidence_refs": ["git://protected_diff"]},
            "prd_spec_review_state": {"status": "accepted", "evidence_refs": ["review://prd_spec"]},
            "human_approval_state": {"status": "accepted", "evidence_refs": ["manual://release_approval"]},
        },
    )

    assert payload["status"] == "accepted"
    assert all(check["status"] == "accepted" for check in payload["data"]["final_gate_summary"]["checks"])


def test_v295_final_release_does_not_accept_runtime_when_venv_probe_fails(tmp_path, monkeypatch):
    workspace, codebase_id, repo, _ = _prepare(tmp_path, monkeypatch)
    _build_all_closure_inputs(workspace, codebase_id, repo, tmp_path)
    AcceptanceRuntimeRestorer(workspace, workspace_id="v295").build_runtime_restore(
        codebase_id,
        {"python_command": _fake_python_without_venv(tmp_path), "focused_command": "true"},
    )

    payload = FinalReleaseGateFinalizer(workspace, workspace_id="v295").build_release_finalizer(
        codebase_id,
        {
            "dependency_hygiene_state": {"status": "accepted", "evidence_refs": ["audit://dependency"]},
            "restore_smoke_state": {"status": "accepted", "evidence_refs": ["command://restore_smoke"]},
            "public_surface_state": {"status": "accepted", "evidence_refs": ["pytest://public_surface_guard"]},
            "protected_legacy_diff_state": {"status": "accepted", "evidence_refs": ["git://protected_diff"]},
            "prd_spec_review_state": {"status": "accepted", "evidence_refs": ["review://prd_spec"]},
            "human_approval_state": {"status": "accepted", "evidence_refs": ["manual://release_approval"]},
        },
    )

    checks = {check["id"]: check for check in payload["data"]["final_gate_summary"]["checks"]}
    assert payload["status"] == "structured_blocker"
    assert checks["runtime"]["status"] == "structured_blocker"
    assert any(item["id"] == "venv_runtime" for item in checks["runtime"]["unresolved"])


def test_v295_public_surface_inventory_includes_real_acceptance_closure(tmp_path, monkeypatch):
    workspace, codebase_id, _, workspace_root = _prepare(tmp_path, monkeypatch)
    parser = _build_knowledge_parser()
    args = parser.parse_args(
        [
            "code",
            "real-acceptance-closure",
            "release-finalizer-read",
            "--workspace-root",
            str(workspace_root),
            "--workspace-id",
            "v295",
            "--codebase-id",
            codebase_id,
        ]
    )
    assert args.code_command == "real-acceptance-closure"
    assert "knowledge_code_real_acceptance_closure_release_finalizer_read" in {spec["name"] for spec in all_tool_specs()}
    client = TestClient(app)
    response = client.get(f"/api/workspaces/v295/codebases/{codebase_id}/real-acceptance-closure/release-finalizer")
    assert response.status_code == 404
