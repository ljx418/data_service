# V2.46-V2.52 Codex Handoff and Restore Guide

Last updated: 2026-06-22

## 1. Purpose

This document preserves the current Codex terminal context for moving development to another machine. It is intentionally explicit about what is accepted, what was tested, and what is not claimed.

Repository remote:

```text
https://github.com/ljx418/data_service.git
```

Current branch:

```text
main
```

## 2. Current Project State

The current worktree contains the completed V2.46-V2.52 Agent Productization phase.

Accepted scope:

- Phase 123 / V2.46: MCP Productization
- Phase 124 / V2.47: Project Profile Onboarding
- Phase 125 / V2.48: Human Architecture Portal
- Phase 126 / V2.49: Task Navigation and Impact
- Phase 127 / V2.50: Doc-Code Governance Workflow
- Phase 128 / V2.51: Agent Context Playbooks
- Phase 129 / V2.52: Multi-project Continuous Acceptance Closure

Current accepted statement:

```text
V2.46-V2.52 Agent Productization is accepted for the current worktree. Phase 123-129 passed staged development, focused tests, real repo E2E, public surface guard, redaction checks, and closure audit.
```

Important boundary:

```text
This does not claim full automatic architecture-intent recovery, full call graph, full runtime topology, data flow, control flow, type inference, or remote repository deployment unless a later commit/push evidence says so.
```

## 3. Main Implementation Files

Agent Productization implementation:

```text
backend/data_service/code_assets/agent_productization/
  __init__.py
  persistence.py
  mcp_usage.py
  profile_onboarding.py
  human_portal.py
  task_navigation.py
  governance.py
  playbooks.py
  closure.py
```

Public entrypoints:

```text
backend/app/api/v1/code_assets_agent_productization.py
backend/data_service/mcp_code_agent_productization_tools.py
backend/data_service/cli_code_agent_productization.py
```

Registration files:

```text
backend/app/api/__init__.py
backend/data_service/mcp_code_tools.py
backend/data_service/cli_code.py
backend/tests/test_public_surface_guard.py
```

Focused tests:

```text
backend/tests/test_v2_46_agent_productization.py
backend/tests/test_v2_47_profile_onboarding.py
backend/tests/test_v2_48_human_portal.py
backend/tests/test_v2_49_task_navigation.py
backend/tests/test_v2_50_governance_workflow.py
backend/tests/test_v2_51_agent_playbooks.py
backend/tests/test_v2_52_continuous_acceptance.py
```

## 4. Main Documents

Core planning and acceptance documents:

```text
docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_PRD.md
docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_TARGET_ARCHITECTURE.md
docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_DEVELOPMENT_AND_ACCEPTANCE_PLAN.md
docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_PHASE_123_129_DETAILED_IMPLEMENTATION_PACKAGE.md
docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_FULL_COVERAGE_MATRIX.md
docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_REAL_REPO_E2E_ACCEPTANCE_MATRIX.md
docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_MILESTONES_AND_EXIT_GATES.md
docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_DOCUMENT_AUDIT_REPORT.md
docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_TARGET_STATE.drawio
```

Human-readable reports:

```text
docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_HTML_ACCEPTANCE_REPORT.html
docs/V2.x/WORKSPACE_PROJECTS_HUMAN_SHOWCASE.html
docs/V2.x/workspace_projects_human_summary.json
```

Final acceptance reports:

```text
docs/V2.x/V2_51_PHASE_128_AGENT_PLAYBOOKS_ACCEPTANCE_AUDIT_REPORT.md
docs/V2.x/V2_52_PHASE_129_CONTINUOUS_ACCEPTANCE_ACCEPTANCE_AUDIT_REPORT.md
```

## 5. Last Verification Commands

Run from repository root:

```bash
pytest -q backend/tests/test_v2_46_agent_productization.py \
  backend/tests/test_v2_47_profile_onboarding.py \
  backend/tests/test_v2_48_human_portal.py \
  backend/tests/test_v2_49_task_navigation.py \
  backend/tests/test_v2_50_governance_workflow.py \
  backend/tests/test_v2_51_agent_playbooks.py \
  backend/tests/test_v2_52_continuous_acceptance.py \
  backend/tests/test_public_surface_guard.py
```

Expected local result at handoff time:

```text
19 passed
```

Additional checks:

```bash
git diff --check
/usr/bin/python3 -m compileall -q backend/data_service backend/app/api/v1
```

Expected local result at handoff time:

```text
passed
```

## 6. Restore on Another Machine

Minimum steps:

```bash
git clone https://github.com/ljx418/data_service.git
cd data_service
git status --short
```

Install project dependencies according to the repository baseline. If a virtual environment already exists in project instructions, use it. Otherwise start with:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -U pip
./.venv/bin/python -m pip install -e backend
```

Then run the focused acceptance suite:

```bash
./.venv/bin/python -m pytest -q backend/tests/test_v2_46_agent_productization.py \
  backend/tests/test_v2_47_profile_onboarding.py \
  backend/tests/test_v2_48_human_portal.py \
  backend/tests/test_v2_49_task_navigation.py \
  backend/tests/test_v2_50_governance_workflow.py \
  backend/tests/test_v2_51_agent_playbooks.py \
  backend/tests/test_v2_52_continuous_acceptance.py \
  backend/tests/test_public_surface_guard.py
```

Open human reports:

```bash
open docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_HTML_ACCEPTANCE_REPORT.html
open docs/V2.x/WORKSPACE_PROJECTS_HUMAN_SHOWCASE.html
```

If the new machine is not macOS, open the HTML files manually in a browser.

## 7. Prompt for the Next Codex Terminal

Copy this prompt into the new Codex terminal after cloning the repository:

```text
你现在接手 /Users/Zhuanz/Desktop/workspace/data_service 项目。

请先阅读以下交接文档和验收文档：
- docs/V2.x/V2_46_52_CODEX_HANDOFF_AND_RESTORE_GUIDE.md
- docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_PRD.md
- docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_TARGET_ARCHITECTURE.md
- docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_FULL_COVERAGE_MATRIX.md
- docs/V2.x/V2_52_PHASE_129_CONTINUOUS_ACCEPTANCE_ACCEPTANCE_AUDIT_REPORT.md
- docs/V2.x/V2_46_52_AGENT_PRODUCTIZATION_HTML_ACCEPTANCE_REPORT.html
- docs/V2.x/WORKSPACE_PROJECTS_HUMAN_SHOWCASE.html

当前已完成并验收的主线是 V2.46-V2.52 Agent Productization：
MCP Productization、Project Profile Onboarding、Human Portal、Task Navigation、Governance Workflow、Agent Playbooks、Continuous Acceptance Closure。

请先运行或评估以下测试：
pytest -q backend/tests/test_v2_46_agent_productization.py backend/tests/test_v2_47_profile_onboarding.py backend/tests/test_v2_48_human_portal.py backend/tests/test_v2_49_task_navigation.py backend/tests/test_v2_50_governance_workflow.py backend/tests/test_v2_51_agent_playbooks.py backend/tests/test_v2_52_continuous_acceptance.py backend/tests/test_public_surface_guard.py

重要边界：
- 不要声称本项目已完整恢复复杂项目设计意图。
- 不要声称 full call graph、runtime topology、data/control flow 或 type inference。
- 不要把 documentation claim 当作 code fact。
- 不要把 needs_review / structured_unavailable 写成 accepted。
- 不要修改 legacy 大文件 backend/app/api/v1/data_service.py 或 backend/data_service/service.py，除非用户明确批准。
- 新阶段开始前必须先做开发计划、验收计划、pre-implementation audit；阶段结束后必须有 focused tests、真实项目 E2E、PRD/spec review、false-green audit。

请先汇报：
1. 当前 git commit 和 git status。
2. V2.46-V2.52 验收文档是否齐全。
3. 测试是否可运行。
4. 是否发现任何 fatal/major 迁移风险。
然后再继续任何新开发。
```

## 8. Notes for Future Work

Potential next directions discussed before handoff:

- improve human-facing project portal depth and chart quality;
- run full profile / portal / task navigation / governance / playbook / closure flows for individual large projects;
- strengthen doc-code architecture verification;
- continue large project architecture assistance for HarnessOS, Navia, codexPat, and other workspace projects;
- keep every accepted claim evidence-backed.

