from pathlib import Path

import tomllib


ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_v53_test_dependency_baseline_is_documented_and_pinned():
    requirements = _read("backend/requirements-test.txt").splitlines()
    assert "pytest==8.4.2" in requirements
    assert "pytest-asyncio==0.23.8" in requirements
    assert "httpx==0.27.0" in requirements
    assert "fastapi==0.109.2" in requirements
    assert "starlette==0.36.3" in requirements

    pyproject = tomllib.loads(_read("backend/pyproject.toml"))
    test_deps = pyproject["project"]["optional-dependencies"]["test"]
    assert "pytest==8.4.2" in test_deps
    assert "pytest-asyncio==0.23.8" in test_deps
    assert "httpx==0.27.0" in test_deps
    assert "fastapi==0.109.2" in test_deps
    assert "starlette==0.36.3" in test_deps


def test_v53_acceptance_runner_tracks_focused_suite_and_static_checks():
    runner = _read("backend/scripts/v2_53_acceptance.py")
    for test_file in [
        "backend/tests/test_v2_46_agent_productization.py",
        "backend/tests/test_v2_47_profile_onboarding.py",
        "backend/tests/test_v2_48_human_portal.py",
        "backend/tests/test_v2_49_task_navigation.py",
        "backend/tests/test_v2_50_governance_workflow.py",
        "backend/tests/test_v2_51_agent_playbooks.py",
        "backend/tests/test_v2_52_continuous_acceptance.py",
        "backend/tests/test_v2_53_acceptance_infrastructure.py",
        "backend/tests/test_public_surface_guard.py",
    ]:
        assert test_file in runner
    assert '"git", "diff", "--check"' in runner
    assert '"compileall", "-q", "backend/data_service", "backend/app/api/v1"' in runner


def test_v53_direct_ui_parity_matrix_matches_phase_129_closure():
    matrix = _read("docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_FULL_COVERAGE_MATRIX.md")
    closure = _read("docs/V2.x/V2_52_PHASE_129_CONTINUOUS_ACCEPTANCE_ACCEPTANCE_AUDIT_REPORT.md")
    assert "| V248-004 | Direct UI route parity or exception | 125/129 | `public_contract_parity.json` | accepted |" in matrix
    assert "closed by Phase 129" in matrix
    assert "structured_blocker_count = 0" in closure
    assert "public contract parity is accepted" in closure


def test_v53_phase_documents_exist_and_preserve_claim_boundaries():
    for path in [
        "docs/V2.x/V2_53_ACCEPTANCE_INFRASTRUCTURE_DEVELOPMENT_PLAN.md",
        "docs/V2.x/V2_53_ACCEPTANCE_INFRASTRUCTURE_ACCEPTANCE_PLAN.md",
        "docs/V2.x/V2_53_ACCEPTANCE_INFRASTRUCTURE_PRE_IMPLEMENTATION_AUDIT_REPORT.md",
        "docs/V2.x/V2_53_ACCEPTANCE_INFRASTRUCTURE_ACCEPTANCE_AUDIT_REPORT.md",
        "docs/V2.x/V2_53_ACCEPTANCE_COMMANDS.md",
    ]:
        assert (ROOT / path).exists()

    development_plan = _read("docs/V2.x/V2_53_ACCEPTANCE_INFRASTRUCTURE_DEVELOPMENT_PLAN.md")
    assert "does not add product capability" in development_plan
    assert "No claim of full call graph" in development_plan
    assert "No changes to `backend/app/api/v1/data_service.py`" in development_plan
    assert "No changes to `backend/data_service/service.py`" in development_plan
