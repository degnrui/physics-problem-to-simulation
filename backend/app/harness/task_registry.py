from typing import Dict, List


def build_task_plan(
    *,
    simulation_ready: bool,
    stage_type: str,
    problem_family: str,
    model_family: str,
    simulation_mode: str,
) -> Dict[str, object]:
    tasks: List[Dict[str, str]] = [
        {"id": "task-1", "type": "problem_profile", "worker": "planner"},
        {"id": "task-2", "type": "physics_model", "worker": "modeler"},
        {"id": "task-3", "type": "teaching_plan", "worker": "pedagogy"},
    ]

    if simulation_ready:
        tasks.extend(
            [
                {"id": "task-4", "type": "scene_spec", "worker": "scene_builder"},
                {"id": "task-5", "type": "simulation_spec", "worker": "scene_builder"},
                {"id": "task-6", "type": "simulation_blueprint", "worker": "renderer"},
                {"id": "task-7", "type": "renderer_payload", "worker": "renderer"},
                {"id": "task-8", "type": "delivery_bundle", "worker": "renderer"},
                {"id": "task-9", "type": "validation_report", "worker": "validator"},
                {"id": "task-10", "type": "teaching_simulation_package", "worker": "orchestrator"},
            ]
        )
    else:
        tasks.extend(
            [
                {"id": "task-4", "type": "validation_report", "worker": "validator"},
                {"id": "task-5", "type": "teaching_analysis_package", "worker": "orchestrator"},
            ]
        )

    return {
        "problem_family": problem_family,
        "model_family": model_family,
        "stage_type": stage_type,
        "simulation_mode": simulation_mode,
        "simulation_ready": simulation_ready,
        "tasks": tasks,
    }
