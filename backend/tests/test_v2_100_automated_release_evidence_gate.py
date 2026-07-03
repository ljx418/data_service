from data_service.code_assets.automated_evidence_closure.cli_gap import DefaultCliGapClosure
from data_service.code_assets.automated_evidence_closure.external_path_registry import ExternalProjectPathRegistry
from data_service.code_assets.automated_evidence_closure.quality_workbench import QualityDecisionWorkbench
from data_service.code_assets.automated_evidence_closure.release_evidence_gate import AutomatedReleaseEvidenceGate
from data_service.code_assets.automated_evidence_closure.route_a_evidence import RouteAEvidenceAutomator
from data_service.code_assets.real_acceptance_closure.persistence import write_release_finalizer
from data_service.code_assets.registry import CodebaseRegistry


def _prepare(tmp_path, monkeypatch, workspace_id="v2100"):
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    (docs / "route_a.md").write_text("# route a\n", encoding="utf-8")
    workspace = tmp_path / "managed" / workspace_id
    workspace.mkdir(parents=True)
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_WORKSPACE_ROOTS", str(tmp_path))
    monkeypatch.setenv("DATA_SERVICE_ALLOWED_CODEBASE_ROOTS", str(tmp_path))
    codebase_id = CodebaseRegistry(workspace, workspace_id=workspace_id).import_codebase(path=str(repo), name="V2100")["asset"].codebase_id
    return workspace, codebase_id, repo


def _build_inputs(workspace, codebase_id, repo, tmp_path):
    DefaultCliGapClosure(workspace, workspace_id="v2100").build_cli_gap(
        codebase_id,
        {
            "shell_command": {"status": "accepted"},
            "parser_inventory": {"status": "accepted"},
            "mcp_inventory": {"status": "accepted"},
            "http_inventory": {"status": "accepted"},
            "evidence_refs": ["command://cli-gap"],
        },
    )
    RouteAEvidenceAutomator(workspace, workspace_id="v2100").build_route_a_evidence(
        codebase_id,
        {
            "materials": [{"source_ref": "repo://docs/route_a.md", "redaction_status": "accepted", "evidence_refs": ["repo://docs/route_a.md"]}],
            "redaction": {"status": "accepted", "policy_ref": "manual://redaction", "risk": "low"},
            "evidence_capture": {"status": "accepted", "evidence_refs": ["screenshot://route-a"]},
            "manual_confirmation": {"decision": "accepted", "evidence_refs": ["manual://route-a"]},
        },
    )
    QualityDecisionWorkbench(workspace, workspace_id="v2100").build_quality_workbench(
        codebase_id,
        {
            "recommendations": [{"recommendation_id": "q1", "risk_level": "high", "evidence_refs": ["artifact://quality/q1"]}],
            "human_decisions": [{"recommendation_id": "q1", "decision": "approved", "evidence_refs": ["review://q1"]}],
        },
    )
    paths = {}
    commands = {}
    for project_id in ["data_service", "codexPat", "HarnessOS", "Navia"]:
        path = repo if project_id == "data_service" else tmp_path / project_id
        path.mkdir(exist_ok=True)
        paths[project_id] = str(path)
        commands[project_id] = "true"
    ExternalProjectPathRegistry(workspace, workspace_id="v2100").build_external_path(codebase_id, {"project_paths": paths, "smoke_commands": commands})
    write_release_finalizer(workspace, codebase_id, {"status": "accepted", "final_release_status": "accepted", "evidence_refs": ["artifact://v95/final"]}, "# v95\n", "# false green\n")


def test_v2100_release_gate_blocks_without_human_approval(tmp_path, monkeypatch):
    workspace, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    _build_inputs(workspace, codebase_id, repo, tmp_path)

    payload = AutomatedReleaseEvidenceGate(workspace, workspace_id="v2100").build_release_gate(codebase_id)

    assert payload["status"] == "needs_review"
    assert any(item["id"] == "human_approval" for item in payload["unresolved"])


def test_v2100_release_gate_accepts_only_when_all_high_risk_evidence_passes(tmp_path, monkeypatch):
    workspace, codebase_id, repo = _prepare(tmp_path, monkeypatch)
    _build_inputs(workspace, codebase_id, repo, tmp_path)

    payload = AutomatedReleaseEvidenceGate(workspace, workspace_id="v2100").build_release_gate(
        codebase_id,
        {
            "dependency_hygiene_state": {"status": "accepted", "evidence_refs": ["audit://dependency"]},
            "restore_smoke_state": {"status": "accepted", "evidence_refs": ["command://restore-smoke"]},
            "prd_spec_review_state": {"status": "accepted", "evidence_refs": ["review://prd-spec"]},
            "human_approval_state": {"status": "accepted", "evidence_refs": ["manual://release-approval"]},
        },
    )

    assert payload["status"] == "accepted"
    assert not payload["unresolved"]

