"""V2.96 default CLI gap closure service."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import cli_gap_artifact_refs, read_cli_gap, write_cli_gap
from .shared import apply_redaction_guard, base_artifact, public_payload, status_summary, unresolved_item


class DefaultCliGapClosure:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = Path(workspace)
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(self.workspace, workspace_id=workspace_id)

    def build_cli_gap(self, codebase_id: str, cli_state: dict[str, Any] | None = None) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        state = cli_state or {}
        generated_at = now()
        refs = cli_gap_artifact_refs(codebase_id)
        shell = dict(state.get("shell_command") or {})
        parser = dict(state.get("parser_inventory") or {})
        mcp = dict(state.get("mcp_inventory") or {})
        http = dict(state.get("http_inventory") or {})
        shell_status = str(shell.get("status") or "needs_review")
        parser_status = str(parser.get("status") or "needs_review")
        mcp_status = str(mcp.get("status") or "needs_review")
        http_status = str(http.get("status") or "needs_review")
        statuses = [shell_status, parser_status, mcp_status, http_status]
        status = "accepted" if all(item == "accepted" for item in statuses) else "needs_review"
        evidence_refs = list(state.get("evidence_refs") or [])
        unresolved = []
        if shell_status != "accepted":
            unresolved.append(unresolved_item("needs_review", "default shell CLI command is not accepted", item_id="default_shell_cli", next_action="run PYTHONPATH=backend python -m data_service code real-acceptance-closure --help"))
        if parser_status != "accepted":
            unresolved.append(unresolved_item("needs_review", "parser inventory is not accepted", item_id="parser_inventory", next_action="verify default parser includes code command"))
        if mcp_status != "accepted":
            unresolved.append(unresolved_item("needs_review", "MCP inventory parity is not accepted", item_id="mcp_inventory", next_action="verify automated evidence closure MCP tools"))
        if http_status != "accepted":
            unresolved.append(unresolved_item("needs_review", "HTTP route inventory parity is not accepted", item_id="http_inventory", next_action="verify automated evidence closure HTTP routes"))
        artifact = base_artifact(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            phase="V2.96",
            artifact_type="cli_surface_result",
            generated_at=generated_at,
            artifact_refs=refs,
            evidence_refs=evidence_refs,
            unresolved=unresolved,
            status=status,
            next_actions=["knowledge_code_automated_evidence_closure_cli_gap_read"],
        )
        artifact.update(
            {
                "data": {
                    "default_shell_command": shell,
                    "parser_inventory": parser,
                    "mcp_inventory": mcp,
                    "http_inventory": http,
                    "gap_status": status,
                },
                "summary": status_summary([{"status": item} for item in statuses]),
            }
        )
        apply_redaction_guard(artifact)
        write_cli_gap(self.workspace, codebase_id, artifact)
        return self.read_cli_gap(codebase_id)

    def read_cli_gap(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        artifact = read_cli_gap(self.workspace, codebase_id)
        return {
            "schema_version": "v2.96-100",
            "workspace_id": self.workspace_id,
            "codebase_id": codebase_id,
            "phase": "V2.96",
            "artifact_type": "cli_gap_closure",
            "status": str(artifact.get("status") or "needs_review"),
            "data": {"cli_surface_result": artifact},
            "summary": dict(artifact.get("summary") or {}),
            "artifact_refs": cli_gap_artifact_refs(codebase_id),
            "evidence_refs": list(artifact.get("evidence_refs") or []),
            "warnings": list(artifact.get("warnings") or []),
            "unresolved": list(artifact.get("unresolved") or []),
            "next_actions": ["knowledge_code_automated_evidence_closure_cli_gap_read"],
        }


def public_cli_gap_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return public_payload(payload)

