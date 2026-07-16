"""Decision set helpers for V2.116-V2.120."""

from __future__ import annotations

from typing import Any

from data_service.mcp_common import now


def empty_decision_set(*, workspace_id: str, decision_set_id: str, proposal_run_id: str) -> dict[str, Any]:
    return {
        "schema_version": "v2.116-120",
        "workspace_id": workspace_id,
        "decision_set_id": decision_set_id,
        "proposal_run_id": proposal_run_id,
        "parent_decision_set_id": "",
        "generated_at": now(),
        "decisions": [],
    }
