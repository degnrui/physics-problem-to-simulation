from typing import Any, Dict


def build_simulation_blueprint(
    planner: Dict[str, Any],
    problem_profile: Dict[str, Any],
    physics_model: Dict[str, Any],
    scene_spec: Dict[str, Any],
    simulation_spec: Dict[str, Any],
) -> Dict[str, Any]:
    benchmark_capabilities = {
        "main_canvas": True,
        "linked_force_or_state_chart": True,
        "linked_energy_chart": True,
        "playback_timeline": True,
        "parameter_controls": True,
        "visual_toggles": True,
        "teacher_guidance": True,
        "option_diagnosis": True,
    }
    return {
        "delivery_mode": "interactive-teaching-demo",
        "problem_family": planner["problem_family"],
        "model_family": planner["model_family"],
        "template_id": simulation_spec["template_id"],
        "scene_type": scene_spec["scene_type"],
        "teaching_goal": physics_model.get("knowledge_points", []),
        "interaction_contract": {
            "controls": simulation_spec["controls"],
            "bindings": simulation_spec["bindings"],
        },
        "render_priority": [
            "main simulation viewport",
            "linked charts",
            "playback and seek controls",
            "parameter control panel",
            "visual toggle panel",
            "teacher explanation panel",
            "option analysis panel",
        ],
        "minimum_quality_bar": {
            "interactive_controls": True,
            "time_playback": True,
            "linked_charts": True,
            "teacher_guidance": True,
            "option_diagnosis": True,
        },
        "benchmark_capabilities": benchmark_capabilities,
        "research_object": problem_profile["research_object"],
    }


def build_renderer_payload(
    planner: Dict[str, Any],
    scene_spec: Dict[str, Any],
    simulation_spec: Dict[str, Any],
    teaching_plan: Dict[str, Any],
) -> Dict[str, Any]:
    component_key = "force-scene-preview"
    if planner["model_family"] == "projectile-motion":
        component_key = "projectile-board-impact"
    if planner["model_family"] == "symmetric-elastic-motion":
        component_key = "elastic-restoring-motion"

    return {
        "component_key": component_key,
        "layout_mode": "simulation-lab",
        "design_system": {
            "theme_key": "impeccable-lab",
            "density": "comfortable",
            "tone": "teaching-exhibition",
            "surface_style": "precision-paper",
        },
        "composition": {
            "workspace": "hero-input + simulation-workspace + inspector",
            "simulation": "main-canvas + linked-charts + controls + teaching-panels",
            "inspector": "summary + artifacts + validation + logs",
            "sidebar": "teacher-guidance + option-diagnosis + key-relations",
        },
        "surface_priority": [
            "problem-input",
            "simulation-workspace",
            "teaching-sidebar",
            "inspector",
        ],
        "hero_panel": {
            "title": "Physics Problem to Simulation",
            "eyebrow": "Teacher Workbench",
            "subtitle": "把物理题转成可讲授、可演示、可验证的教学 simulation 成品。",
        },
        "scene_spec": scene_spec,
        "simulation_spec": simulation_spec,
        "teaching_plan": teaching_plan,
    }


def build_delivery_bundle(
    blueprint: Dict[str, Any],
    renderer_payload: Dict[str, Any],
    teaching_plan: Dict[str, Any],
) -> Dict[str, Any]:
    panel_contract = {
        "simulation_canvas": {
            "required": True,
            "content": "main motion viewport with vectors and geometry state",
        },
        "linked_charts": {
            "required": True,
            "content": ["force-displacement", "energy-time"],
        },
        "parameter_controls": {
            "required": True,
            "content": "sliders and scenario parameters defined by simulation_spec.controls",
        },
        "playback_panel": {
            "required": True,
            "content": "play pause reset seek and speed controls",
        },
        "teacher_guidance": {
            "required": True,
            "content": "teacher prompts and observation targets",
        },
        "option_diagnosis": {
            "required": True,
            "content": "choice analysis or claim verification panel",
        },
    }
    return {
        "primary_view": "simulation-viewport",
        "secondary_views": [
            "linked-charts",
            "playback-panel",
            "parameter-controls",
            "teacher-guidance",
            "option-diagnosis",
            "task-log",
            "physics-model",
            "validation-report",
        ],
        "renderer_payload": renderer_payload,
        "blueprint_summary": blueprint,
        "teacher_script": teaching_plan["teacher_prompts"],
        "observation_targets": teaching_plan["observation_targets"],
        "panel_contract": panel_contract,
        "inspector_contract": {
            "summary": ["primary_goal", "classroom_use", "interaction_strategy"],
            "artifacts": ["problem_profile", "physics_model", "teaching_plan", "scene_spec", "simulation_spec"],
            "validation": ["validation_report", "blueprint_summary"],
            "logs": ["task_log"],
        },
        "artifact_tabs": [
            {"id": "summary", "label": "Summary"},
            {"id": "artifacts", "label": "Artifacts"},
            {"id": "validation", "label": "Validation"},
            {"id": "logs", "label": "Logs"},
        ],
        "default_open_panels": [
            "simulation_canvas",
            "parameter_controls",
            "teacher_guidance",
            "option_diagnosis",
        ],
        "teaching_sidebar": {
            "sections": ["teacher_script", "observation_targets", "option_diagnosis", "key_relations"],
            "tone": "teacher-facing",
        },
    }
