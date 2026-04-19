from typing import Any, Dict

from app.domain.problem import ProblemInput


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def build_plan_metadata(problem: ProblemInput) -> Dict[str, Any]:
    text = problem.text
    if "平抛运动" in text or ("钢球" in text and "落点" in text and "水平距离" in text):
        return {
            "topic": "high-school-physics",
            "problem_family": "projectile-motion",
            "model_family": "projectile-motion",
            "stage_type": "ramp-to-projectile",
            "simulation_mode": "trajectory-lab",
            "simulation_ready": True,
            "reason": "题目核心是平抛轨迹、飞行时间和落点关系，适合做轨迹与参数联动仿真。",
        }
    if "橡皮绳" in text and "AB中垂线" in text:
        return {
            "topic": "high-school-physics",
            "problem_family": "elastic-motion",
            "model_family": "symmetric-elastic-motion",
            "stage_type": "restoring-motion",
            "simulation_mode": "restoring-force-lab",
            "simulation_ready": True,
            "reason": "题目核心是对称弹力、摩擦与往复运动，适合做回复力和能量变化仿真。",
        }
    if "质点" in text:
        return {
            "topic": "high-school-physics",
            "problem_family": "modeling-judgement",
            "model_family": "modeling-judgement",
            "stage_type": "modeling-judgement",
            "simulation_mode": "analysis-only",
            "simulation_ready": False,
            "reason": "该题首先是建模判断题，优先输出教学分析包而不是强行生成仿真。",
        }
    if "小猫" in text and "腾空" in text:
        return {
            "topic": "high-school-physics",
            "problem_family": "force-analysis",
            "model_family": "force-analysis",
            "stage_type": "cat-jump",
            "simulation_mode": "stage-force-visualization",
            "simulation_ready": True,
            "reason": "接触到腾空的阶段切换适合映射为分阶段受力 simulation。",
        }
    if "足球" in text and "触网" in text:
        return {
            "topic": "high-school-physics",
            "problem_family": "force-analysis",
            "model_family": "force-analysis",
            "stage_type": "football-net",
            "simulation_mode": "stage-force-visualization",
            "simulation_ready": True,
            "reason": "飞行到触网的受力变化适合映射为阶段切换 simulation。",
        }
    if _contains_any(text, ("飞行", "空中")) and _contains_any(
        text,
        ("触网", "触板", "碰到", "碰板", "撞到", "撞击", "击中", "落地", "着地", "接触", "反弹"),
    ):
        return {
            "topic": "high-school-physics",
            "problem_family": "force-analysis",
            "model_family": "force-analysis",
            "stage_type": "contact-impact",
            "simulation_mode": "stage-force-visualization",
            "simulation_ready": True,
            "reason": "题目涉及飞行到接触的受力切换，适合映射为分阶段受力 simulation。",
        }
    if _contains_any(text, ("腾空", "离地", "离开地面", "脱离", "离手", "起跳", "蹬地")):
        return {
            "topic": "high-school-physics",
            "problem_family": "force-analysis",
            "model_family": "force-analysis",
            "stage_type": "contact-release",
            "simulation_mode": "stage-force-visualization",
            "simulation_ready": True,
            "reason": "题目涉及接触到脱离接触的受力切换，适合映射为分阶段受力 simulation。",
        }
    return {
        "topic": "high-school-physics",
        "problem_family": "force-analysis",
        "model_family": "force-analysis",
        "stage_type": "single-stage",
        "simulation_mode": "stage-force-visualization",
        "simulation_ready": True,
        "reason": "当前默认使用受力分析模板进入 simulation 链路。",
    }
