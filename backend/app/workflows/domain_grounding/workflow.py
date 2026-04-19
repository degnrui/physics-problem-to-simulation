from __future__ import annotations

from typing import Any, Dict, List

from ..common import detect_domain_type, issue, split_sentences


def _domain_template(domain_type: str) -> Dict[str, Any]:
    if domain_type == "small_angle_pendulum":
        return {
            "symbol_table": {"T": {"meaning": "period"}, "l": {"meaning": "length"}, "g": {"meaning": "gravity"}},
            "canonical_equations": ["T = 2*pi*sqrt(l/g)"],
            "assumptions": ["small-angle approximation", "massless string"],
        }
    if domain_type == "projectile_motion":
        return {
            "symbol_table": {"x": {"meaning": "horizontal distance"}, "h": {"meaning": "vertical drop"}},
            "canonical_equations": ["x = v0 * t", "h = 0.5 * g * t^2"],
            "assumptions": ["ignore air drag"],
        }
    if domain_type == "restoring_force":
        return {
            "symbol_table": {"F": {"meaning": "restoring force"}, "x": {"meaning": "displacement"}},
            "canonical_equations": ["F_net points toward equilibrium", "energy transfers between elastic and kinetic forms"],
            "assumptions": ["symmetric elastic elements", "friction dissipates energy"],
        }
    return {
        "symbol_table": {"F": {"meaning": "force"}, "m": {"meaning": "mass"}},
        "canonical_equations": ["sum(F) = m*a"],
        "assumptions": ["analyze forces stage by stage"],
    }


def build_artifact(inputs: Dict[str, Dict[str, Any]], state: Dict[str, Any], __: Dict[str, Any]) -> Dict[str, Any]:
    request_text = state["request_text"]
    domain_type = detect_domain_type(request_text)
    domain = _domain_template(domain_type)
    evidence_source = inputs.get("evidence_ingestion", {}).get("evidence_items") or [
        {"id": f"request-{index}", "text": text}
        for index, text in enumerate(split_sentences(request_text), start=1)
    ]
    return {
        "domain_type": domain_type,
        "symbol_table": domain["symbol_table"],
        "canonical_equations": domain["canonical_equations"],
        "assumptions": domain["assumptions"],
        "trustworthy_evidence": evidence_source[:4],
    }


def validate_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for key in ["domain_type", "symbol_table", "canonical_equations", "assumptions", "trustworthy_evidence"]:
        if candidate.get(key) in (None, "", [], {}):
            issues.append(issue("MISSING_FIELD", f"Missing grounding field `{key}`.", key))
    return issues


def repair_artifact(
    candidate: Dict[str, Any],
    _: List[Dict[str, Any]],
    inputs: Dict[str, Dict[str, Any]],
    state: Dict[str, Any],
    __: Dict[str, Any],
) -> Dict[str, Any]:
    fresh = build_artifact(inputs, state, {})
    return {
        "domain_type": candidate.get("domain_type") or fresh["domain_type"],
        "symbol_table": candidate.get("symbol_table") or fresh["symbol_table"],
        "canonical_equations": candidate.get("canonical_equations") or fresh["canonical_equations"],
        "assumptions": candidate.get("assumptions") or fresh["assumptions"],
        "trustworthy_evidence": candidate.get("trustworthy_evidence") or fresh["trustworthy_evidence"],
    }


def approve_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not candidate.get("trustworthy_evidence"):
        return [issue("NO_EVIDENCE", "Domain grounding needs trustworthy evidence.", "trustworthy_evidence")]
    return []
