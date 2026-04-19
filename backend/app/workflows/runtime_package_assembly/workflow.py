from __future__ import annotations

from typing import Any, Dict, List

from ..common import issue


def build_artifact(inputs: Dict[str, Dict[str, Any]], _: Dict[str, Any], __: Dict[str, Any]) -> Dict[str, Any]:
    design = inputs["simulation_design"]
    return {
        "generator_target": "single_file_html_runtime",
        "required_features": ["canvas", "play", "pause", "reset", "measurement-panel"],
        "forbidden_outputs": ["Simulation Contract", "Simulation Payload", "payload dump"],
        "design_spec": design,
    }


def validate_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for key in ["generator_target", "required_features", "forbidden_outputs", "design_spec"]:
        if candidate.get(key) in (None, "", [], {}):
            issues.append(issue("MISSING_FIELD", f"runtime_package_assembly missing `{key}`.", key))
    return issues


def repair_artifact(
    _: Dict[str, Any],
    __: List[Dict[str, Any]],
    inputs: Dict[str, Dict[str, Any]],
    ___: Dict[str, Any],
    ____: Dict[str, Any],
) -> Dict[str, Any]:
    return build_artifact(inputs, {}, {})


def approve_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    if "design_spec" not in candidate or "controls" not in candidate["design_spec"]:
        return [issue("INCOMPLETE_PACKAGE", "runtime package must include the approved design.", "design_spec")]
    return []
