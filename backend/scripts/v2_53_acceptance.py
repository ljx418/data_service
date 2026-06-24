"""Run the V2.46-V2.52 acceptance infrastructure checks.

This runner intentionally keeps one canonical command list for the V2.53
acceptance-infrastructure phase. It does not mutate tracked files.
"""

from __future__ import annotations

import subprocess
import sys


FOCUSED_TESTS = [
    "backend/tests/test_v2_46_agent_productization.py",
    "backend/tests/test_v2_47_profile_onboarding.py",
    "backend/tests/test_v2_48_human_portal.py",
    "backend/tests/test_v2_49_task_navigation.py",
    "backend/tests/test_v2_50_governance_workflow.py",
    "backend/tests/test_v2_51_agent_playbooks.py",
    "backend/tests/test_v2_52_continuous_acceptance.py",
    "backend/tests/test_v2_53_acceptance_infrastructure.py",
    "backend/tests/test_public_surface_guard.py",
]


def _run(command: list[str]) -> int:
    print("$ " + " ".join(command), flush=True)
    completed = subprocess.run(command, check=False)
    return int(completed.returncode)


def main() -> int:
    commands = [
        [sys.executable, "-m", "pytest", "-q", *FOCUSED_TESTS],
        ["git", "diff", "--check"],
        [sys.executable, "-m", "compileall", "-q", "backend/data_service", "backend/app/api/v1"],
    ]
    for command in commands:
        code = _run(command)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
