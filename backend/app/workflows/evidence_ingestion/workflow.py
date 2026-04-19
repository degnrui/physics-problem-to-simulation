from __future__ import annotations

from typing import Any, Dict, List

from ..common import issue, required_fields, split_sentences


def build_artifact(_: Dict[str, Dict[str, Any]], state: Dict[str, Any], __: Dict[str, Any]) -> Dict[str, Any]:
    evidence = split_sentences(state["request_text"])
    return {
        "completion_status": "completed",
        "evidence_items": [{"id": f"evidence-{index}", "text": text, "source": "request"} for index, text in enumerate(evidence, start=1)],
        "source_inventory": [{"kind": "text", "count": len(evidence)}],
        "missing_evidence": [],
    }


def validate_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for key in required_fields(___, ["completion_status", "evidence_items", "source_inventory", "missing_evidence"]):
        if key != "evidence_items" and candidate.get(key) in (None, "", [], {}):
            issues.append(issue("MISSING_FIELD", f"Missing evidence field `{key}`.", key))
    if candidate.get("completion_status") not in {"completed", "skipped"}:
        issues.append(issue("INVALID_STATUS", "completion_status must be completed or skipped.", "completion_status"))
    if candidate.get("completion_status") == "completed" and not candidate.get("evidence_items"):
        issues.append(issue("EMPTY_EVIDENCE", "Completed evidence ingestion requires evidence_items.", "evidence_items"))
    if candidate.get("source_inventory") in (None, []):
        issues.append(issue("MISSING_SOURCES", "source_inventory is required.", "source_inventory"))
    return issues


def repair_artifact(
    candidate: Dict[str, Any],
    _: List[Dict[str, Any]],
    __: Dict[str, Dict[str, Any]],
    state: Dict[str, Any],
    ___: Dict[str, Any],
) -> Dict[str, Any]:
    if candidate.get("completion_status") == "completed" and candidate.get("evidence_items"):
        return {
            **candidate,
            "source_inventory": candidate.get("source_inventory") or [{"kind": "text", "count": len(candidate["evidence_items"])}],
        }
    return build_artifact({}, state, {})


def approve_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    if candidate.get("completion_status") == "completed" and not candidate.get("source_inventory"):
        return [issue("UNUSABLE_EVIDENCE", "Evidence bundle is missing source inventory.", "source_inventory")]
    return []
