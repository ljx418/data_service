"""MCP usage guide productization for Codex/Copilot-style agents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .persistence import (
    mcp_productization_artifact_refs,
    read_codex_mcp_usage_guide,
    read_mcp_agent_workflows,
    read_mcp_tool_catalog,
    read_mcp_usage_guide,
    write_mcp_productization,
)


AGENT_PRODUCTIZATION_SCHEMA_VERSION = "v2.46-52"


class AgentMCPProductizationService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_mcp_usage(self, codebase_id: str, tool_specs: list[dict[str, Any]]) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = mcp_productization_artifact_refs(codebase_id)
        catalog = _build_catalog(self.workspace_id, codebase_id, tool_specs, refs)
        workflows = _build_workflows(self.workspace_id, codebase_id, {tool["tool_name"] for tool in catalog["tools"]}, refs)
        usage_guide = _build_usage_guide(self.workspace_id, codebase_id, catalog, workflows, refs)
        markdown = _render_markdown(usage_guide, catalog, workflows)
        write_mcp_productization(self.workspace, codebase_id, usage_guide, catalog, workflows, markdown)
        return {
            "mcp_usage_guide": usage_guide,
            "mcp_tool_catalog_readable": catalog,
            "mcp_agent_workflows": workflows,
            "codex_mcp_usage_guide": {"content": markdown, "format": "markdown"},
            "artifact_refs": refs,
            "warnings": [],
            "unresolved": workflows.get("unresolved", []),
            "next_actions": ["knowledge_code_agent_productization_mcp_read"],
        }

    def read_mcp_usage(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = mcp_productization_artifact_refs(codebase_id)
        return {
            "mcp_usage_guide": read_mcp_usage_guide(self.workspace, codebase_id),
            "mcp_tool_catalog_readable": read_mcp_tool_catalog(self.workspace, codebase_id),
            "mcp_agent_workflows": read_mcp_agent_workflows(self.workspace, codebase_id),
            "codex_mcp_usage_guide": {"content": read_codex_mcp_usage_guide(self.workspace, codebase_id), "format": "markdown"},
            "artifact_refs": refs,
            "warnings": [],
            "unresolved": read_mcp_agent_workflows(self.workspace, codebase_id).get("unresolved", []),
            "next_actions": ["knowledge_code_agent_productization_mcp_read"],
        }


def public_mcp_productization_payload(payload: dict[str, Any]) -> dict[str, Any]:
    guide = dict(payload.get("mcp_usage_guide") or {})
    catalog = dict(payload.get("mcp_tool_catalog_readable") or {})
    workflows = dict(payload.get("mcp_agent_workflows") or {})
    markdown = dict(payload.get("codex_mcp_usage_guide") or {})
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "artifact_type": "agent_productization_mcp_bundle",
        "mcp_usage_guide": guide,
        "mcp_tool_catalog_readable": catalog,
        "mcp_agent_workflows": workflows,
        "codex_mcp_usage_guide": {
            "format": markdown.get("format", "markdown"),
            "content": markdown.get("content", ""),
        },
        "tool_count": int(catalog.get("tool_count") or 0),
        "workflow_count": int(workflows.get("workflow_count") or 0),
        "validation_summary": guide.get("validation_summary", {}),
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _build_catalog(workspace_id: str, codebase_id: str, tool_specs: list[dict[str, Any]], refs: list[dict[str, str]]) -> dict[str, Any]:
    tools = [_tool_entry(spec) for spec in sorted(tool_specs, key=lambda item: str(item.get("name") or ""))]
    groups: dict[str, list[str]] = {}
    for tool in tools:
        groups.setdefault(tool["group_id"], []).append(tool["tool_name"])
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "artifact_type": "mcp_tool_catalog_readable",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "generated_at": now(),
        "tool_count": len(tools),
        "groups": [{"group_id": group, "tool_count": len(names), "tools": sorted(names)} for group, names in sorted(groups.items())],
        "tools": tools,
        "artifact_refs": refs,
    }


def _tool_entry(spec: dict[str, Any]) -> dict[str, Any]:
    name = str(spec.get("name") or "")
    schema = spec.get("inputSchema") or {}
    required = sorted(str(item) for item in list(schema.get("required") or []))
    properties = schema.get("properties") or {}
    optional = sorted(str(key) for key in properties if key not in required)
    return {
        "tool_name": name,
        "group_id": _group_for(name),
        "description": str(spec.get("description") or ""),
        "required_inputs": required,
        "optional_inputs": optional,
        "recommended_for": _recommended_for(name),
        "expected_outputs": _expected_outputs(name),
        "failure_modes": _failure_modes(name),
    }


def _group_for(name: str) -> str:
    if name.startswith("knowledge_code_platform_"):
        return "platform"
    if "architecture" in name:
        return "architecture"
    if name.startswith("knowledge_code") or name.startswith("knowledge_project") or name.startswith("knowledge_agent"):
        return "codebase"
    if name.startswith("knowledge_workspace"):
        return "workspace"
    if name.startswith("knowledge_source"):
        return "source"
    if name.startswith("knowledge_build"):
        return "build"
    if name.startswith("knowledge_quality") or name.startswith("knowledge_correction"):
        return "quality"
    if name.startswith("knowledge_session") or name.startswith("knowledge_actor"):
        return "session"
    return "core"


def _recommended_for(name: str) -> list[str]:
    tags = []
    if any(token in name for token in ("overview", "inventory", "devwiki", "portal", "console")):
        tags.append("human_project_reading")
    if any(token in name for token in ("context", "task", "impact", "reading", "handoff")):
        tags.append("coding_agent_task_context")
    if any(token in name for token in ("architecture", "relationship", "evidence", "trace", "ranking")):
        tags.append("architecture_review")
    if any(token in name for token in ("quality", "governance", "feedback", "rule")):
        tags.append("governance_loop")
    return sorted(set(tags or ["general_usage"]))


def _expected_outputs(name: str) -> list[str]:
    if name.endswith("_build") or name.endswith("build") or "snapshot" in name:
        return ["persisted_artifact", "artifact_refs"]
    if name.endswith("_read") or name.endswith("read"):
        return ["artifact_payload", "artifact_refs"]
    if "view" in name or "portal" in name:
        return ["rendered_view", "artifact_refs"]
    return ["structured_payload"]


def _failure_modes(name: str) -> list[str]:
    modes = ["missing_workspace", "missing_codebase"]
    if any(token in name for token in ("build", "snapshot", "profile", "architecture")):
        modes.append("source_artifact_missing")
    if any(token in name for token in ("provider", "runtime")):
        modes.append("provider_or_runtime_unavailable")
    if any(token in name for token in ("context", "task", "impact")):
        modes.append("insufficient_evidence_or_token_budget")
    return sorted(set(modes))


def _build_workflows(workspace_id: str, codebase_id: str, tool_names: set[str], refs: list[dict[str, str]]) -> dict[str, Any]:
    workflow_specs = [
        ("project_reading", "项目阅读与摘要", ["knowledge_codebase_import", "knowledge_codebase_snapshot", "knowledge_project_inventory", "knowledge_project_overview"]),
        ("architecture_review", "架构证据审计", ["knowledge_code_architecture_evidence_v2_build", "knowledge_code_architecture_relationships_v2_build", "knowledge_code_architecture_human_report_v2_build", "knowledge_code_architecture_context_pack_v3"]),
        ("coding_task_context", "开发任务上下文", ["knowledge_code_task_navigation_prepare", "knowledge_code_impact_analyze", "knowledge_code_module_reading_pack", "knowledge_agent_context_pack"]),
        ("governance_review", "文档代码治理", ["knowledge_code_architecture_doc_view", "knowledge_code_platform_governance_feedback", "knowledge_code_platform_governance_rules_build", "knowledge_code_platform_governance_overlay"]),
    ]
    unresolved = []
    workflows = []
    for workflow_id, title, chain in workflow_specs:
        steps = []
        for index, tool in enumerate(chain, start=1):
            status = "available" if tool in tool_names else "missing"
            if status == "missing":
                unresolved.append({"workflow_id": workflow_id, "tool_name": tool, "reason": "tool_not_registered"})
            steps.append(
                {
                    "step_index": index,
                    "tool_name": tool,
                    "status": status,
                    "purpose": _purpose(tool),
                    "required_inputs": ["workspace_id", "codebase_id"],
                    "expected_outputs": _expected_outputs(tool),
                    "failure_modes": _failure_modes(tool),
                }
            )
        workflows.append({"workflow_id": workflow_id, "title": title, "steps": steps})
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "artifact_type": "mcp_agent_workflows",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "generated_at": now(),
        "workflow_count": len(workflows),
        "workflows": workflows,
        "unresolved": unresolved,
        "artifact_refs": refs,
    }


def _purpose(tool: str) -> str:
    if "import" in tool:
        return "register project before reading artifacts"
    if "snapshot" in tool:
        return "refresh deterministic file facts"
    if "overview" in tool or "inventory" in tool:
        return "read project summary and public surface facts"
    if "context" in tool or "task" in tool or "impact" in tool:
        return "prepare bounded coding-agent context"
    if "governance" in tool or "quality" in tool:
        return "review and govern evidence-backed findings"
    return "read or build evidence-backed project artifact"


def _build_usage_guide(workspace_id: str, codebase_id: str, catalog: dict[str, Any], workflows: dict[str, Any], refs: list[dict[str, str]]) -> dict[str, Any]:
    missing = list(workflows.get("unresolved") or [])
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "artifact_type": "mcp_usage_guide",
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "generated_at": now(),
        "codex_cli": {
            "server_name": "data_service",
            "recommended_command": "python -m data_service.mcp_stdio",
            "configuration_note": "Register data_service as an MCP stdio server, then call the listed tools before broad code reading.",
        },
        "recommended_entry_workflows": [workflow["workflow_id"] for workflow in workflows.get("workflows", [])],
        "validation_summary": {
            "registry_count": int(catalog.get("tool_count") or 0),
            "catalog_count": int(catalog.get("tool_count") or 0),
            "workflow_count": int(workflows.get("workflow_count") or 0),
            "missing_workflow_tool_count": len(missing),
        },
        "failure_policy": [
            "structured unavailable is not accepted implementation evidence",
            "do not treat MCP health as business capability acceptance",
            "every task recommendation must keep evidence_refs or needs_review",
        ],
        "artifact_refs": refs,
    }


def _render_markdown(guide: dict[str, Any], catalog: dict[str, Any], workflows: dict[str, Any]) -> str:
    lines = [
        "# Codex CLI MCP Usage Guide",
        "",
        "## Server",
        "",
        f"- Name: `{guide['codex_cli']['server_name']}`",
        f"- Command: `{guide['codex_cli']['recommended_command']}`",
        "",
        "## Why use this service",
        "",
        "Use the MCP tools before broad repository reading to get project overview, public surfaces, architecture evidence, task context, and governance findings with artifact references.",
        "",
        "## Tool catalog",
        "",
        f"- Tool count: {catalog.get('tool_count', 0)}",
        f"- Group count: {len(catalog.get('groups', []))}",
        "",
        "## Recommended workflows",
        "",
    ]
    for workflow in workflows.get("workflows", []):
        lines.append(f"### {workflow['title']}")
        lines.append("")
        for step in workflow.get("steps", []):
            lines.append(f"{step['step_index']}. `{step['tool_name']}` - {step['purpose']} ({step['status']})")
        lines.append("")
    lines.extend(
        [
            "## Failure handling",
            "",
            "- If a project path is unavailable, keep the result as structured unavailable.",
            "- If a tool is missing from registry, do not mark the workflow accepted.",
            "- If a recommendation lacks evidence, mark it needs_review.",
            "",
        ]
    )
    return "\n".join(lines)

