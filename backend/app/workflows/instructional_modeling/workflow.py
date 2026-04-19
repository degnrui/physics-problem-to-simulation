from __future__ import annotations

from typing import Any, Dict, List

from ..common import issue, required_fields


def build_artifact(inputs: Dict[str, Dict[str, Any]], _: Dict[str, Any], __: Dict[str, Any]) -> Dict[str, Any]:
    domain_grounding = inputs["domain_grounding"]
    request_analysis = inputs["request_analysis"]
    domain_type = domain_grounding["domain_type"]
    return {
        "learning_goals": [f"Explain the key {domain_type} relationships with observable evidence."],
        "observation_priorities": [equation for equation in domain_grounding["canonical_equations"][:2]],
        "misconception_plan": ["Separate force description from motion outcome."],
        "interaction_priorities": ["manipulate one parameter at a time", "compare runtime response with the chart"],
        "audience_mode": "teacher_and_student" if request_analysis["request_mode"] == "new_simulation" else "revision_review",
    }


def validate_artifact(candidate: Dict[str, Any], inputs: Dict[str, Dict[str, Any]], _: Dict[str, Any], __: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for key in required_fields(__, ["learning_goals", "observation_priorities", "misconception_plan", "interaction_priorities", "audience_mode"]):
        if candidate.get(key) in (None, "", [], {}):
            issues.append(issue("MISSING_FIELD", f"Missing instructional field `{key}`.", key))
    approved_equations = " ".join(inputs["domain_grounding"].get("canonical_equations", []))
    for observation in candidate.get("observation_priorities", []):
        if observation not in approved_equations and observation not in inputs["domain_grounding"].get("canonical_equations", []):
            issues.append(issue("UNGROUNDED_PRIORITY", f"Observation `{observation}` is not grounded.", "observation_priorities"))
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
    if not candidate.get("observation_priorities"):
        return [issue("NO_PRIORITIES", "Instructional modeling requires observation priorities.", "observation_priorities")]
    return []
