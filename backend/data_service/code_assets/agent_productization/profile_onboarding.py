"""Project profile onboarding draft generation for V2.47."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from pathlib import Path
from typing import Any

from data_service.mcp_common import now

from ..registry import CodebaseRegistry
from .mcp_usage import AGENT_PRODUCTIZATION_SCHEMA_VERSION
from .persistence import (
    profile_onboarding_artifact_refs,
    read_authority_rule_suggestions,
    read_no_hardcode_audit,
    read_path_pattern_suggestions,
    read_profile_draft,
    read_taxonomy_suggestions,
    write_profile_onboarding,
)


PRODUCTION_HARDCODE_SCAN_PATHS = [
    "backend/data_service/code_assets/agent_productization",
    "backend/data_service/code_assets/architecture",
    "backend/data_service/mcp_code_agent_productization_tools.py",
    "backend/data_service/cli_code_agent_productization.py",
    "backend/app/api/v1/code_assets_agent_productization.py",
]

SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}

DOC_SUFFIXES = {".md", ".mdx", ".rst", ".txt", ".drawio"}
SOURCE_DIR_CANDIDATES = {"src", "backend", "frontend", "app", "apps", "packages", "lib", "server", "client"}
TEST_DIR_CANDIDATES = {"test", "tests", "spec", "specs", "__tests__"}
CONFIG_NAMES = {"pyproject.toml", "package.json", "pnpm-workspace.yaml", "tsconfig.json", "vite.config.ts", "docker-compose.yml", "Dockerfile", "Makefile"}
GENERIC_TERMS = {"repo", "project", "service", "data_service", "backend", "frontend", "source", "codebase", "workspace", "python", "typescript", "javascript"}


class AgentProfileOnboardingService:
    def __init__(self, workspace: Path, *, workspace_id: str) -> None:
        self.workspace = workspace
        self.workspace_id = workspace_id
        self.registry = CodebaseRegistry(workspace, workspace_id=workspace_id)

    def build_profile_onboarding(self, codebase_id: str) -> dict[str, Any]:
        asset = self.registry.describe(codebase_id)
        refs = profile_onboarding_artifact_refs(codebase_id)
        created_at = now()
        repo_root = Path(asset.root_path).expanduser()
        if not repo_root.exists() or not repo_root.is_dir():
            payload = _unavailable_payload(
                workspace_id=self.workspace_id,
                codebase_id=codebase_id,
                project_name=asset.name,
                refs=refs,
                created_at=created_at,
            )
            write_profile_onboarding(
                self.workspace,
                codebase_id,
                payload["profile_draft"],
                payload["taxonomy_suggestions"],
                payload["authority_rule_suggestions"],
                payload["path_pattern_suggestions"],
                payload["no_hardcode_audit"],
            )
            return payload

        doc_assets = _discover_doc_assets(repo_root)
        top_level = _top_level_entries(repo_root)
        path_patterns = _path_patterns(repo_root, top_level)
        taxonomy = _taxonomy_suggestions(self.workspace_id, codebase_id, asset.name, doc_assets, top_level, created_at)
        authority = _authority_rule_suggestions(self.workspace_id, codebase_id, doc_assets, created_at)
        paths = _path_pattern_suggestions(self.workspace_id, codebase_id, path_patterns, created_at)
        forbidden_terms = _project_specific_terms(asset.name, repo_root.name)
        no_hardcode = _no_hardcode_audit(self.workspace_id, codebase_id, forbidden_terms, created_at)
        profile = _profile_draft(
            workspace_id=self.workspace_id,
            codebase_id=codebase_id,
            project_name=asset.name or repo_root.name,
            doc_assets=doc_assets,
            path_patterns=path_patterns,
            taxonomy=taxonomy,
            authority=authority,
            no_hardcode=no_hardcode,
            refs=refs,
            created_at=created_at,
        )
        write_profile_onboarding(self.workspace, codebase_id, profile, taxonomy, authority, paths, no_hardcode)
        return _bundle(self.workspace_id, codebase_id, profile, taxonomy, authority, paths, no_hardcode, refs)

    def read_profile_onboarding(self, codebase_id: str) -> dict[str, Any]:
        self.registry.describe(codebase_id)
        refs = profile_onboarding_artifact_refs(codebase_id)
        profile = read_profile_draft(self.workspace, codebase_id)
        taxonomy = read_taxonomy_suggestions(self.workspace, codebase_id)
        authority = read_authority_rule_suggestions(self.workspace, codebase_id)
        paths = read_path_pattern_suggestions(self.workspace, codebase_id)
        no_hardcode = read_no_hardcode_audit(self.workspace, codebase_id)
        return _bundle(self.workspace_id, codebase_id, profile, taxonomy, authority, paths, no_hardcode, refs)


def public_profile_onboarding_payload(payload: dict[str, Any]) -> dict[str, Any]:
    profile = dict(payload.get("profile_draft") or {})
    taxonomy = dict(payload.get("taxonomy_suggestions") or {})
    authority = dict(payload.get("authority_rule_suggestions") or {})
    paths = dict(payload.get("path_pattern_suggestions") or {})
    audit = dict(payload.get("no_hardcode_audit") or {})
    profile["doc_assets"] = list(profile.get("doc_assets") or [])[:50]
    taxonomy["suggestions"] = list(taxonomy.get("suggestions") or [])[:50]
    authority["rules"] = list(authority.get("rules") or [])[:50]
    paths["patterns"] = list(paths.get("patterns") or [])[:50]
    audit["findings"] = list(audit.get("findings") or [])[:50]
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "artifact_type": "project_profile_onboarding",
        "profile_draft": profile,
        "taxonomy_suggestions": taxonomy,
        "authority_rule_suggestions": authority,
        "path_pattern_suggestions": paths,
        "no_hardcode_audit": audit,
        "summary": dict(payload.get("summary") or {}),
        "artifact_refs": list(payload.get("artifact_refs") or []),
        "warnings": list(payload.get("warnings") or []),
        "unresolved": list(payload.get("unresolved") or []),
    }


def _bundle(
    workspace_id: str,
    codebase_id: str,
    profile: dict[str, Any],
    taxonomy: dict[str, Any],
    authority: dict[str, Any],
    paths: dict[str, Any],
    no_hardcode: dict[str, Any],
    refs: list[dict[str, str]],
) -> dict[str, Any]:
    unresolved = list(profile.get("unresolved") or [])
    warnings = []
    if no_hardcode.get("status") == "failed":
        warnings.append("no_hardcode_audit_failed")
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "profile_draft": profile,
        "taxonomy_suggestions": taxonomy,
        "authority_rule_suggestions": authority,
        "path_pattern_suggestions": paths,
        "no_hardcode_audit": no_hardcode,
        "summary": {
            "profile_status": profile.get("profile_status"),
            "doc_asset_count": len(profile.get("doc_assets") or []),
            "taxonomy_suggestion_count": len(taxonomy.get("suggestions") or []),
            "authority_rule_count": len(authority.get("rules") or []),
            "path_pattern_count": len(paths.get("patterns") or []),
            "no_hardcode_status": no_hardcode.get("status"),
        },
        "artifact_refs": refs,
        "warnings": warnings,
        "unresolved": unresolved,
        "next_actions": ["knowledge_code_agent_productization_profile_read"],
    }


def _unavailable_payload(
    *,
    workspace_id: str,
    codebase_id: str,
    project_name: str,
    refs: list[dict[str, str]],
    created_at: str,
) -> dict[str, Any]:
    base = _base(workspace_id, codebase_id, created_at)
    unresolved = [{"code": "PROJECT_REPO_UNAVAILABLE", "reason": "registered codebase root is missing or not a directory"}]
    profile = {
        **base,
        "artifact_type": "profile_draft",
        "profile_id": _stable_id("profile", codebase_id, project_name),
        "profile_status": "structured_unavailable",
        "project_name": project_name or codebase_id,
        "doc_assets": [],
        "path_patterns": [],
        "authority_summary": {},
        "taxonomy_summary": {},
        "unresolved": unresolved,
        "artifact_refs": refs,
    }
    empty = {**base, "status": "structured_unavailable", "unresolved": unresolved, "artifact_refs": refs}
    return _bundle(
        workspace_id,
        codebase_id,
        profile,
        {**empty, "artifact_type": "taxonomy_suggestions", "suggestions": []},
        {**empty, "artifact_type": "authority_rule_suggestions", "rules": []},
        {**empty, "artifact_type": "path_pattern_suggestions", "patterns": []},
        {**empty, "artifact_type": "no_hardcode_audit", "status": "not_run", "findings": []},
        refs,
    )


def _profile_draft(
    *,
    workspace_id: str,
    codebase_id: str,
    project_name: str,
    doc_assets: list[dict[str, Any]],
    path_patterns: list[dict[str, Any]],
    taxonomy: dict[str, Any],
    authority: dict[str, Any],
    no_hardcode: dict[str, Any],
    refs: list[dict[str, str]],
    created_at: str,
) -> dict[str, Any]:
    return {
        **_base(workspace_id, codebase_id, created_at),
        "artifact_type": "profile_draft",
        "profile_id": _stable_id("profile", codebase_id, project_name),
        "profile_status": "draft",
        "project_name": project_name,
        "doc_assets": doc_assets,
        "path_patterns": path_patterns,
        "taxonomy_summary": {
            "suggestion_count": len(taxonomy.get("suggestions") or []),
            "top_terms": [item["term"] for item in list(taxonomy.get("suggestions") or [])[:10]],
        },
        "authority_summary": {
            "rule_count": len(authority.get("rules") or []),
            "primary_document_count": sum(1 for item in authority.get("rules", []) if item.get("authority_level") == "primary"),
        },
        "no_hardcode_status": no_hardcode.get("status"),
        "unresolved": [],
        "artifact_refs": refs,
    }


def _discover_doc_assets(repo_root: Path) -> list[dict[str, Any]]:
    docs: list[dict[str, Any]] = []
    for file_path in _iter_files(repo_root, limit=1200):
        rel = _rel(repo_root, file_path)
        name = file_path.name
        if file_path.suffix.lower() in DOC_SUFFIXES or name.lower().startswith("readme"):
            docs.append(
                {
                    "path": rel,
                    "doc_type": _doc_type(rel),
                    "authority_role": _authority_role(rel),
                    "authority_level": _authority_level(rel),
                    "evidence_refs": [f"repo://{rel}"],
                }
            )
        if len(docs) >= 300:
            break
    return sorted(docs, key=lambda item: (str(item.get("authority_level")), str(item.get("path"))))


def _top_level_entries(repo_root: Path) -> list[str]:
    entries = []
    try:
        for item in repo_root.iterdir():
            if item.name in SKIP_DIRS:
                continue
            entries.append(item.name)
    except OSError:
        return []
    return sorted(entries)[:100]


def _path_patterns(repo_root: Path, top_level: list[str]) -> list[dict[str, Any]]:
    patterns: list[dict[str, Any]] = []
    for name in top_level:
        path = repo_root / name
        if path.is_dir() and name.lower() == "docs":
            patterns.append(_pattern("docs", "docs/**", "documentation_assets", name))
        elif path.is_dir() and name in SOURCE_DIR_CANDIDATES:
            patterns.append(_pattern("source", f"{name}/**", "source_candidate", name))
        elif path.is_dir() and name.lower() in TEST_DIR_CANDIDATES:
            patterns.append(_pattern("tests", f"{name}/**", "test_candidate", name))
        elif path.is_dir() and name in {"dist", "build", "generated"}:
            patterns.append(_pattern("generated", f"{name}/**", "generated_candidate", name))
        elif path.is_file() and name in CONFIG_NAMES:
            patterns.append(_pattern("config", name, "config_candidate", name))
    if not patterns:
        patterns.append(_pattern("repo_root", "*", "generic_repo_root", "."))
    return patterns


def _pattern(pattern_id: str, glob: str, role: str, evidence_path: str) -> dict[str, Any]:
    return {
        "pattern_id": pattern_id,
        "glob": glob,
        "role": role,
        "confidence": 0.75 if pattern_id == "repo_root" else 0.9,
        "evidence_refs": [f"repo://{evidence_path}"],
    }


def _taxonomy_suggestions(
    workspace_id: str,
    codebase_id: str,
    project_name: str,
    doc_assets: list[dict[str, Any]],
    top_level: list[str],
    created_at: str,
) -> dict[str, Any]:
    counter: Counter[str] = Counter()
    for value in [project_name, *top_level]:
        for token in _tokens(value):
            counter[token] += 3
    for doc in doc_assets:
        path = str(doc.get("path") or "")
        for token in _tokens(Path(path).stem):
            counter[token] += 2
        for token in _tokens(path):
            counter[token] += 1
    suggestions = []
    for term, score in counter.most_common(50):
        if term.lower() in GENERIC_TERMS or len(term) < 3:
            continue
        suggestions.append(
            {
                "term": term,
                "term_id": _stable_id("term", codebase_id, term),
                "suggested_role": _suggested_term_role(term),
                "score": score,
                "status": "draft",
                "evidence_refs": _term_evidence(term, doc_assets, top_level),
            }
        )
    return {
        **_base(workspace_id, codebase_id, created_at),
        "artifact_type": "taxonomy_suggestions",
        "status": "draft",
        "suggestions": suggestions,
        "unresolved": [] if suggestions else [{"code": "NO_TAXONOMY_SUGGESTIONS", "reason": "no stable project terms found"}],
    }


def _authority_rule_suggestions(workspace_id: str, codebase_id: str, doc_assets: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    rules = []
    for doc in doc_assets:
        role = str(doc.get("authority_role") or "unknown")
        if role == "unknown":
            continue
        path = str(doc.get("path") or "")
        rules.append(
            {
                "rule_id": _stable_id("authority", codebase_id, path, role),
                "path": path,
                "authority_role": role,
                "authority_level": doc.get("authority_level", "supporting"),
                "status": "draft",
                "evidence_refs": doc.get("evidence_refs") or [f"repo://{path}"],
            }
        )
    return {
        **_base(workspace_id, codebase_id, created_at),
        "artifact_type": "authority_rule_suggestions",
        "status": "draft",
        "rules": rules,
        "unresolved": [] if rules else [{"code": "NO_AUTHORITY_DOCUMENTS_FOUND", "reason": "no PRD/architecture/gap/audit/readme docs found"}],
    }


def _path_pattern_suggestions(workspace_id: str, codebase_id: str, patterns: list[dict[str, Any]], created_at: str) -> dict[str, Any]:
    return {
        **_base(workspace_id, codebase_id, created_at),
        "artifact_type": "path_pattern_suggestions",
        "status": "draft",
        "patterns": patterns,
        "unresolved": [],
    }


def _no_hardcode_audit(workspace_id: str, codebase_id: str, forbidden_terms: list[str], created_at: str) -> dict[str, Any]:
    root = Path.cwd()
    findings = []
    for rel in PRODUCTION_HARDCODE_SCAN_PATHS:
        path = root / rel
        if path.is_dir():
            files = [item for item in path.rglob("*.py") if "__pycache__" not in str(item)]
        elif path.exists():
            files = [path]
        else:
            continue
        for file_path in files:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
            for term in forbidden_terms:
                if term and term in text:
                    findings.append(
                        {
                            "path": str(file_path.relative_to(root)),
                            "term_hash": hashlib.sha256(term.encode("utf-8")).hexdigest()[:12],
                            "term": "<project_specific_term>",
                            "severity": "major",
                        }
                    )
    return {
        **_base(workspace_id, codebase_id, created_at),
        "artifact_type": "no_hardcode_audit",
        "status": "passed" if not findings else "failed",
        "scanned_paths": PRODUCTION_HARDCODE_SCAN_PATHS,
        "forbidden_term_count": len(forbidden_terms),
        "findings": findings,
        "unresolved": [],
    }


def _iter_files(repo_root: Path, *, limit: int) -> list[Path]:
    files: list[Path] = []
    for item in repo_root.rglob("*"):
        if len(files) >= limit:
            break
        if any(part in SKIP_DIRS for part in item.parts):
            continue
        if item.is_file():
            files.append(item)
    return files


def _rel(repo_root: Path, file_path: Path) -> str:
    try:
        return str(file_path.relative_to(repo_root))
    except ValueError:
        return file_path.name


def _doc_type(path: str) -> str:
    lower = path.lower()
    if lower.endswith(".drawio"):
        return "drawio"
    if "prd" in lower:
        return "prd"
    if "architecture" in lower or "架构" in lower:
        return "target_architecture"
    if "gap" in lower:
        return "gap_analysis"
    if "audit" in lower or "审计" in lower:
        return "audit_report"
    if "acceptance" in lower or "验收" in lower:
        return "acceptance_plan"
    if "readme" in lower:
        return "readme"
    return "documentation"


def _authority_role(path: str) -> str:
    doc_type = _doc_type(path)
    return {
        "prd": "target",
        "target_architecture": "target",
        "gap_analysis": "gap",
        "audit_report": "audit_status",
        "acceptance_plan": "acceptance_gate",
        "drawio": "diagram_claim",
        "readme": "overview",
    }.get(doc_type, "supporting")


def _authority_level(path: str) -> str:
    role = _authority_role(path)
    if role == "target":
        return "primary"
    if role in {"acceptance_gate", "audit_status"}:
        return "supporting"
    if role == "diagram_claim":
        return "supporting"
    return "weak"


def _tokens(value: str) -> list[str]:
    raw = re.split(r"[^A-Za-z0-9]+", str(value or ""))
    return [token for token in raw if token and len(token) >= 3]


def _suggested_term_role(term: str) -> str:
    lower = term.lower()
    if lower in {"api", "mcp", "cli", "http"}:
        return "public_surface"
    if lower in {"workflow", "runtime", "agent", "adapter", "provider"}:
        return "architecture_concept"
    if lower in {"test", "tests", "spec"}:
        return "test_concept"
    return "project_term"


def _term_evidence(term: str, doc_assets: list[dict[str, Any]], top_level: list[str]) -> list[str]:
    refs = []
    for name in top_level:
        if term.lower() in name.lower():
            refs.append(f"repo://{name}")
    for doc in doc_assets:
        path = str(doc.get("path") or "")
        if term.lower() in path.lower():
            refs.append(f"repo://{path}")
        if len(refs) >= 5:
            break
    return refs or ["repo://."]


def _project_specific_terms(project_name: str, repo_name: str) -> list[str]:
    candidates = {project_name, repo_name}
    terms = []
    for candidate in candidates:
        value = str(candidate or "").strip()
        if len(value) < 4 or value.lower() in GENERIC_TERMS:
            continue
        terms.append(value)
    return sorted(set(terms))


def _base(workspace_id: str, codebase_id: str, created_at: str) -> dict[str, Any]:
    return {
        "schema_version": AGENT_PRODUCTIZATION_SCHEMA_VERSION,
        "workspace_id": workspace_id,
        "codebase_id": codebase_id,
        "created_at": created_at,
    }


def _stable_id(*parts: str) -> str:
    text = ":".join(str(part or "") for part in parts)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
    prefix = re.sub(r"[^a-z0-9]+", "_", str(parts[0] or "id").lower()).strip("_") or "id"
    return f"{prefix}_{digest}"
