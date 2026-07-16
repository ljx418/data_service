"""OCR provider execution for V2.116."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from .shared import digest_value, file_hash


def provider_health() -> list[dict[str, Any]]:
    providers = []
    for name in ("tesseract", "pdftoppm", "soffice"):
        executable = shutil.which(name)
        version = ""
        if executable:
            try:
                result = subprocess.run([executable, "--version"], capture_output=True, text=True, timeout=5, check=False)
                version = (result.stdout or result.stderr).splitlines()[0][:120] if (result.stdout or result.stderr) else "available"
            except Exception:
                version = "available"
        providers.append(
            {
                "provider_name": name,
                "available": bool(executable),
                "version": version,
                "row_acceptance_status": "accepted" if executable else "structured_unavailable",
            }
        )
    return providers


def execute_ocr_rows(root: Path, anchor_rows: list[dict[str, Any]], workspace_run_dir: Path) -> list[dict[str, Any]]:
    tesseract = shutil.which("tesseract")
    output_dir = workspace_run_dir / "ocr_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for anchor in anchor_rows:
        source_ref = str(anchor["source_ref"])
        media_id = str(anchor["media_id"])
        anchor_text = str(anchor.get("ocr_anchor") or "")
        if not anchor_text:
            rows.append(_provider_row(media_id, [], [], False, "needs_review"))
            continue
        if not tesseract:
            rows.append(_provider_row(media_id, [], [], False, "structured_unavailable"))
            continue
        if not source_ref.startswith("<workspace-root>/"):
            rows.append(_provider_row(media_id, [], [], False, "structured_blocker"))
            continue
        input_path = root / source_ref.removeprefix("<workspace-root>/")
        if input_path.suffix.lower() == ".pdf":
            rows.append(_provider_row(media_id, [], [], False, "structured_unavailable"))
            continue
        if input_path.suffix.lower() in {".ppt", ".pptx"}:
            rows.append(_provider_row(media_id, [], [], False, "structured_unavailable"))
            continue
        output_base = output_dir / media_id
        command = [tesseract, str(input_path), str(output_base), "-l", "eng"]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)
        except subprocess.TimeoutExpired:
            rows.append(_provider_row(media_id, [], [], False, "failed"))
            continue
        output_text_path = output_base.with_suffix(".txt")
        output_text = output_text_path.read_text(encoding="utf-8", errors="replace") if output_text_path.exists() else ""
        anchor_hit = bool(anchor_text and anchor_text in output_text)
        status = "accepted" if result.returncode == 0 and anchor_hit and output_text_path.exists() else "needs_review"
        if result.returncode != 0:
            status = "failed"
        step = {
            "provider_name": "tesseract",
            "provider_version": "detected",
            "command_ref": ["tesseract", "<input>", "<output>", "-l", "eng"],
            "input_ref": source_ref,
            "input_hash": anchor.get("sha256") or "",
            "output_ref": str(output_text_path.relative_to(workspace_run_dir)) if output_text_path.exists() else "",
            "output_hash": file_hash(output_text_path) or "",
            "page_or_slide": 1,
            "language": "eng",
            "resource_limits": {"timeout_seconds": 20},
            "failure_category": "" if result.returncode == 0 else "provider_execution_failed",
        }
        page = {
            "page_or_slide": 1,
            "output_hash": step["output_hash"],
            "anchor_hit": anchor_hit,
            "text_hash": digest_value(output_text, length=64) if output_text else "",
        }
        rows.append(_provider_row(media_id, [step], [page], anchor_hit, status))
    return rows


def _provider_row(
    media_id: str,
    provider_steps: list[dict[str, Any]],
    page_outputs: list[dict[str, Any]],
    anchor_hit: bool,
    row_acceptance_status: str,
) -> dict[str, Any]:
    return {
        "media_id": media_id,
        "provider_steps": provider_steps,
        "page_outputs": page_outputs,
        "anchor_hit": anchor_hit,
        "row_acceptance_status": row_acceptance_status,
    }
