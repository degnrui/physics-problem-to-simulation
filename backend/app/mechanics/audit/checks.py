from __future__ import annotations

from typing import Dict, List

from backend.app.schemas.mechanics import (
    MechanicsCandidateModel,
    MechanicsConflictItem,
    MechanicsIssue,
    MechanicsProblemRepresentation,
    MechanicsSimulationResult,
    MechanicsSolutionModel,
)


def audit_mechanics_models(
    problem: MechanicsProblemRepresentation,
    candidate: MechanicsCandidateModel,
    simulation: MechanicsSimulationResult,
    solution: MechanicsSolutionModel,
) -> Dict[str, List]:
    issues: List[MechanicsIssue] = []
    conflicts: List[MechanicsConflictItem] = []

    if not problem.source_fragments:
        conflicts.append(
            MechanicsConflictItem(
                id="missing-problem-text",
                kind="insufficient_input",
                severity="error",
                message="缺少可用于抽模的题干文本。",
                recommendation="补充题干文本或人工确认模型。",
            )
        )

    if not solution.available:
        issues.append(
            MechanicsIssue(
                id="missing-solution",
                message="未提供完整解析，系统仅能依据题干和最终答案做降级校验。",
                target="solution_text",
            )
        )
        conflicts.append(
            MechanicsConflictItem(
                id="solution-missing",
                kind="insufficient_input",
                severity="warning",
                message="缺少完整解析，建议教师确认关键假设后再采用。",
                recommendation="补充完整解析或在确认页锁定候选模型。",
            )
        )
    else:
        if "动能定理" not in solution.laws:
            conflicts.append(
                MechanicsConflictItem(
                    id="law-kinetic-missing",
                    kind="law_mismatch",
                    severity="warning",
                    message="解析中未识别到动能定理，但题干模型依赖该定律。",
                    recommendation="检查解析文本是否缺失关键步骤。",
                )
            )
        for key, answer in simulation.answers.items():
            expected = solution.answer_map.get(key)
            if expected and not answer.matches_reference:
                conflicts.append(
                    MechanicsConflictItem(
                        id=f"answer-{key}",
                        kind="answer_mismatch",
                        severity="error",
                        message=f"{answer.label} 与参考答案不一致。",
                        target=key,
                        expected=expected,
                        actual=answer.display_value,
                        recommendation="默认拦截，请教师确认后再采用。",
                    )
                )

    if candidate.id == "belt_arc_guarded":
        conflicts.append(
            MechanicsConflictItem(
                id="guarded-model",
                kind="assumption_gap",
                severity="warning",
                message="当前为保守候选模型，圆弧阶段假设尚未锁定。",
                recommendation="优先确认是否采用传送带共速 + 可动圆弧守恒模型。",
            )
        )

    return {"issues": issues, "conflicts": conflicts}
