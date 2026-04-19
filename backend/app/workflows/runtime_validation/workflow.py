from __future__ import annotations

from typing import Any, Dict, List

from ..common import issue


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
    if not candidate.get("primary_file"):
        issues.append(issue("MISSING_PRIMARY_FILE", "runtime_validation requires a primary HTML file.", "primary_file"))
    if "canvas" not in lowered and "simulation viewport" not in lowered:
        issues.append(issue("MISSING_CANVAS", "HTML must contain a canvas or simulation viewport.", "html"))
    for token in ["play", "pause", "reset"]:
        if token not in lowered:
            issues.append(issue("MISSING_CONTROL", f"HTML must contain `{token}` control.", "html"))
    if "measurement-panel" not in lowered and "chart-card" not in lowered and "chart" not in lowered:
        issues.append(issue("MISSING_EVIDENCE_UI", "HTML must contain charts or measurement panels.", "html"))
    if "simulation payload" in lowered or "simulation contract" in lowered or "<pre>" in lowered:
        issues.append(issue("FORBIDDEN_SHELL", "HTML cannot default to report-shell or payload-shell output.", "html"))
    if "type=\"range\"" not in lowered and "type='range'" not in lowered and "select" not in lowered:
        issues.append(issue("MISSING_STATE_CONTROL", "HTML must contain a state-changing control.", "html"))
    return issues


def approve_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [] if candidate.get("html") else [issue("EMPTY_HTML", "Validated runtime cannot be empty.", "html")]
