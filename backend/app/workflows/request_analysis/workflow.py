from __future__ import annotations

from typing import Any, Dict, List

from app.orchestrator.planner import analyze_request_text

from ..common import issue

KNOWN_STAGES = {
    "request_analysis",
    "evidence_ingestion",
    "domain_grounding",
    "instructional_modeling",
    "simulation_design",
    "runtime_package_assembly",
    "code_generation",
    "runtime_validation",
}


def build_artifact(_: Dict[str, Dict[str, Any]], state: Dict[str, Any], __: Dict[str, Any]) -> Dict[str, Any]:
    analysis = analyze_request_text(state["request_text"])
    return {
        **analysis,
        "has_explicit_problem": True,
        "has_explicit_solution": analysis["input_profile"] == "problem_with_solution",
    }


def validate_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for key in [
        "request_mode",
        "input_profile",
        "information_density",
        "has_existing_simulation",
        "recommended_plan",
    ]:
        if candidate.get(key) in (None, "", []):
            issues.append(issue("MISSING_FIELD", f"Missing request analysis field `{key}`.", key))
    plan = candidate.get("recommended_plan") or []
    if not isinstance(plan, list) or not plan:
        issues.append(issue("INVALID_PLAN", "recommended_plan must be a non-empty list.", "recommended_plan"))
    for stage in plan:
        if stage not in KNOWN_STAGES:
            issues.append(issue("UNKNOWN_STAGE", f"Unknown stage `{stage}` in recommended_plan.", "recommended_plan"))
    if candidate.get("request_mode") == "revision_existing_simulation" and not candidate.get("has_existing_simulation"):
        issues.append(issue("INVALID_REVISION", "Revision mode requires existing simulation context.", "request_mode"))
    return issues


def repair_artifact(
    _: Dict[str, Any],
    __: List[Dict[str, Any]],
    ___: Dict[str, Dict[str, Any]],
    state: Dict[str, Any],
    ____: Dict[str, Any],
) -> Dict[str, Any]:
    return build_artifact({}, state, {})


def approve_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    plan = candidate.get("recommended_plan") or []
    if plan and plan[0] != "request_analysis":
        return [issue("PLAN_ORDER", "Workflow plan must start at request_analysis.", "recommended_plan")]
    return []
