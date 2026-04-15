from typing import Any, Dict, Optional


def build_validation_report(
    *,
    planner: Dict[str, Any],
    problem_profile: Dict[str, Any],
    physics_model: Dict[str, Any],
    teaching_plan: Dict[str, Any],
    scene_spec: Optional[Dict[str, Any]],
    simulation_spec: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    physics_checks = [
        {
            "name": "has_force_cases",
            "passed": len(physics_model.get("force_cases", [])) > 0,
        },
        {
            "name": "has_research_object",
            "passed": bool(problem_profile.get("research_object")),
        },
    ]
    teaching_checks = [
        {
            "name": "has_observation_targets",
            "passed": len(teaching_plan.get("observation_targets", [])) > 0,
        }
    ]
    template_checks = [
        {
            "name": "scene_template_selected",
            "passed": scene_spec is not None and bool(scene_spec.get("template_id")),
        },
        {
            "name": "simulation_bindings_present",
            "passed": simulation_spec is not None and bool(simulation_spec.get("bindings")),
        },
    ]
    if not planner["simulation_ready"]:
        template_checks = [
            {
                "name": "analysis_only_route",
                "passed": True,
            }
        ]

    ready_for_delivery = all(check["passed"] for check in physics_checks + teaching_checks + template_checks)
    return {
        "ready_for_delivery": ready_for_delivery,
        "route": "simulation" if planner["simulation_ready"] else "analysis-only",
        "physics_checks": physics_checks,
        "teaching_checks": teaching_checks,
        "template_checks": template_checks,
    }
