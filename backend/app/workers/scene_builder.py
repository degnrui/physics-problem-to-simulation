from typing import Any, Dict

from app.domain.problem import ProblemInput
from app.pipeline.problem_to_simulation import run_problem_to_simulation


def _projectile_scene_spec(
    problem_profile: Dict[str, Any],
    physics_model: Dict[str, Any],
    teaching_plan: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "scene_type": "projectile-motion",
        "template_id": "projectile-board-impact-v1",
        "visual_elements": [
            {"type": "ramp", "id": "ramp", "label": "斜面"},
            {"type": "table-edge", "id": "table-edge", "label": "桌边"},
            {"type": "projectile", "id": "ball", "label": "钢球"},
            {"type": "target-board", "id": "board", "label": "可调木板"},
            {"type": "trajectory", "id": "trajectory", "label": "平抛轨迹"},
            {"type": "impact-vector", "id": "impact-vector", "label": "撞击速度"},
        ],
        "controls": [
            {"type": "slider", "id": "h", "label": "木板高度 h", "min": 0.2, "max": 2.5, "step": 0.1},
            {"type": "toggle", "id": "show-formulas", "label": "显示公式面板", "default": True},
            {"type": "toggle", "id": "show-vectors", "label": "显示速度矢量", "default": True},
            {"type": "button", "id": "replay", "label": "重播"},
        ],
        "parameters": {
            "simulation_mode": problem_profile["simulation_mode"],
            "derived_quantities": physics_model["derived_quantities"],
            "knowledge_points": physics_model["knowledge_points"],
            "option_analysis": physics_model["option_analysis"],
        },
        "notes": [
            "通过拖动 h 观察飞行时间、落点与撞击速度方向变化。",
        ],
        "teaching_overlay": {
            "observation_targets": teaching_plan["observation_targets"],
            "teacher_prompts": teaching_plan["teacher_prompts"],
        },
    }


def _elastic_scene_spec(
    problem_profile: Dict[str, Any],
    physics_model: Dict[str, Any],
    teaching_plan: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "scene_type": "elastic-motion",
        "template_id": "elastic-restoring-motion-v1",
        "visual_elements": [
            {"type": "anchor", "id": "A", "label": "A"},
            {"type": "anchor", "id": "B", "label": "B"},
            {"type": "marker", "id": "C", "label": "C"},
            {"type": "marker", "id": "O", "label": "O"},
            {"type": "block", "id": "block", "label": "物块"},
            {"type": "elastic-band", "id": "band-1", "label": "上橡皮绳"},
            {"type": "elastic-band", "id": "band-2", "label": "下橡皮绳"},
            {"type": "force-vector", "id": "restoring-force", "label": "回复力"},
            {"type": "force-vector", "id": "friction-force", "label": "摩擦力"},
        ],
        "controls": [
            {"type": "slider", "id": "L", "label": "初始拉开距离 L", "min": 0.2, "max": 2.5, "step": 0.1},
            {"type": "slider", "id": "mu", "label": "动摩擦因数 μ", "min": 0, "max": 0.8, "step": 0.05},
            {"type": "toggle", "id": "show-force-decomposition", "label": "显示力分解", "default": True},
            {"type": "toggle", "id": "show-energy-panel", "label": "显示功能量面板", "default": True},
            {"type": "button", "id": "release", "label": "释放"},
        ],
        "parameters": {
            "simulation_mode": problem_profile["simulation_mode"],
            "derived_quantities": physics_model["derived_quantities"],
            "knowledge_points": physics_model["knowledge_points"],
            "option_analysis": physics_model["option_analysis"],
        },
        "notes": [
            "通过拖动 L 和 μ 观察回复力、速度和功能量变化。",
        ],
        "teaching_overlay": {
            "observation_targets": teaching_plan["observation_targets"],
            "teacher_prompts": teaching_plan["teacher_prompts"],
        },
    }


def _force_scene_spec(
    problem_profile: Dict[str, Any],
    teaching_plan: Dict[str, Any],
) -> Dict[str, Any]:
    text = problem_profile["summary"]
    pipeline_result = run_problem_to_simulation(
        ProblemInput(text=text, topic_hint="force-analysis")
    )
    scene = pipeline_result.scene
    return {
        "scene_type": scene["scene_type"],
        "template_id": scene["template_id"],
        "visual_elements": scene["visual_elements"],
        "controls": scene["controls"],
        "parameters": scene["parameters"],
        "notes": scene["notes"],
        "teaching_overlay": {
            "observation_targets": teaching_plan["observation_targets"],
            "teacher_prompts": teaching_plan["teacher_prompts"],
        },
    }


def build_scene_spec(
    problem_profile: Dict[str, Any],
    physics_model: Dict[str, Any],
    teaching_plan: Dict[str, Any],
) -> Dict[str, Any]:
    family = problem_profile["model_family"]
    if family == "projectile-motion":
        return _projectile_scene_spec(problem_profile, physics_model, teaching_plan)
    if family == "symmetric-elastic-motion":
        return _elastic_scene_spec(problem_profile, physics_model, teaching_plan)
    return _force_scene_spec(problem_profile, teaching_plan)


def build_simulation_spec(
    scene_spec: Dict[str, Any],
    teaching_plan: Dict[str, Any],
) -> Dict[str, Any]:
    renderer_mode = "parameterized-motion-preview"
    if scene_spec["scene_type"] == "force-analysis":
        renderer_mode = "stage-switching-preview"
    return {
        "template_id": scene_spec["template_id"],
        "renderer_mode": renderer_mode,
        "bindings": scene_spec["parameters"],
        "controls": scene_spec["controls"],
        "teaching_mode": teaching_plan["classroom_use"],
    }
