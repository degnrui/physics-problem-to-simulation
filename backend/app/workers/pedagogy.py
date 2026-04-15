from typing import Any, Dict


def build_teaching_plan(
    problem_profile: Dict[str, Any],
    physics_model: Dict[str, Any],
    planner: Dict[str, Any],
) -> Dict[str, Any]:
    stage_count = len(problem_profile.get("stages", []))
    if planner["model_family"] == "projectile-motion":
        return {
            "classroom_use": "选项辨析 + 参数探究",
            "primary_goal": "帮助教师显化 h、t、x 和末速度方向之间的关系",
            "observation_targets": [
                "改变 h 时飞行时间如何变化",
                "落点水平距离与 h 的关系",
                "撞击木板瞬间速度方向是否变化",
            ],
            "teacher_prompts": [
                "先固定出射速度，拖动 h，观察轨迹和落点。",
                "再显示公式面板，对照 t=sqrt(2h/g) 与 x=v0t。",
            ],
            "misconception_focus": physics_model.get("misconceptions", []),
            "interaction_strategy": "参数滑块 + 轨迹回放 + 速度矢量显示",
            "recommended_duration_minutes": 8,
        }
    if planner["model_family"] == "symmetric-elastic-motion":
        return {
            "classroom_use": "受力讲评 + 回复运动可视化",
            "primary_goal": "帮助教师显化对称弹力合成、摩擦影响和选项判断依据",
            "observation_targets": [
                "O 点处合回复力方向",
                "AOB 角变化时合力大小",
                "摩擦对机械能和到达 C 点速度的影响",
            ],
            "teacher_prompts": [
                "先显示两根橡皮绳的弹力分解，再看水平方向合力。",
                "切换到能量面板，比较弹力做功和摩擦做功。",
            ],
            "misconception_focus": physics_model.get("misconceptions", []),
            "interaction_strategy": "位移拖拽 + 力分解显示 + 功能量面板",
            "recommended_duration_minutes": 10,
        }
    return {
        "classroom_use": "习题讲评 + 课堂演示",
        "primary_goal": "帮助教师显化分阶段受力变化",
        "observation_targets": [
            "识别不同阶段是否仍存在接触力",
            "比较受力数量和方向的变化",
        ],
        "teacher_prompts": [
            "请先判断研究对象在这一阶段是否仍与外界接触。",
            "如果接触状态变化了，哪些力会随之出现或消失？",
        ],
        "misconception_focus": physics_model.get("misconceptions", []),
        "interaction_strategy": (
            "阶段切换 + 力箭头显隐 + 教学焦点提示"
            if planner["simulation_ready"]
            else "输出建模判断提示与课堂讨论问题"
        ),
        "recommended_duration_minutes": 5 if stage_count <= 1 else 8,
    }
