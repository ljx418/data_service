"""Final gate evaluation for V2.120."""

from __future__ import annotations

from typing import Any

from .shared import worst_status


NON_WAIVABLE_FAILURES = {
    "mixed_run",
    "stale_or_tampered_input",
    "forged_or_invalid_approval",
    "path_escape_guard_bypassed",
    "secret_redaction_failure",
    "child_process_cleanup_failure",
    "artifact_hash_mismatch",
    "schema_validation_failed",
}


def evaluate_gate(artifacts: list[dict[str, Any]], *, schema_errors: list[str], decision_set_ids: list[str], input_manifest_hash: str) -> dict[str, Any]:
    statuses = [str(item.get("artifact_status") or "needs_review") for item in artifacts]
    if schema_errors:
        statuses.append("failed")
    final_status = worst_status(statuses)
    unresolved = []
    for item in artifacts:
        unresolved.extend(list(item.get("unresolved") or []))
    non_waivable = ["schema_validation_failed"] if schema_errors else []
    high_risk_unresolved_count = sum(1 for status in statuses if status != "accepted") + len(unresolved)
    portfolio_final_status = "accepted" if final_status == "accepted" and not non_waivable and high_risk_unresolved_count == 0 else final_status
    return {
        "run_acceptance_status": final_status,
        "implementation_delivery_status": "accepted" if not schema_errors else "failed",
        "portfolio_final_status": portfolio_final_status,
        "artifact_status_priority_applied": statuses,
        "non_waivable_failures": non_waivable,
        "high_risk_unresolved_count": high_risk_unresolved_count,
        "gate_reasons": _gate_reasons(statuses, schema_errors),
        "false_green_rejected": [
            "needs_review/structured_unavailable/structured_blocker/failed not counted as accepted",
            "safe build proposals do not imply external build acceptance",
            "HTML/report presence does not replace headless DOM evidence",
        ],
        "input_manifest_hash": input_manifest_hash,
        "decision_set_ids": decision_set_ids,
    }


def _gate_reasons(statuses: list[str], schema_errors: list[str]) -> list[str]:
    reasons = []
    if schema_errors:
        reasons.append("schema validation failed")
    for status in sorted(set(statuses)):
        if status != "accepted":
            reasons.append(f"{status} evidence remains")
    return reasons or ["all high-risk evidence accepted"]
