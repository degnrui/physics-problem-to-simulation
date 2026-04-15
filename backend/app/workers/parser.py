from typing import Any, Dict, List

from app.domain.problem import ProblemInput
from app.pipeline.problem_to_simulation import run_problem_to_simulation


def _projectile_profile(problem: ProblemInput, planner: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "summary": problem.text[:120],
        "research_object": "钢球",
        "scenario": "斜面出射后的平抛运动",
        "known_conditions": [
            "钢球从同一位置静止滚下",
            "离开桌边后做平抛运动",
            "木板距桌面竖直距离为h",
            "落点距桌边水平距离为x",
        ],
        "target_questions": [
            "建立平抛时间与位移关系",
            "判断速度方向是否随h改变",
            "辨析选项正误",
        ],
        "stages": [
            {
                "id": "stage-1",
                "label": "斜面滚下与出射",
                "description": "钢球从斜面滚下并以水平初速度离开桌边。",
                "contact_state": "与斜面/桌面接触",
                "key_question": "出射瞬间水平初速度如何确定？",
            },
            {
                "id": "stage-2",
                "label": "平抛飞行与击板",
                "description": "钢球离台后在重力作用下做平抛运动并击中木板。",
                "contact_state": "空中飞行",
                "key_question": "h 改变时飞行时间、落点和速度方向如何变化？",
            },
        ],
        "topic": planner["topic"],
        "problem_family": planner["problem_family"],
        "model_family": planner["model_family"],
        "stage_type": planner["stage_type"],
        "simulation_mode": planner["simulation_mode"],
        "simulation_ready": planner["simulation_ready"],
    }


def _elastic_profile(problem: ProblemInput, planner: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "summary": problem.text[:120],
        "research_object": "物块",
        "scenario": "双橡皮绳约束下的回复运动",
        "known_conditions": [
            "两根相同橡皮绳",
            "C 点时橡皮绳为原长",
            "物块沿 AB 中垂线拉至 O 点后静止释放",
            "CO=L",
            "存在动摩擦因数μ",
        ],
        "target_questions": [
            "分析回复力来源与方向",
            "判断是否做简谐运动",
            "建立功和能量变化关系",
        ],
        "stages": [
            {
                "id": "stage-1",
                "label": "O 点释放",
                "description": "物块位于 O 点，两根橡皮绳均被拉伸，存在对称回复力。",
                "contact_state": "与桌面接触",
                "key_question": "此时合力与位移方向关系如何？",
            },
            {
                "id": "stage-2",
                "label": "向 C 回程",
                "description": "物块在弹力和摩擦力共同作用下向 C 运动。",
                "contact_state": "与桌面接触",
                "key_question": "摩擦力如何影响机械能与到达 C 点速度？",
            },
        ],
        "topic": planner["topic"],
        "problem_family": planner["problem_family"],
        "model_family": planner["model_family"],
        "stage_type": planner["stage_type"],
        "simulation_mode": planner["simulation_mode"],
        "simulation_ready": planner["simulation_ready"],
    }


def _force_profile(problem: ProblemInput, planner: Dict[str, Any]) -> Dict[str, Any]:
    pipeline_result = run_problem_to_simulation(problem)
    structured = pipeline_result.structured_problem
    return {
        "summary": pipeline_result.problem_summary,
        "research_object": structured["research_object"],
        "scenario": structured["scenario"],
        "known_conditions": structured["known_conditions"],
        "target_questions": structured["target_questions"],
        "stages": structured.get("stages", []),
        "topic": planner["topic"],
        "problem_family": planner["problem_family"],
        "model_family": planner["model_family"],
        "stage_type": planner["stage_type"],
        "simulation_mode": planner["simulation_mode"],
        "simulation_ready": planner["simulation_ready"],
    }


def build_problem_profile(problem: ProblemInput, planner: Dict[str, Any]) -> Dict[str, Any]:
    family = planner["problem_family"]
    if family == "projectile-motion":
        return _projectile_profile(problem, planner)
    if family == "elastic-motion":
        return _elastic_profile(problem, planner)
    return _force_profile(problem, planner)
