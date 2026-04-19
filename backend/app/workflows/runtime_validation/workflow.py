from __future__ import annotations

from typing import Any, Dict, List

from ..common import contract_value, issue


def build_artifact(inputs: Dict[str, Dict[str, Any]], _: Dict[str, Any], __: Dict[str, Any]) -> Dict[str, Any]:
    generation = inputs["code_generation"]
    primary_file = generation["primary_file"]
    html = generation["files"][primary_file]
    return {
        "primary_file": primary_file,
        "html": html,
    }


def validate_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    html = str(candidate.get("html", ""))
    lowered = html.lower()
    required_controls = contract_value(___, "required_controls", ["play", "pause", "reset"])
    evidence_markers = contract_value(___, "evidence_markers", ["measurement-panel", "chart-card", "chart"])
    forbidden_markers = [marker.lower() for marker in contract_value(___, "forbidden_markers", ["Simulation Payload", "Simulation Contract", "<pre>"])]
    state_control_markers = contract_value(___, "state_control_markers", ['type="range"', "type='range'", "select"])
    if not candidate.get("primary_file"):
        issues.append(issue("MISSING_PRIMARY_FILE", "runtime_validation requires a primary HTML file.", "primary_file"))
    if "canvas" not in lowered and "simulation viewport" not in lowered:
        issues.append(issue("MISSING_CANVAS", "HTML must contain a canvas or simulation viewport.", "html"))
    for token in required_controls:
        if token not in lowered:
            issues.append(issue("MISSING_CONTROL", f"HTML must contain `{token}` control.", "html"))
    if not any(marker.lower() in lowered for marker in evidence_markers):
        issues.append(issue("MISSING_EVIDENCE_UI", "HTML must contain charts or measurement panels.", "html"))
    if any(marker in lowered for marker in forbidden_markers):
        issues.append(issue("FORBIDDEN_SHELL", "HTML cannot default to report-shell or payload-shell output.", "html"))
    if not any(marker.lower() in lowered for marker in state_control_markers):
        issues.append(issue("MISSING_STATE_CONTROL", "HTML must contain a state-changing control.", "html"))
    return issues


def approve_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [] if candidate.get("html") else [issue("EMPTY_HTML", "Validated runtime cannot be empty.", "html")]
