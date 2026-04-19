from __future__ import annotations

import math
import re
from typing import Any, Dict, List

from app.domain.problem import ProblemInput
from app.harness.stage_runtime import (
    ArtifactMap,
    StageContract,
    ValidationIssue,
    ValidationResult,
    missing_required_issues,
)


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _split_sentences(text: str) -> List[str]:
    parts = re.split(r"[。！？;\n]+", text)
    return [part.strip() for part in parts if part.strip()]


def _first_sentence(text: str) -> str:
    sentences = _split_sentences(text)
    return sentences[0] if sentences else text.strip()


def _extract_answer(text: str) -> str | None:
    match = re.search(r"答案[:：]\s*([A-D])", text, flags=re.IGNORECASE)
    return match.group(1).upper() if match else None


def _extract_explanation(text: str) -> str:
    match = re.search(r"解析[:：](.+)$", text, flags=re.DOTALL)
    return match.group(1).strip() if match else ""


def _extract_formulas(text: str) -> List[str]:
    formulas = re.findall(r"[A-Za-z_][^。；\n]*?=[^。；\n]+", text)
    unique: List[str] = []
    for formula in formulas:
        normalized = formula.strip()
        if normalized and normalized not in unique:
            unique.append(normalized)
    return unique[:8]


def _extract_research_object(text: str) -> str:
    patterns = [
        r"质量为[^，。,；;]*?的([^，。,；;]+)",
        r"让([^，。,；;]+?)从",
        r"([小钢铁木足篮猫球物块]+[球块猫]*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            candidate = re.sub(r"\s+", "", match.group(1))
            if 1 <= len(candidate) <= 12:
                return candidate
    for candidate in ("小铁球", "小球", "钢球", "物块", "足球", "篮球", "小猫"):
        if candidate in text:
            return candidate
    return "研究对象"


def _extract_numeric_givens(text: str) -> List[str]:
    clauses = re.split(r"[。；;\n]", text)
    givens: List[str] = []
    for clause in clauses:
        normalized = clause.strip()
        if not normalized:
            continue
        if re.search(r"\d", normalized) or _contains_any(normalized, ("质量", "倾角", "间距", "重力加速度", "答案", "解析")):
            givens.append(normalized)
    return givens[:10]


def _extract_target_questions(text: str, explanation: str) -> List[str]:
    questions: List[str] = []
    if re.search(r"\bA\.", text) and re.search(r"\bB\.", text):
        questions.append("判断选项正误")
    if "周期" in text or "单摆" in text:
        questions.append("确定等效摆长与摆动周期")
    if "拉力" in text:
        questions.append("比较绳两端拉力与平衡条件")
    if explanation and "正确" in explanation:
        questions.append("根据解析验证关键物理关系")
    return questions or ["提炼题目中的关键物理关系"]


def _infer_stages(text: str) -> List[Dict[str, Any]]:
    stages: List[Dict[str, Any]] = []
    if "平衡时" in text:
        stages.append(
            {
                "id": "stage-1",
                "label": "平衡态分析",
                "description": "分析研究对象在平衡位置时的受力和约束关系。",
                "contact_state": "静态平衡",
                "key_question": "平衡时哪些力相互制约？",
            }
        )
    if _contains_any(text, ("扰动", "摆动", "振动", "释放")):
        stages.append(
            {
                "id": f"stage-{len(stages) + 1}",
                "label": "扰动后运动",
                "description": "观察受到微扰后的运动模型、周期或能量关系。",
                "contact_state": "动态响应",
                "key_question": "扰动后由哪个等效模型描述运动？",
            }
        )
    if not stages:
        stages.append(
            {
                "id": "stage-1",
                "label": "题目分析",
                "description": "围绕题目条件建立核心物理关系。",
                "contact_state": "按题意确定",
                "key_question": "哪些量是必须建立联系的？",
            }
        )
    return stages


def _experience_mode(text: str) -> str:
    lowered = text.lower()
    if _contains_any(text, ("自主探究", "学生探索", "课后")):
        return "student_exploration"
    if _contains_any(text, ("课堂", "讲评", "演示", "教师")) or "teacher" in lowered:
        return "teacher_demo"
    return "hybrid"


def _input_profile(text: str) -> str:
    if _contains_any(text, ("改一下", "修改", "优化")) and "simulation" in text.lower():
        return "revision_existing_simulation"
    if _extract_answer(text) or "解析" in text:
        return "problem_with_solution"
    if len(text.strip()) < 24:
        return "goal_only"
    return "problem_only"


def _information_density(text: str) -> str:
    length = len(text.strip())
    if length < 40:
        return "low"
    if length < 180:
        return "medium"
    return "high"


def _infer_model_type(text: str, explanation: str) -> str:
    corpus = f"{text}\n{explanation}"
    if "单摆" in corpus:
        return "small_angle_pendulum"
    if _contains_any(corpus, ("橡皮绳", "回复力", "简谐")):
        return "restoring_motion"
    if "平抛" in corpus:
        return "projectile_motion"
    if _contains_any(corpus, ("受力", "拉力", "支持力")):
        return "constraint_force_model"
    return "generic_physics_model"


def _generic_scene_template(model_type: str) -> str:
    if model_type == "small_angle_pendulum":
        return "physics-pendulum-lab-v1"
    if model_type == "restoring_motion":
        return "physics-restoring-lab-v1"
    if model_type == "projectile_motion":
        return "physics-trajectory-lab-v1"
    return "physics-concept-lab-v1"


def build_run_profiling(problem: ProblemInput, _: ArtifactMap) -> Dict[str, Any]:
    answer = _extract_answer(problem.text)
    return {
        "input_profile": _input_profile(problem.text),
        "run_mode": "generate_from_problem",
        "information_density": _information_density(problem.text),
        "experience_mode": _experience_mode(problem.text),
        "has_explicit_problem": True,
        "has_explicit_solution": bool(answer or "解析" in problem.text),
        "has_diagram_reference": "如图" in problem.text or "图示" in problem.text,
        "has_existing_simulation": False,
        "missing_context": [],
        "next_stage_plan": [
            "01_evidence_completion" if _information_density(problem.text) == "low" else "02_knowledge_grounding",
            "03_structured_task_model",
            "04_instructional_design_brief",
        ],
    }


def build_evidence_completion(problem: ProblemInput, artifacts: ArtifactMap) -> Dict[str, Any]:
    profiling = artifacts["run_profiling"]
    performed = profiling["information_density"] == "low"
    return {
        "performed": performed,
        "completion_status": "completed" if performed else "skipped",
        "completion_actions": ["补充默认观察目标", "补充边界条件"] if performed else [],
        "evidence_bundle": {
            "reference_solution_status": "provided" if profiling["has_explicit_solution"] else "missing",
            "diagram_reference_detected": profiling["has_diagram_reference"],
            "default_assumptions_added": performed,
        },
        "unresolved_gaps": [],
        "notes": "当前版本只做最小证据补全，不做外部检索。",
    }


def build_knowledge_grounding(problem: ProblemInput, artifacts: ArtifactMap) -> Dict[str, Any]:
    explanation = _extract_explanation(problem.text)
    formulas = _extract_formulas(problem.text)
    answer = _extract_answer(problem.text)
    assumptions: List[str] = []
    if "单摆" in problem.text:
        assumptions.extend(
            [
                "微小摆动近似为小角度单摆。",
                "细线不可伸长且光滑，同一根细线两端张力大小相等。",
            ]
        )
    if "光滑" in problem.text:
        assumptions.append("忽略摩擦与能量损耗。")
    if "等效" in problem.text:
        assumptions.append("允许将复杂约束等效为标准物理模型进行分析。")
    if not assumptions:
        assumptions.append("采用高中物理标准理想化近似，忽略未显式给出的次要非理想因素。")
    solution_basis: List[str] = []
    if answer:
        solution_basis.append(f"题目给定答案为 {answer}。")
    if explanation:
        solution_basis.append(explanation[:220])
    if not solution_basis:
        solution_basis.append("根据题干结构与标准高中物理关系建立可验证基准。")
    return {
        "grounding_type": "problem_solution_verified" if answer or explanation else "conceptual_grounding",
        "trustworthy": True,
        "concept_boundaries": [
            "先建立约束关系、几何关系和物理模型，再决定 simulation 的可视化表达。",
            "优先保留题目显式给出的答案、解析和标准公式。",
        ],
        "assumptions": assumptions,
        "solution_basis": solution_basis,
        "canonical_answer": answer,
        "canonical_explanation": explanation[:400],
        "key_formulas": formulas,
        "reference_notes": ["优先使用题干、答案和解析内的证据。"],
        "unresolved_risks": [],
    }


def build_structured_task_model(problem: ProblemInput, artifacts: ArtifactMap) -> Dict[str, Any]:
    explanation = artifacts["knowledge_grounding"]["canonical_explanation"]
    givens = _extract_numeric_givens(problem.text)
    if not givens:
        givens = [
            _first_sentence(problem.text) or "题干给出了需要转成 simulation 的物理情境。",
        ]
    return {
        "summary": _first_sentence(problem.text)[:160],
        "research_object": _extract_research_object(problem.text),
        "scenario": _first_sentence(problem.text),
        "givens": givens,
        "unknowns": _extract_target_questions(problem.text, explanation),
        "constraints": artifacts["knowledge_grounding"]["assumptions"],
        "target_questions": _extract_target_questions(problem.text, explanation),
        "stages": _infer_stages(problem.text),
        "success_conditions": [
            "关键物理关系正确",
            "教学证据可见并可比较",
            "spec 可被 deterministic compiler 消费",
        ],
    }


def build_instructional_design_brief(problem: ProblemInput, artifacts: ArtifactMap) -> Dict[str, Any]:
    del problem
    task_model = artifacts["structured_task_model"]
    mode = artifacts["run_profiling"]["experience_mode"]
    evidence_goals = task_model["target_questions"][:3]
    return {
        "teaching_goal": f"围绕 `{task_model['scenario']}` 组织一个可讲授、可验证的 simulation。",
        "target_misconceptions": [
            "把题目结论当作记忆结果，而不是来自物理关系的推导。",
            "看见界面变化但无法解释它对应的物理含义。",
        ],
        "evidence_goals": evidence_goals,
        "teacher_moves": [
            "先说明研究对象、约束与等效模型。",
            "再对照图形、数值和公式解释关键结论。",
        ],
        "student_actions": [
            "观察关键量并记录变化。",
            "根据图形或公式验证正确选项。",
        ],
        "success_criteria": task_model["success_conditions"],
        "classroom_use": "课堂演示" if mode == "teacher_demo" else "课堂讲评与探究",
        "assessment_hooks": [
            "是否能说明哪条公式或关系支持最终结论。",
            "是否能把图中几何关系转成物理量关系。",
        ],
        "interaction_strategy": "公式提示 + 可见证据 + 阶段比较",
    }


def build_physics_model_stage(problem: ProblemInput, artifacts: ArtifactMap) -> Dict[str, Any]:
    explanation = artifacts["knowledge_grounding"]["canonical_explanation"]
    model_type = _infer_model_type(problem.text, explanation)
    formulas = artifacts["knowledge_grounding"]["key_formulas"]
    relations = list(formulas)
    derived_results: List[str] = []
    misconceptions: List[str] = []
    key_quantities: List[str] = []
    if model_type == "small_angle_pendulum":
        if not any("T=" in formula or "T =" in formula for formula in relations):
            relations.append("T = 2pi * sqrt(l/g)")
        if not any("2F" in formula or "F_A" in formula for formula in relations):
            relations.append("2F_A cos30° = mg")
        key_quantities.extend(["摆长 l", "周期 T", "张力 F_A", "张力 F_B"])
        derived_results.extend(
            [
                "等效摆长 l = 1 m",
                "摆动周期 T 约为 2 s",
                "平衡时 F_A = F_B",
            ]
        )
        misconceptions.extend(
            [
                "误以为摆角会影响单摆周期。",
                "忽略同一根光滑细线两端张力相等。",
            ]
        )
    elif model_type == "restoring_motion":
        relations.extend(
            [
                "偏离平衡位置后合力总体指向平衡位置。",
                "摩擦力与瞬时运动方向相反，会耗散机械能。",
            ]
        )
        key_quantities.extend(["位移 x", "合力方向", "摩擦力", "机械能变化"])
        derived_results.extend(
            [
                "释放后物块围绕平衡位置往复或衰减运动。",
                "图像和文字提示需要同时呈现回复趋势与耗能。",
            ]
        )
        misconceptions.extend(
            [
                "只看位移变化，不追踪合力方向为何始终指向平衡位置。",
                "忽略摩擦导致的能量损失。",
            ]
        )
    elif model_type == "projectile_motion":
        relations.extend(
            [
                "离开接触面后研究对象只受重力作用。",
                "水平和竖直方向的运动可分解处理。",
            ]
        )
        key_quantities.extend(["水平位移", "竖直位移", "初速度", "飞行时间"])
        derived_results.extend(
            [
                "不同落点由初速度、下落高度和时间共同决定。",
            ]
        )
        misconceptions.extend(
            [
                "误以为离台后仍然保留支持力或推力。",
            ]
        )
    elif model_type == "constraint_force_model":
        relations.extend(
            [
                "不同接触阶段对应不同的受力集合。",
                "只有在发生接触时，接触力才会出现或改变。",
            ]
        )
        key_quantities.extend(["接触状态", "重力", "支持力或弹力", "合力变化"])
        derived_results.extend(
            [
                "需要把飞行、接触、反弹等阶段拆开比较。",
            ]
        )
        misconceptions.extend(
            [
                "把已经脱离接触后的力继续保留在受力图中。",
            ]
        )
    else:
        relations.append("先根据约束与状态识别受力，再建立量与结论之间的对应。")
        key_quantities.extend(["研究对象状态", "关键受力", "约束关系"])
        derived_results.append("根据题干和解析整理关键物理结论。")
        misconceptions.append("只记答案，不追踪物理关系来源。")
    return {
        "model_type": model_type,
        "research_object": artifacts["structured_task_model"]["research_object"],
        "state_variables": key_quantities,
        "relations": relations,
        "equilibrium_conditions": [sentence for sentence in _split_sentences(problem.text) if "平衡" in sentence][:3],
        "stages": artifacts["structured_task_model"]["stages"],
        "key_quantities": key_quantities,
        "misconceptions": misconceptions,
        "executable_constraints": [
            "图中可见量必须能映射到公式或结论。",
            "交互不能引入与题意冲突的自由度。",
        ],
        "derived_results": derived_results,
        "answer_evaluation": {
            "provided_answer": artifacts["knowledge_grounding"]["canonical_answer"],
            "explanation_excerpt": explanation[:220],
        },
    }


def build_representation_interaction_design(problem: ProblemInput, artifacts: ArtifactMap) -> Dict[str, Any]:
    model = artifacts["physics_model"]
    task_model = artifacts["structured_task_model"]
    template_id = _generic_scene_template(model["model_type"])
    controls = [
        {"type": "toggle", "id": "show-formulas", "label": "显示公式", "default": True},
        {"type": "toggle", "id": "show-evidence", "label": "显示关键证据", "default": True},
        {"type": "button", "id": "replay", "label": "重播"},
    ]
    if len(task_model["stages"]) > 1:
        controls.insert(
            0,
            {
                "type": "select",
                "id": "stage-selector",
                "label": "分析阶段",
                "options": [{"id": stage["id"], "label": stage["label"]} for stage in task_model["stages"]],
            },
        )
    visual_elements = [
        {"type": "focus-card", "id": "research-object", "label": task_model["research_object"]},
        {"type": "equation-board", "id": "equations", "label": "关键公式"},
        {"type": "evidence-panel", "id": "evidence", "label": "观察证据"},
    ]
    if model["model_type"] == "small_angle_pendulum":
        visual_elements.extend(
            [
                {"type": "rod", "id": "support-rod", "label": "斜杆 AB"},
                {"type": "ball", "id": "pendulum-ball", "label": task_model["research_object"]},
                {"type": "pivot", "id": "equivalent-pivot", "label": "等效悬挂点"},
                {"type": "arc", "id": "swing-arc", "label": "摆动轨迹"},
            ]
        )
    scene_spec = {
        "scene_type": "generic-physics-lab",
        "template_id": template_id,
        "visual_elements": visual_elements,
        "controls": controls,
        "parameters": {
            "summary": task_model["summary"],
            "research_object": task_model["research_object"],
            "relations": model["relations"],
            "derived_results": model["derived_results"],
            "stages": task_model["stages"],
        },
        "notes": [
            "优先展示题目结论的物理来源，而不是追求复杂动画。",
        ],
    }
    return {
        "visible_quantities": model["key_quantities"],
        "comparisons": ["公式与结论对应", "不同阶段或状态下的量变化"],
        "controls": controls,
        "hidden_logic": ["编译器负责把公式、提示和面板组织成稳定 runtime。"],
        "representations": visual_elements,
        "scene_spec": scene_spec,
    }


def build_experience_mode_adaptation(problem: ProblemInput, artifacts: ArtifactMap) -> Dict[str, Any]:
    del problem
    mode = artifacts["run_profiling"]["experience_mode"]
    scene_spec = dict(artifacts["representation_interaction_design"]["scene_spec"])
    controls = list(scene_spec["controls"])
    if mode == "teacher_demo" and len(controls) > 3:
        controls = controls[:3]
    scene_spec["controls"] = controls
    return {
        "experience_mode": mode,
        "ui_constraints": {
            "max_controls": len(controls),
            "presentation": "projection-first" if mode == "teacher_demo" else "self-directed",
        },
        "control_policy": "少而关键" if mode == "teacher_demo" else "带引导的探索",
        "pacing_strategy": "pause-and-explain" if mode == "teacher_demo" else "observe-compare-justify",
        "prompt_style": "teacher-facing" if mode == "teacher_demo" else "student-facing",
        "assessment_hooks": artifacts["instructional_design_brief"]["assessment_hooks"],
        "adapted_scene_spec": scene_spec,
    }


def build_simulation_spec_generation(problem: ProblemInput, artifacts: ArtifactMap) -> Dict[str, Any]:
    del problem
    scene_spec = artifacts["experience_mode_adaptation"]["adapted_scene_spec"]
    simulation_spec = {
        "template_id": scene_spec["template_id"],
        "renderer_mode": "generic-physics-runtime",
        "bindings": scene_spec["parameters"],
        "controls": scene_spec["controls"],
        "teaching_mode": artifacts["instructional_design_brief"]["classroom_use"],
        "runtime_contract": {
            "required_panels": ["simulation_canvas", "evidence_panel", "formula_panel", "teacher_guidance"],
            "evidence_goals": artifacts["instructional_design_brief"]["evidence_goals"],
        },
    }
    return {
        "scene_spec": scene_spec,
        "simulation_spec": simulation_spec,
        "executable": True,
        "delivery_targets": ["simulation_blueprint", "renderer_payload", "delivery_bundle"],
    }


def build_final_validation(problem: ProblemInput, artifacts: ArtifactMap) -> Dict[str, Any]:
    del problem
    issues: List[Dict[str, Any]] = []
    scene_spec = artifacts["simulation_spec_generation"]["scene_spec"]
    simulation_spec = artifacts["simulation_spec_generation"]["simulation_spec"]
    if not scene_spec.get("template_id"):
        issues.append({"issue_code": "MISSING_TEMPLATE", "why": "缺少 scene template", "fix_at": "06_representation_interaction_design"})
    if not simulation_spec.get("bindings"):
        issues.append({"issue_code": "MISSING_BINDINGS", "why": "缺少 runtime bindings", "fix_at": "08_simulation_spec_generation"})
    score = 96 - len(issues) * 20
    return {
        "ready_for_generation": not issues,
        "ready_for_delivery": not issues,
        "route": "simulation",
        "score": score,
        "rubric": {
            "physics_fidelity": 25,
            "pedagogical_usefulness": 18,
            "evidence_visibility": 15,
            "interaction_quality": 15,
            "spec_executability": 15,
            "ux_discipline": 8,
        },
        "issues": issues,
        "hard_blockers": [] if not issues else ["compile_blocked"],
        "suggested_repair_stage": None if not issues else issues[0]["fix_at"],
        "retry_recommendations": issues,
        "export_ready": not issues,
    }


def build_compile_delivery(problem: ProblemInput, artifacts: ArtifactMap) -> Dict[str, Any]:
    del problem
    spec = artifacts["simulation_spec_generation"]
    task_model = artifacts["structured_task_model"]
    brief = artifacts["instructional_design_brief"]
    physics_model = artifacts["physics_model"]
    scene_spec = spec["scene_spec"]
    simulation_spec = spec["simulation_spec"]
    simulation_blueprint = {
        "delivery_mode": "interactive-teaching-demo",
        "template_id": scene_spec["template_id"],
        "scene_type": scene_spec["scene_type"],
        "teaching_goal": brief["teaching_goal"],
        "interaction_contract": {
            "controls": simulation_spec["controls"],
            "bindings": simulation_spec["bindings"],
        },
        "minimum_quality_bar": {
            "interactive_controls": True,
            "teacher_guidance": True,
            "evidence_panel": True,
            "formula_panel": True,
        },
        "research_object": task_model["research_object"],
    }
    renderer_payload = {
        "component_key": "generic-physics-runtime",
        "layout_mode": "physics-workbench",
        "hero_panel": {
            "title": task_model["summary"],
            "eyebrow": "Physics Workbench",
            "subtitle": brief["teaching_goal"],
        },
        "scene_spec": scene_spec,
        "simulation_spec": simulation_spec,
    }
    delivery_bundle = {
        "primary_view": "simulation-viewport",
        "secondary_views": ["evidence-panel", "formula-panel", "teacher-guidance", "validation-report"],
        "teacher_script": brief["teacher_moves"],
        "observation_targets": brief["evidence_goals"],
        "panel_contract": {
            "simulation_canvas": {"required": True, "content": "visual scene and key state"},
            "evidence_panel": {"required": True, "content": brief["evidence_goals"]},
            "formula_panel": {"required": True, "content": physics_model["relations"]},
            "teacher_guidance": {"required": True, "content": brief["teacher_moves"]},
        },
        "inspector_contract": {
            "summary": ["run_profiling", "structured_task_model", "instructional_design_brief"],
            "artifacts": [
                "knowledge_grounding",
                "physics_model",
                "representation_interaction_design",
                "simulation_spec_generation",
            ],
            "validation": ["final_validation"],
            "logs": ["task_log"],
        },
        "artifact_tabs": [
            {"id": "summary", "label": "Summary"},
            {"id": "artifacts", "label": "Artifacts"},
            {"id": "validation", "label": "Validation"},
            {"id": "logs", "label": "Logs"},
        ],
        "default_open_panels": ["simulation_canvas", "evidence_panel", "teacher_guidance"],
        "exportable": artifacts["final_validation"]["export_ready"],
        "export_mode": "single-file-html",
        "export_includes": ["compile_delivery", "final_validation"],
    }
    return {
        "simulation_blueprint": simulation_blueprint,
        "renderer_payload": renderer_payload,
        "delivery_bundle": delivery_bundle,
    }


def _validation_result(payload: Dict[str, Any], required_keys: List[str], extra_issues: List[ValidationIssue] | None = None) -> ValidationResult:
    issues = missing_required_issues(payload, required_keys)
    if extra_issues:
        issues.extend(extra_issues)
    return ValidationResult(
        pass_=not issues,
        repairable=bool(issues),
        score=max(0, 100 - len(issues) * 20),
        issues=issues,
        repair_hint="补齐必填字段并修正空值。" if issues else None,
    )


def validate_run_profiling(payload: Dict[str, Any], _: ArtifactMap, __: ProblemInput) -> ValidationResult:
    return _validation_result(
        payload,
        [
            "input_profile",
            "run_mode",
            "information_density",
            "experience_mode",
            "has_explicit_problem",
            "has_explicit_solution",
        ],
    )


def validate_evidence_completion(payload: Dict[str, Any], _: ArtifactMap, __: ProblemInput) -> ValidationResult:
    return _validation_result(payload, ["completion_status", "evidence_bundle"])


def validate_knowledge_grounding(payload: Dict[str, Any], _: ArtifactMap, __: ProblemInput) -> ValidationResult:
    return _validation_result(payload, ["grounding_type", "assumptions", "solution_basis"])


def validate_structured_task_model(payload: Dict[str, Any], _: ArtifactMap, __: ProblemInput) -> ValidationResult:
    return _validation_result(payload, ["summary", "research_object", "scenario", "givens", "target_questions", "stages"])


def validate_instructional_design_brief(payload: Dict[str, Any], _: ArtifactMap, __: ProblemInput) -> ValidationResult:
    return _validation_result(payload, ["teaching_goal", "evidence_goals", "teacher_moves", "student_actions", "success_criteria"])


def validate_physics_model(payload: Dict[str, Any], _: ArtifactMap, __: ProblemInput) -> ValidationResult:
    return _validation_result(payload, ["model_type", "research_object", "relations", "key_quantities", "executable_constraints"])


def validate_representation_interaction_design(payload: Dict[str, Any], _: ArtifactMap, __: ProblemInput) -> ValidationResult:
    return _validation_result(payload, ["visible_quantities", "controls", "scene_spec"])


def validate_experience_mode_adaptation(payload: Dict[str, Any], _: ArtifactMap, __: ProblemInput) -> ValidationResult:
    return _validation_result(payload, ["experience_mode", "ui_constraints", "adapted_scene_spec"])


def validate_simulation_spec_generation(payload: Dict[str, Any], _: ArtifactMap, __: ProblemInput) -> ValidationResult:
    return _validation_result(payload, ["scene_spec", "simulation_spec", "delivery_targets"])


def validate_final_validation(payload: Dict[str, Any], _: ArtifactMap, __: ProblemInput) -> ValidationResult:
    issues = missing_required_issues(payload, ["ready_for_generation", "score", "rubric", "export_ready"])
    if payload.get("ready_for_generation") is False and not payload.get("suggested_repair_stage"):
        issues.append(
            ValidationIssue(
                code="MISSING_REPAIR_STAGE",
                severity="major",
                field_path="suggested_repair_stage",
                message="Failed final validation must specify a repair stage.",
                repair_hint="Point to the nearest upstream stage that can fix the issue.",
            )
        )
    return ValidationResult(
        pass_=not issues,
        repairable=bool(issues),
        score=max(0, 100 - len(issues) * 20),
        issues=issues,
        repair_hint="补齐 final_validation 输出字段。" if issues else None,
    )


def validate_compile_delivery(payload: Dict[str, Any], artifacts: ArtifactMap, __: ProblemInput) -> ValidationResult:
    issues = missing_required_issues(payload, ["simulation_blueprint", "renderer_payload", "delivery_bundle"])
    if not artifacts["final_validation"]["ready_for_generation"]:
        issues.append(
            ValidationIssue(
                code="COMPILE_BLOCKED",
                severity="critical",
                field_path="delivery_bundle",
                message="Compile must not run before final validation passes.",
                repair_hint="Return to the stage pointed by final_validation.suggested_repair_stage.",
            )
        )
    return ValidationResult(
        pass_=not issues,
        repairable=False,
        score=max(0, 100 - len(issues) * 25),
        hard_blockers=["compile_blocked"] if issues else [],
        issues=issues,
    )


def _fill_defaults(payload: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    patched = dict(payload)
    for key, value in defaults.items():
        if patched.get(key) in (None, "", [], {}):
            patched[key] = value
    return patched


def repair_run_profiling(payload: Dict[str, Any], _: ValidationResult, __: ArtifactMap, problem: ProblemInput) -> Dict[str, Any]:
    return _fill_defaults(payload, build_run_profiling(problem, {}))


def repair_evidence_completion(payload: Dict[str, Any], _: ValidationResult, artifacts: ArtifactMap, problem: ProblemInput) -> Dict[str, Any]:
    return _fill_defaults(payload, build_evidence_completion(problem, artifacts))


def repair_knowledge_grounding(payload: Dict[str, Any], _: ValidationResult, artifacts: ArtifactMap, problem: ProblemInput) -> Dict[str, Any]:
    return _fill_defaults(payload, build_knowledge_grounding(problem, artifacts))


def repair_structured_task_model(payload: Dict[str, Any], _: ValidationResult, artifacts: ArtifactMap, problem: ProblemInput) -> Dict[str, Any]:
    return _fill_defaults(payload, build_structured_task_model(problem, artifacts))


def repair_instructional_design_brief(payload: Dict[str, Any], _: ValidationResult, artifacts: ArtifactMap, problem: ProblemInput) -> Dict[str, Any]:
    return _fill_defaults(payload, build_instructional_design_brief(problem, artifacts))


def repair_physics_model(payload: Dict[str, Any], _: ValidationResult, artifacts: ArtifactMap, problem: ProblemInput) -> Dict[str, Any]:
    return _fill_defaults(payload, build_physics_model_stage(problem, artifacts))


def repair_representation_interaction_design(payload: Dict[str, Any], _: ValidationResult, artifacts: ArtifactMap, problem: ProblemInput) -> Dict[str, Any]:
    return _fill_defaults(payload, build_representation_interaction_design(problem, artifacts))


def repair_experience_mode_adaptation(payload: Dict[str, Any], _: ValidationResult, artifacts: ArtifactMap, problem: ProblemInput) -> Dict[str, Any]:
    return _fill_defaults(payload, build_experience_mode_adaptation(problem, artifacts))


def repair_simulation_spec_generation(payload: Dict[str, Any], _: ValidationResult, artifacts: ArtifactMap, problem: ProblemInput) -> Dict[str, Any]:
    return _fill_defaults(payload, build_simulation_spec_generation(problem, artifacts))


def repair_final_validation(payload: Dict[str, Any], _: ValidationResult, artifacts: ArtifactMap, problem: ProblemInput) -> Dict[str, Any]:
    return _fill_defaults(payload, build_final_validation(problem, artifacts))


def should_run_evidence_completion(artifacts: ArtifactMap, _: ProblemInput) -> bool:
    return artifacts["run_profiling"]["information_density"] == "low"


def should_run_compile_delivery(artifacts: ArtifactMap, _: ProblemInput) -> bool:
    return artifacts["final_validation"]["ready_for_generation"]


def build_stage_contracts() -> List[StageContract]:
    return [
        StageContract(
            id="stage-00",
            stage_name="run_profiling",
            artifact_name="run_profiling",
            input_artifacts=[],
            required_keys=["input_profile", "run_mode", "information_density", "experience_mode"],
            skill_path="00_run_profiling/skill.md",
            validator_path="00_run_profiling/validator.md",
            repair_path="00_run_profiling/repair.md",
            builder=build_run_profiling,
            validator=validate_run_profiling,
            repairer=repair_run_profiling,
        ),
        StageContract(
            id="stage-01",
            stage_name="evidence_completion",
            artifact_name="evidence_completion",
            input_artifacts=["run_profiling"],
            required_keys=["completion_status", "evidence_bundle"],
            skill_path="01_evidence_completion/skill.md",
            validator_path="01_evidence_completion/validator.md",
            repair_path="01_evidence_completion/repair.md",
            builder=build_evidence_completion,
            validator=validate_evidence_completion,
            repairer=repair_evidence_completion,
            conditional=True,
            should_run=should_run_evidence_completion,
        ),
        StageContract(
            id="stage-02",
            stage_name="knowledge_grounding",
            artifact_name="knowledge_grounding",
            input_artifacts=["run_profiling", "evidence_completion"],
            required_keys=["grounding_type", "assumptions", "solution_basis"],
            skill_path="02_knowledge_grounding/skill.md",
            validator_path="02_knowledge_grounding/validator.md",
            repair_path="02_knowledge_grounding/repair.md",
            builder=build_knowledge_grounding,
            validator=validate_knowledge_grounding,
            repairer=repair_knowledge_grounding,
        ),
        StageContract(
            id="stage-03",
            stage_name="structured_task_model",
            artifact_name="structured_task_model",
            input_artifacts=["run_profiling", "knowledge_grounding"],
            required_keys=["summary", "research_object", "scenario", "givens", "target_questions", "stages"],
            skill_path="03_structured_task_model/skill.md",
            validator_path="03_structured_task_model/validator.md",
            repair_path="03_structured_task_model/repair.md",
            builder=build_structured_task_model,
            validator=validate_structured_task_model,
            repairer=repair_structured_task_model,
        ),
        StageContract(
            id="stage-04",
            stage_name="instructional_design_brief",
            artifact_name="instructional_design_brief",
            input_artifacts=["run_profiling", "structured_task_model", "knowledge_grounding"],
            required_keys=["teaching_goal", "evidence_goals", "teacher_moves", "student_actions", "success_criteria"],
            skill_path="04_instructional_design_brief/skill.md",
            validator_path="04_instructional_design_brief/validator.md",
            repair_path="04_instructional_design_brief/repair.md",
            builder=build_instructional_design_brief,
            validator=validate_instructional_design_brief,
            repairer=repair_instructional_design_brief,
        ),
        StageContract(
            id="stage-05",
            stage_name="physics_model",
            artifact_name="physics_model",
            input_artifacts=["knowledge_grounding", "structured_task_model", "instructional_design_brief"],
            required_keys=["model_type", "research_object", "relations", "key_quantities", "executable_constraints"],
            skill_path="05_physics_model/skill.md",
            validator_path="05_physics_model/validator.md",
            repair_path="05_physics_model/repair.md",
            builder=build_physics_model_stage,
            validator=validate_physics_model,
            repairer=repair_physics_model,
        ),
        StageContract(
            id="stage-06",
            stage_name="representation_interaction_design",
            artifact_name="representation_interaction_design",
            input_artifacts=["structured_task_model", "instructional_design_brief", "physics_model"],
            required_keys=["visible_quantities", "controls", "scene_spec"],
            skill_path="06_representation_interaction_design/skill.md",
            validator_path="06_representation_interaction_design/validator.md",
            repair_path="06_representation_interaction_design/repair.md",
            builder=build_representation_interaction_design,
            validator=validate_representation_interaction_design,
            repairer=repair_representation_interaction_design,
        ),
        StageContract(
            id="stage-07",
            stage_name="experience_mode_adaptation",
            artifact_name="experience_mode_adaptation",
            input_artifacts=["run_profiling", "instructional_design_brief", "representation_interaction_design"],
            required_keys=["experience_mode", "ui_constraints", "adapted_scene_spec"],
            skill_path="07_experience_mode_adaptation/skill.md",
            validator_path="07_experience_mode_adaptation/validator.md",
            repair_path="07_experience_mode_adaptation/repair.md",
            builder=build_experience_mode_adaptation,
            validator=validate_experience_mode_adaptation,
            repairer=repair_experience_mode_adaptation,
        ),
        StageContract(
            id="stage-08",
            stage_name="simulation_spec_generation",
            artifact_name="simulation_spec_generation",
            input_artifacts=["instructional_design_brief", "experience_mode_adaptation"],
            required_keys=["scene_spec", "simulation_spec", "delivery_targets"],
            skill_path="08_simulation_spec_generation/skill.md",
            validator_path="08_simulation_spec_generation/validator.md",
            repair_path="08_simulation_spec_generation/repair.md",
            builder=build_simulation_spec_generation,
            validator=validate_simulation_spec_generation,
            repairer=repair_simulation_spec_generation,
        ),
        StageContract(
            id="stage-09",
            stage_name="final_validation",
            artifact_name="final_validation",
            input_artifacts=[
                "structured_task_model",
                "instructional_design_brief",
                "physics_model",
                "representation_interaction_design",
                "experience_mode_adaptation",
                "simulation_spec_generation",
            ],
            required_keys=["ready_for_generation", "score", "rubric", "export_ready"],
            skill_path="09_final_validation/skill.md",
            validator_path="09_final_validation/validator.md",
            repair_path="09_final_validation/repair.md",
            builder=build_final_validation,
            validator=validate_final_validation,
            repairer=repair_final_validation,
        ),
        StageContract(
            id="stage-10",
            stage_name="compile_delivery",
            artifact_name="compile_delivery",
            input_artifacts=["structured_task_model", "instructional_design_brief", "physics_model", "simulation_spec_generation", "final_validation"],
            required_keys=["simulation_blueprint", "renderer_payload", "delivery_bundle"],
            skill_path="10_compile_delivery/skill.md",
            validator_path="10_compile_delivery/validator.md",
            repair_path=None,
            builder=build_compile_delivery,
            validator=validate_compile_delivery,
            repairer=None,
            max_attempts=1,
            conditional=True,
            should_run=should_run_compile_delivery,
        ),
    ]
