import re
from typing import Dict, List, Tuple

from app.domain.model import ForceCase, ForceItem, PhysicsModel
from app.domain.problem import ProblemInput, ProblemStage, StructuredProblem
from app.domain.scene import ProblemToSimulationResult, SimulationScene, StageLog


def _extract_known_conditions(text: str) -> List[str]:
    knowns: List[str] = []
    patterns = [
        (r"质量为(\d+(?:\.\d+)?)kg", "质量"),
        (r"大小为(\d+(?:\.\d+)?)N", "拉力"),
        (r"摩擦力大小为(\d+(?:\.\d+)?)N", "摩擦力"),
    ]
    for pattern, label in patterns:
        match = re.search(pattern, text)
        if match:
            knowns.append(f"{label}={match.group(1)}")
    if "静止" in text:
        knowns.append("初始状态=静止")
    if "粗糙水平面" in text:
        knowns.append("接触面=粗糙水平面")
    if "忽略空气阻力" in text:
        knowns.append("空气阻力=忽略")
    return knowns


def _extract_target_questions(text: str) -> List[str]:
    targets: List[str] = []
    if "受力" in text:
        targets.append("分析受力情况")
    if "运动状态" in text:
        targets.append("判断运动状态")
    if "哪些力" in text or "存在或消失" in text:
        targets.append("比较不同阶段的力是否存在")
    if "质点" in text:
        targets.append("判断能否视为质点")
    if not targets:
        targets.append("构建受力分析模型")
    return targets


def _extract_research_object(text: str) -> str:
    if "小猫" in text:
        return "小猫"
    if "足球" in text:
        return "足球"
    if "木块" in text:
        return "木块"
    if "物块" in text:
        return "物块"
    if "运动员" in text:
        return "运动员"
    return "研究对象"


def _extract_scenario(text: str) -> str:
    if "小猫" in text and "腾空" in text:
        return "接触到腾空的分阶段受力"
    if "足球" in text and "触网" in text:
        return "飞行到触网的分阶段受力"
    if "水平面" in text:
        return "粗糙水平面受力"
    if "斜面" in text:
        return "斜面受力"
    if "质点" in text:
        return "建模条件判断"
    return "一般受力分析情境"


def _detect_stage_type(text: str) -> str:
    if "小猫" in text and "腾空" in text:
        return "cat-jump"
    if "足球" in text and "触网" in text:
        return "football-net"
    return "single-stage"


def _build_problem_stages(text: str) -> List[ProblemStage]:
    stage_type = _detect_stage_type(text)
    if stage_type == "cat-jump":
        return [
            ProblemStage(
                id="stage-1",
                label="蹬地阶段",
                description="小猫与地面接触，通过蹬地产生跃起趋势。",
                contact_state="与地面接触",
                key_question="此阶段除重力外是否存在地面对小猫的支持作用？",
            ),
            ProblemStage(
                id="stage-2",
                label="腾空阶段",
                description="小猫离开地面后在空中运动。",
                contact_state="脱离地面",
                key_question="离地后哪些接触力消失，哪些力仍然存在？",
            ),
        ]
    if stage_type == "football-net":
        return [
            ProblemStage(
                id="stage-1",
                label="飞行阶段",
                description="足球离脚后在空中飞行，题目要求忽略空气阻力。",
                contact_state="无接触",
                key_question="飞行过程中足球主要受哪些外力？",
            ),
            ProblemStage(
                id="stage-2",
                label="触网阶段",
                description="足球与球网接触并发生形变。",
                contact_state="与球网接触",
                key_question="触网时新增了什么接触力？",
            ),
        ]
    return [
        ProblemStage(
            id="stage-1",
            label="受力分析阶段",
            description="按题干条件对研究对象进行单阶段受力分析。",
            contact_state="按题干确定",
            key_question="列全受力并判断合力方向。",
        )
    ]


def _problem_parser(problem: ProblemInput) -> Tuple[StructuredProblem, StageLog]:
    text = problem.text
    research_object = _extract_research_object(text)
    scenario = _extract_scenario(text)
    stages = _build_problem_stages(text)
    structured = StructuredProblem(
        summary=text[:80],
        research_object=research_object,
        scenario=scenario,
        known_conditions=_extract_known_conditions(text),
        target_questions=_extract_target_questions(text),
        explicit_constraints=["受力分析限于题干明示条件"],
        implicit_constraints=["默认重力方向竖直向下", "默认支持面提供支持力"],
        key_actions=["识别研究对象", "列出受力", "判断合力和运动状态"],
        stages=stages,
    )
    stage_log = StageLog(
        task_id="stage-1",
        task_type="problem_parser",
        status="completed",
        input_summary="原始题目文本",
        output_digest=f"抽取对象={research_object}，情境={scenario}，阶段数={len(stages)}",
        warnings=[],
        debug_notes=["使用规则模板抽取对象、条件、问题目标与阶段切分"],
        next_task="force_model_builder",
    )
    return structured, stage_log


def _single_stage_forces(problem_text: str) -> Tuple[List[ForceItem], Dict[str, str]]:
    forces = [
        ForceItem(name="重力", direction="竖直向下", magnitude="mg", category="field"),
        ForceItem(name="支持力", direction="竖直向上", magnitude="N", category="contact"),
    ]
    derived = {"gravity_expression": "G=mg"}
    if "拉力" in problem_text:
        pull_match = re.search(r"大小为(\d+(?:\.\d+)?)N", problem_text)
        pull_value = pull_match.group(1) if pull_match else "未知"
        direction = "水平向右" if "向右" in problem_text else "水平"
        forces.append(
            ForceItem(name="拉力", direction=direction, magnitude=f"{pull_value}N", category="applied")
        )
        derived["pull_force"] = f"{pull_value}N"
    if "摩擦力" in problem_text:
        friction_match = re.search(r"摩擦力大小为(\d+(?:\.\d+)?)N", problem_text)
        friction_value = friction_match.group(1) if friction_match else "未知"
        direction = "水平向左" if "向右" in problem_text else "与相对运动趋势相反"
        forces.append(
            ForceItem(
                name="摩擦力",
                direction=direction,
                magnitude=f"{friction_value}N",
                category="contact",
            )
        )
        derived["friction_force"] = f"{friction_value}N"
    return forces, derived


def _infer_single_stage_motion(problem_text: str) -> str:
    if "静止" in problem_text and "拉力" in problem_text and "摩擦力" in problem_text:
        pull_match = re.search(r"大小为(\d+(?:\.\d+)?)N", problem_text)
        friction_match = re.search(r"摩擦力大小为(\d+(?:\.\d+)?)N", problem_text)
        if pull_match and friction_match:
            pull_force = float(pull_match.group(1))
            friction_force = float(friction_match.group(1))
            if pull_force > friction_force:
                return "合力向右，木块将向右加速"
            if pull_force == friction_force:
                return "合力为零，木块保持静止或匀速"
    return "需要结合受力与初始条件综合判断"


def _build_force_cases(structured: StructuredProblem, problem_text: str) -> Tuple[List[ForceCase], Dict[str, str]]:
    stage_type = _detect_stage_type(problem_text)
    if stage_type == "cat-jump":
        return (
            [
                ForceCase(
                    stage_id="stage-1",
                    stage_label="蹬地阶段",
                    forces=[
                        ForceItem(name="重力", direction="竖直向下", magnitude="mg", category="field"),
                        ForceItem(name="地面支持力", direction="竖直向上", magnitude="N", category="contact"),
                    ],
                    motion_state="与地面接触，竖直方向合力向上，准备跃起。",
                    focus="识别接触力存在的前提是与地面接触。",
                ),
                ForceCase(
                    stage_id="stage-2",
                    stage_label="腾空阶段",
                    forces=[
                        ForceItem(name="重力", direction="竖直向下", magnitude="mg", category="field"),
                    ],
                    motion_state="离地后只受重力作用，做曲线运动。",
                    focus="离地后地面支持力消失，只保留非接触力。",
                ),
            ],
            {"stage_type": "cat-jump", "focus": "接触力随接触状态变化"},
        )
    if stage_type == "football-net":
        return (
            [
                ForceCase(
                    stage_id="stage-1",
                    stage_label="飞行阶段",
                    forces=[
                        ForceItem(name="重力", direction="竖直向下", magnitude="mg", category="field"),
                    ],
                    motion_state="忽略空气阻力时，飞行阶段只受重力。",
                    focus="无接触且忽略空气阻力时，仅保留重力。",
                ),
                ForceCase(
                    stage_id="stage-2",
                    stage_label="触网阶段",
                    forces=[
                        ForceItem(name="重力", direction="竖直向下", magnitude="mg", category="field"),
                        ForceItem(name="球网弹力", direction="与压缩方向相反", magnitude="F_net", category="contact"),
                    ],
                    motion_state="触网后新增球网弹力，合力方向取决于接触形变。",
                    focus="接触后新增弹力，受力数量发生变化。",
                ),
            ],
            {"stage_type": "football-net", "focus": "飞行与接触的受力对比"},
        )

    single_stage_forces, derived = _single_stage_forces(problem_text)
    return (
        [
            ForceCase(
                stage_id=structured.stages[0].id,
                stage_label=structured.stages[0].label,
                forces=single_stage_forces,
                motion_state=_infer_single_stage_motion(problem_text),
                focus="单阶段列全受力并判断合力。",
            )
        ],
        derived,
    )


def _force_model_builder(structured: StructuredProblem, problem: ProblemInput) -> Tuple[PhysicsModel, StageLog]:
    force_cases, derived_quantities = _build_force_cases(structured, problem.text)
    model = PhysicsModel(
        model_type="force_analysis",
        research_object=structured.research_object,
        scenario=structured.scenario,
        forces=force_cases[0].forces,
        force_cases=force_cases,
        constraints=structured.explicit_constraints + structured.implicit_constraints,
        motion_state=force_cases[-1].motion_state,
        core_principles=["牛顿运动定律", "受力平衡分析", "接触力存在条件判断"],
        misconceptions=["把接触力错误保留到脱离接触后的阶段", "遗漏重力这一恒定存在的场力"],
        derived_quantities=derived_quantities,
    )
    stage_log = StageLog(
        task_id="stage-2",
        task_type="force_model_builder",
        status="completed",
        input_summary="结构化题目结果",
        output_digest=f"生成 {len(model.force_cases)} 个阶段受力案例",
        warnings=[],
        debug_notes=["依据题型模板生成分阶段受力项与阶段焦点"],
        next_task="scene_compiler",
    )
    return model, stage_log


def _force_cases_to_stage_map(force_cases: List[ForceCase]) -> Dict[str, List[Dict[str, str]]]:
    return {
        case.stage_id: [force.model_dump() for force in case.forces]
        for case in force_cases
    }


def _scene_compiler(model: PhysicsModel) -> Tuple[SimulationScene, StageLog]:
    stage_options = [
        {"id": force_case.stage_id, "label": force_case.stage_label}
        for force_case in model.force_cases
    ]
    active_case = model.force_cases[0]
    visual_elements = [
        {
            "type": "object",
            "id": "subject",
            "label": model.research_object,
            "position": "center",
        },
        {
            "type": "stage-badge",
            "id": "active-stage",
            "label": active_case.stage_label,
            "position": "top",
        },
    ]
    for index, force in enumerate(active_case.forces, start=1):
        visual_elements.append(
            {
                "type": "force-vector",
                "id": f"{active_case.stage_id}-force-{index}",
                "stage_id": active_case.stage_id,
                "label": force.name,
                "direction": force.direction,
                "magnitude": force.magnitude,
            }
        )

    scene = SimulationScene(
        scene_type="force-analysis",
        template_id="force-analysis-staged-v1" if len(model.force_cases) > 1 else "force-analysis-horizontal-v1",
        coordinate_system="x-right-y-up",
        visual_elements=visual_elements,
        controls=[
            {"type": "select", "id": "stage-selector", "label": "阶段切换", "options": stage_options},
            {"type": "toggle", "id": "show-resultant", "label": "显示合力", "default": True},
            {"type": "toggle", "id": "show-force-labels", "label": "显示力名称", "default": True},
        ],
        parameters={
            "surface_type": "staged-force-analysis" if len(model.force_cases) > 1 else "horizontal",
            "active_stage_id": active_case.stage_id,
            "stage_options": stage_options,
            "forces_by_stage": _force_cases_to_stage_map(model.force_cases),
            "motion_state_by_stage": {
                case.stage_id: case.motion_state for case in model.force_cases
            },
            "focus_by_stage": {
                case.stage_id: case.focus for case in model.force_cases
            },
            "show_resultant": True,
        },
        notes=["第一版 scene 以阶段切换和受力显隐为主，不做连续时间动画。"],
    )
    stage_log = StageLog(
        task_id="stage-3",
        task_type="scene_compiler",
        status="completed",
        input_summary="物理模型结果",
        output_digest=f"生成 {len(scene.visual_elements)} 个可视元素和 {len(stage_options)} 个阶段选项",
        warnings=[],
        debug_notes=["将阶段受力映射为可切换的 force-vector 结构"],
        next_task="simulation_adapter",
    )
    return scene, stage_log


def _simulation_adapter(scene: SimulationScene, model: PhysicsModel) -> Tuple[SimulationScene, StageLog]:
    adapted_scene = scene.model_copy(deep=True)
    adapted_scene.parameters["resultant_hint"] = model.motion_state
    adapted_scene.parameters["scene_mode"] = "stage-switching"
    stage_log = StageLog(
        task_id="stage-4",
        task_type="simulation_adapter",
        status="completed",
        input_summary="scene 编译结果",
        output_digest="补充交互参数与运行提示",
        warnings=["当前版本未实现真实时间步进仿真"],
        debug_notes=["保留 simulation adapter 作为未来物理引擎接入点"],
        next_task="",
    )
    return adapted_scene, stage_log


def run_problem_to_simulation(problem: ProblemInput) -> ProblemToSimulationResult:
    structured, parser_log = _problem_parser(problem)
    model, model_log = _force_model_builder(structured, problem)
    scene, scene_log = _scene_compiler(model)
    adapted_scene, adapter_log = _simulation_adapter(scene, model)

    warnings = adapter_log.warnings[:]
    return ProblemToSimulationResult(
        problem_summary=structured.summary,
        structured_problem=structured.model_dump(),
        physics_model=model.model_dump(),
        scene=adapted_scene.model_dump(),
        stage_logs=[
            parser_log.model_dump(),
            model_log.model_dump(),
            scene_log.model_dump(),
            adapter_log.model_dump(),
        ],
        warnings=warnings,
    )
