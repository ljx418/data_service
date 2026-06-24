"""Public surface stabilization for V2.59."""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    read_migration_notes,
    read_public_surface_drift_report,
    read_public_surface_parity_matrix,
    read_public_surface_snapshot,
    stabilization_artifact_refs,
    write_public_surface,
)
from .shared import base_artifact, redaction_findings


PHASE = "V2.59"
CAPABILITIES = ["surface", "e2e", "package", "portal"]
DRIFT_CATEGORIES = {"added", "removed", "renamed", "schema_drift", "route_mismatch", "needs_review"}


class PublicSurfaceStabilizationService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_surface(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        generated_at = now()
        refs = stabilization_artifact_refs(codebase_id)
        snapshot = _surface_snapshot(self.workspace_id, codebase_id, generated_at, refs)
        parity = _parity_matrix(self.workspace_id, codebase_id, generated_at, refs, snapshot)
        drift = _drift_report(self.workspace_id, codebase_id, generated_at, refs, snapshot, parity)
        migration_notes = _migration_notes(snapshot, parity, drift)
        unresolved = redaction_findings(snapshot) + redaction_findings(parity) + redaction_findings(drift) + redaction_findings(migration_notes)
        if unresolved:
            snapshot["unresolved"].extend(unresolved)
            parity["unresolved"].extend(unresolved)
            drift["unresolved"].extend(unresolved)
        write_public_surface(self.workspace, codebase_id, snapshot, parity, drift, migration_notes)
        return _bundle(self.workspace_id, codebase_id, snapshot, parity, drift, migration_notes, refs)

    def read_surface(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = stabilization_artifact_refs(codebase_id)
        return _bundle(
            self.workspace_id,
            codebase_id,
            read_public_surface_snapshot(self.workspace, codebase_id),
            read_public_surface_parity_matrix(self.workspace, codebase_id),
            read_public_surface_drift_report(self.workspace, codebase_id),
            read_migration_notes(self.workspace, codebase_id),
            refs,
        )


def public_surface_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": payload.get("schema_version"),
        "artifact_type": "public_surface_stabilization",
        "snapshot": payload.get("snapshot") or {},
        "parity_matrix": payload.get("parity_matrix") or {},
        "drift_report": payload.get("drift_report") or {},
        "migration_notes": {"format": "markdown", "content": payload.get("migration_notes") or ""},
        "summary": payload.get("summary") or {},
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _bundle(workspace_id: str, codebase_id: str, snapshot: dict[str, Any], parity: dict[str, Any], drift: dict[str, Any], migration_notes: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    warnings = list(snapshot.get("warnings") or []) + list(parity.get("warnings") or []) + list(drift.get("warnings") or [])
    unresolved = list(snapshot.get("unresolved") or []) + list(parity.get("unresolved") or []) + list(drift.get("unresolved") or [])
    return {
        "schema_version": "v2.59-62",
        "artifact_type": "public_surface_stabilization",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "snapshot": snapshot,
        "parity_matrix": parity,
        "drift_report": drift,
        "migration_notes": migration_notes,
        "summary": {
            "mcp_tool_count": len(snapshot.get("mcp_tools") or []),
            "cli_command_count": len(snapshot.get("cli_commands") or []),
            "http_route_count": len(snapshot.get("http_routes") or []),
            "capability_count": len(parity.get("capabilities") or []),
            "hardcoded_expected_only": bool(snapshot.get("hardcoded_expected_only")),
            "drift_count": len(drift.get("drift_items") or []),
        },
        "artifact_refs": refs,
        "warnings": warnings,
        "unresolved": unresolved,
        "next_actions": ["knowledge_code_stabilization_surface_read"],
    }


def _surface_snapshot(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]]) -> dict[str, Any]:
    payload = base_artifact(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        phase=PHASE,
        artifact_type="public_surface_snapshot",
        generated_at=generated_at,
        artifact_refs=refs,
        evidence_refs=[
            {"type": "mcp_registry", "artifact_ref": "backend/data_service/mcp_code_tools.py"},
            {"type": "cli_registry", "artifact_ref": "backend/data_service/cli_code.py"},
            {"type": "http_registry", "artifact_ref": "backend/app/api/__init__.py"},
        ],
    )
    mcp_tools = _discover_mcp_tools()
    cli_commands = _discover_cli_commands()
    http_routes = _discover_http_routes()
    payload.update(
        {
            "source": {
                "mcp_registry": "backend/data_service/mcp_code_tools.py",
                "cli_registry": "backend/data_service/cli_code.py",
                "http_registry": "backend/app/api/__init__.py",
            },
            "mcp_tools": mcp_tools,
            "cli_commands": cli_commands,
            "http_routes": http_routes,
            "discovery_mode": "registry_inspection",
            "hardcoded_expected_only": False,
        }
    )
    return payload


def _discover_mcp_tools() -> list[dict[str, str]]:
    names: set[str] = set()
    for module_name, attr in [
        ("data_service.mcp_code_human_agent_deepening_tools", "HUMAN_AGENT_DEEPENING_TOOL_NAMES"),
        ("data_service.mcp_code_stabilization_e2e_portal_tools", "STABILIZATION_E2E_PORTAL_TOOL_NAMES"),
    ]:
        try:
            module = importlib.import_module(module_name)
            names.update(getattr(module, attr))
        except Exception:
            continue
    return [{"name": name, "operation": _operation_for_name(name)} for name in sorted(names)]


def _discover_cli_commands() -> list[dict[str, str]]:
    commands = []
    try:
        module = importlib.import_module("data_service.cli_code_stabilization_e2e_portal")
        for name in sorted(getattr(module, "STABILIZATION_E2E_PORTAL_COMMAND_TO_TOOL", {})):
            commands.append({"command": f"code stabilization-e2e-portal {name}", "operation": _operation_for_name(name)})
    except Exception:
        pass
    try:
        module = importlib.import_module("data_service.cli_code_human_agent_deepening")
        for name in sorted(getattr(module, "HUMAN_AGENT_DEEPENING_COMMAND_TO_TOOL", {})):
            commands.append({"command": f"code human-agent-deepening {name}", "operation": _operation_for_name(name)})
    except Exception:
        pass
    return commands


def _discover_http_routes() -> list[dict[str, str]]:
    routes = []
    try:
        module = importlib.import_module("app.main")
        for route in getattr(module, "app").routes:
            path = getattr(route, "path", "")
            if "human-agent-deepening" not in path and "stabilization-e2e-portal" not in path:
                continue
            for method in sorted(getattr(route, "methods", []) or []):
                if method in {"HEAD", "OPTIONS"}:
                    continue
                routes.append({"method": method, "path": path, "route_path": path, "operation": _operation_for_name(path)})
    except Exception:
        pass
    return sorted(routes, key=lambda item: (item["path"], item["method"]))


def _operation_for_name(name: str) -> str:
    if "build" in name:
        return "build"
    if "view" in name:
        return "view"
    if "read" in name or name.endswith(("surface", "e2e", "package", "portal", "restore", "regression", "evidence-loop", "task-workflow")):
        return "read"
    return "other"


def _parity_matrix(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], snapshot: dict[str, Any]) -> dict[str, Any]:
    payload = base_artifact(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        phase=PHASE,
        artifact_type="public_surface_parity_matrix",
        generated_at=generated_at,
        artifact_refs=refs,
        evidence_refs=snapshot.get("evidence_refs", []),
    )
    mcp_names = " ".join(item["name"] for item in snapshot.get("mcp_tools", []))
    cli_names = " ".join(item["command"] for item in snapshot.get("cli_commands", []))
    http_paths = " ".join(item.get("route_path") or item.get("path", "") for item in snapshot.get("http_routes", []))
    capabilities = []
    for capability in CAPABILITIES:
        mcp = "present" if f"_{capability}_" in mcp_names or mcp_names.endswith(f"_{capability}_read") or capability in mcp_names else "missing"
        cli = "present" if capability in cli_names else "missing"
        http = "present" if f"/{capability}" in http_paths else "missing"
        status = "accepted" if mcp == cli == http == "present" else "needs_review"
        capabilities.append({"capability": capability, "mcp": mcp, "cli": cli, "http": http, "parity_status": status})
    payload["capabilities"] = capabilities
    if any(item["parity_status"] != "accepted" for item in capabilities):
        payload["warnings"].append("PUBLIC_SURFACE_PARITY_PARTIAL")
    return payload


def _drift_report(workspace_id: str, codebase_id: str, generated_at: str, refs: list[dict[str, str]], snapshot: dict[str, Any], parity: dict[str, Any]) -> dict[str, Any]:
    payload = base_artifact(
        workspace_id=workspace_id,
        codebase_id=codebase_id,
        phase=PHASE,
        artifact_type="public_surface_drift_report",
        generated_at=generated_at,
        artifact_refs=refs,
        evidence_refs=snapshot.get("evidence_refs", []),
    )
    drift_items = []
    for item in parity.get("capabilities", []):
        if item.get("parity_status") != "accepted":
            drift_items.append(
                {
                    "surface": "mcp|cli|http",
                    "name": item["capability"],
                    "category": "needs_review",
                    "evidence_refs": [ref["artifact_ref"] for ref in snapshot.get("evidence_refs", [])],
                }
            )
    payload["drift_items"] = drift_items
    payload["allowed_categories"] = sorted(DRIFT_CATEGORIES)
    return payload


def _migration_notes(snapshot: dict[str, Any], parity: dict[str, Any], drift: dict[str, Any]) -> str:
    lines = [
        "# Public Surface Migration Notes",
        "",
        "## Summary",
        "",
        f"- MCP tools discovered: {len(snapshot.get('mcp_tools') or [])}",
        f"- CLI commands discovered: {len(snapshot.get('cli_commands') or [])}",
        f"- HTTP routes discovered: {len(snapshot.get('http_routes') or [])}",
        f"- Drift items: {len(drift.get('drift_items') or [])}",
        "",
        "## Required Follow-up Tests",
        "",
        "- Run `backend/tests/test_public_surface_guard.py`.",
        "- Run the V2.59 focused test before accepting public surface changes.",
        "- Run real data_service E2E to verify generated artifacts are readable.",
        "",
        "## User-facing Impact",
        "",
        "Maintainers can inspect whether MCP, CLI, and HTTP contracts are present and whether drift requires migration work.",
        "",
    ]
    for item in parity.get("capabilities", []):
        lines.append(f"- {item['capability']}: {item['parity_status']}")
    return "\n".join(lines)
