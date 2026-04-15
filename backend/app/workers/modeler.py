from typing import Any, Dict

from app.domain.problem import ProblemInput
from app.pipeline.problem_to_simulation import run_problem_to_simulation


def _projectile_model(problem_profile: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "model_type": "projectile_motion",
        "research_object": "钢球",
        "scenario": problem_profile["scenario"],
        "forces": [
            {"name": "重力", "direction": "竖直向下", "magnitude": "mg", "category": "field"}
        ],
        "force_cases": [
            {
                "stage_id": "stage-1",
                "stage_label": "斜面滚下与出射",
                "forces": [
                    {"name": "重力", "direction": "竖直向下", "magnitude": "mg", "category": "field"},
                    {"name": "支持力", "direction": "垂直接触面", "magnitude": "N", "category": "contact"},
                ],
                "motion_state": "钢球从斜面滚下并以水平初速度离开桌边。",
                "focus": "出射点是平抛初状态，初速度方向水平。",
            },
            {
                "stage_id": "stage-2",
                "stage_label": "平抛飞行与击板",
                "forces": [
                    {"name": "重力", "direction": "竖直向下", "magnitude": "mg", "category": "field"}
                ],
                "motion_state": "钢球在空中做平抛运动，水平速度不变，竖直速度增大。",
                "focus": "h 影响飞行时间、竖直分速度和末速度方向。",
            },
        ],
        "constraints": [
            "忽略空气阻力",
            "离台后仅受重力",
        ],
        "motion_state": "钢球离台后做平抛运动。",
        "core_principles": [
            "平抛运动水平和竖直方向独立",
            "t=sqrt(2h/g)",
            "x=v0*t",
            "tan(theta)=vy/vx",
        ],
        "misconceptions": [
            "把 x 与 h 视为相互独立",
            "误以为撞击速度方向与 h 无关",
            "把 v0 错写成 x*sqrt(2h/g)",
        ],
        "derived_quantities": {
            "time_of_flight": "sqrt(2h/g)",
            "horizontal_displacement": "x=v0*sqrt(2h/g)",
            "initial_speed": "v0=x*sqrt(g/2h)",
            "vertical_speed": "vy=sqrt(2gh)",
        },
        "knowledge_points": [
            "平抛运动",
            "运动分解",
            "位移-时间-速度关系",
        ],
        "option_analysis": {
            "A": "错误",
            "B": "正确",
            "C": "错误",
            "D": "错误",
        },
        "problem_profile_summary": {
            "research_object": problem_profile["research_object"],
            "stage_type": problem_profile["stage_type"],
        },
    }


def _elastic_model(problem_profile: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "model_type": "symmetric_elastic_motion",
        "research_object": "物块",
        "scenario": problem_profile["scenario"],
        "forces": [
            {"name": "重力", "direction": "竖直向下", "magnitude": "mg", "category": "field"},
            {"name": "支持力", "direction": "竖直向上", "magnitude": "N", "category": "contact"},
            {"name": "摩擦力", "direction": "与运动方向相反", "magnitude": "μmg", "category": "contact"},
        ],
        "force_cases": [
            {
                "stage_id": "stage-1",
                "stage_label": "O 点释放",
                "forces": [
                    {"name": "重力", "direction": "竖直向下", "magnitude": "mg", "category": "field"},
                    {"name": "支持力", "direction": "竖直向上", "magnitude": "N", "category": "contact"},
                    {"name": "两根橡皮绳弹力合力", "direction": "沿 CO 指向 C", "magnitude": "2Fcosθ", "category": "elastic"},
                ],
                "motion_state": "物块由 O 向 C 加速运动，摩擦力始终阻碍运动。",
                "focus": "对称弹力的横向分量合成形成回复力。",
            },
            {
                "stage_id": "stage-2",
                "stage_label": "向 C 回程",
                "forces": [
                    {"name": "重力", "direction": "竖直向下", "magnitude": "mg", "category": "field"},
                    {"name": "支持力", "direction": "竖直向上", "magnitude": "N", "category": "contact"},
                    {"name": "摩擦力", "direction": "与运动方向相反", "magnitude": "μmg", "category": "contact"},
                    {"name": "两根橡皮绳弹力合力", "direction": "沿 CO 指向 C", "magnitude": "2Fcosθ", "category": "elastic"},
                ],
                "motion_state": "运动过程中机械能因摩擦逐渐减少，不做简谐运动。",
                "focus": "区分回复力存在与简谐运动成立不是一回事。",
            },
        ],
        "constraints": [
            "橡皮绳始终处于弹性限度内",
            "桌面水平",
            "存在动摩擦",
        ],
        "motion_state": "物块在回复力和摩擦力共同作用下往返运动，但不是简谐运动。",
        "core_principles": [
            "受力合成",
            "对称弹力的水平分量合成",
            "动能定理",
            "机械能变化与摩擦做功",
        ],
        "misconceptions": [
            "只把两根橡皮绳看成一个单独弹力",
            "把存在回复力直接等同于简谐运动",
            "忽略摩擦力做功",
        ],
        "derived_quantities": {
            "resultant_elastic_force": "2Fcosθ",
            "when_AOB_is_90_deg": "合力=2Fcos45°=√2F",
            "work_energy_relation": "W_elastic=1/2 mv0^2 + μmgL",
        },
        "knowledge_points": [
            "受力分析",
            "回复力",
            "简谐运动判据",
            "动能定理",
        ],
        "option_analysis": {
            "A": "错误",
            "B": "正确",
            "C": "正确",
            "D": "正确",
        },
        "problem_profile_summary": {
            "research_object": problem_profile["research_object"],
            "stage_type": problem_profile["stage_type"],
        },
    }


def _force_model(problem: ProblemInput, problem_profile: Dict[str, Any]) -> Dict[str, Any]:
    pipeline_result = run_problem_to_simulation(problem)
    model = pipeline_result.physics_model
    model["problem_profile_summary"] = {
        "research_object": problem_profile["research_object"],
        "stage_type": problem_profile["stage_type"],
    }
    model["knowledge_points"] = ["受力分析"]
    return model


def build_physics_model(problem: ProblemInput, problem_profile: Dict[str, Any]) -> Dict[str, Any]:
    family = problem_profile["model_family"]
    if family == "projectile-motion":
        return _projectile_model(problem_profile)
    if family == "symmetric-elastic-motion":
        return _elastic_model(problem_profile)
    return _force_model(problem, problem_profile)
