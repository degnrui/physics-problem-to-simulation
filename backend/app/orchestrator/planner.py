from __future__ import annotations

from typing import Any, Dict, List


def _has_solution(text: str) -> bool:
    lowered = text.lower()
    return any(token in lowered for token in ["答案", "解析", "solution", "answer"])


def _has_existing_simulation(text: str) -> bool:
    lowered = text.lower()
    return any(
        token in lowered
        for token in [
            "已有 simulation",
            "existing simulation",
            "在已有",
            "保留原有",
            "revise",
            "modify",
            "修改",
        ]
    )


def analyze_request_text(text: str) -> Dict[str, Any]:
    has_existing_simulation = _has_existing_simulation(text)
    request_mode = "revision_existing_simulation" if has_existing_simulation else "new_simulation"
    information_density = "high" if len(text.strip()) >= 60 else "low"
    input_profile = "problem_with_solution" if _has_solution(text) else "problem_only"
    recommended_plan: List[str] = ["request_analysis"]
    if information_density == "low":
        recommended_plan.append("evidence_ingestion")
    recommended_plan.extend(
        [
            "domain_grounding",
            "instructional_modeling",
            "simulation_design",
            "runtime_package_assembly",
            "code_generation",
            "runtime_validation",
        ]
    )
    return {
        "request_mode": request_mode,
        "input_profile": input_profile,
        "information_density": information_density,
        "has_existing_simulation": has_existing_simulation,
        "recommended_plan": recommended_plan,
    }
