import sys

from data_service.workspace_portfolio_real_evidence_acceptance import WorkspacePortfolioRealEvidenceService
from data_service.workspace_portfolio_real_evidence_acceptance.safe_build import execution_rows_from_proposals
from data_service.workspace_portfolio_real_evidence_acceptance.shared import digest_value

from test_v2_101_workspace_portfolio_discovery import _workspace_fixture


def test_v2119_safe_build_generates_proposals_but_does_not_execute_without_approval_and_sandbox(tmp_path, monkeypatch):
    managed, root = _workspace_fixture(tmp_path, monkeypatch)

    payload = WorkspacePortfolioRealEvidenceService(managed, workspace_id="v2119").build(root=root, max_code_projects=1)
    allowlist = payload["data"]["safe_build_allowlist"]
    execution = payload["data"]["safe_build_execution_results"]

    assert allowlist["data"]["commands"]
    assert allowlist["data"]["commands"][0]["approval_status"] == "needs_review"
    assert allowlist["data"]["commands"][0]["cwd_policy"] == "managed_sandbox_working_copy"
    assert execution["data"]["commands"][0]["execution_status"] == "skipped"
    assert execution["data"]["commands"][0]["row_acceptance_status"] in {"needs_review", "structured_blocker"}
    assert execution["data"]["commands"][0]["original_project_write_check_passed"] is False


def test_v2119_approved_command_can_succeed_inside_deterministic_managed_sandbox(tmp_path):
    binding = {
        "executable": sys.executable,
        "argv": [sys.executable, "-c", "print('ok')"],
        "cwd_policy": "managed_sandbox_working_copy",
        "project_input_hash": "a" * 64,
        "env_policy": "minimal_allowlist",
        "network_policy": "disabled",
        "output_policy": "managed_workspace_only",
    }
    command = {
        "command_id": "fixture-command",
        "project_id": "fixture-project",
        "proposal_run_id": "proposal-run",
        "decision_set_id": "decision-set",
        "argv": [sys.executable, "-c", "print('ok')"],
        "cwd_policy": "managed_sandbox_working_copy",
        "normalized_binding_digest": digest_value(binding, length=64),
        "sandbox_policy_digest": digest_value({"sandbox": "managed", "network": "disabled"}, length=64),
        "project_input_hash": "a" * 64,
        "approval_status": "approved",
    }

    rows = execution_rows_from_proposals([command], sandbox_verified=True, workspace_run_dir=tmp_path, execution_run_id="execution-run")

    assert rows[0]["execution_status"] == "succeeded"
    assert rows[0]["row_acceptance_status"] == "accepted"
    assert rows[0]["sandbox_ref"].startswith("run_sandbox/")
    assert rows[0]["original_project_write_check_passed"] is True
