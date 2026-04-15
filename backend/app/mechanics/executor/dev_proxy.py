from __future__ import annotations

from typing import Any, Dict, Optional

from backend.app.mechanics.tools import (
    audit_selected_candidate_tool,
    build_candidate_models_tool,
    extract_problem_representation_tool,
    extract_solution_model_tool,
    select_best_candidate_tool,
    simulate_candidate_models_tool,
)


def _trace(tool: str, summary: str, artifact_key: str) -> Dict[str, str]:
    return {"tool": tool, "summary": summary, "artifact_key": artifact_key}


def run_dev_proxy_executor(
    harness_packet: Dict[str, Any],
    preferred_model_id: Optional[str] = None,
) -> Dict[str, Any]:
    normalized = dict(harness_packet.get("inputs", {}))
    tool_trace = []
    intermediate_artifacts: Dict[str, Any] = {}

    problem_representation = extract_problem_representation_tool(normalized)
    intermediate_artifacts["problem_representation"] = problem_representation.model_dump()
    tool_trace.append(
        _trace("extract_problem_representation", "从题干抽取对象、量和阶段。", "problem_representation")
    )

    candidate_models = build_candidate_models_tool(problem_representation)
    intermediate_artifacts["candidate_models"] = [item.model_dump() for item in candidate_models]
    tool_trace.append(_trace("build_candidate_models", "构建候选物理模型。", "candidate_models"))

    solution_model = extract_solution_model_tool(normalized)
    intermediate_artifacts["solution_model"] = solution_model.model_dump()
    tool_trace.append(_trace("extract_solution_model", "从解析与答案抽取步骤图。", "solution_model"))

    simulations = simulate_candidate_models_tool(problem_representation, candidate_models, solution_model)
    intermediate_artifacts["candidate_simulations"] = {
        key: value.model_dump() for key, value in simulations.items()
    }
    tool_trace.append(
        _trace("simulate_candidate_models", "对候选模型执行分段仿真与数值回证。", "candidate_simulations")
    )

    selected_model, simulation = select_best_candidate_tool(
        candidate_models, simulations, solution_model, preferred_model_id=preferred_model_id
    )
    intermediate_artifacts["selected_model"] = selected_model.model_dump()
    tool_trace.append(_trace("select_best_candidate", "结合解析与结果选择当前模型。", "selected_model"))

    audit = audit_selected_candidate_tool(problem_representation, selected_model, simulation, solution_model)
    intermediate_artifacts["audit"] = {
        "issues": [item.model_dump() for item in audit["issues"]],
        "conflicts": [item.model_dump() for item in audit["conflicts"]],
    }
    tool_trace.append(_trace("audit_selected_candidate", "执行冲突审计与护栏检查。", "audit"))

    verification_report = {
        "status": "blocked" if audit["conflicts"] else "passed",
        "checks": [
            {
                "name": "answer_alignment",
                "passed": not any(item.kind == "answer_mismatch" for item in audit["conflicts"]),
            },
            {
                "name": "solution_completeness",
                "passed": solution_model.available,
            },
            {
                "name": "guardrail_audit",
                "passed": len(audit["conflicts"]) == 0,
            },
        ],
        "issue_count": len(audit["issues"]),
        "conflict_count": len(audit["conflicts"]),
    }

    return {
        "executor": "dev_proxy",
        "tool_trace": tool_trace,
        "intermediate_artifacts": intermediate_artifacts,
        "problem_representation": problem_representation.model_dump(),
        "candidate_models": [item.model_dump() for item in candidate_models],
        "selected_model": selected_model.model_dump(),
        "solution_model": solution_model.model_dump(),
        "conflict_items": [item.model_dump() for item in audit["conflicts"]],
        "issues": [item.model_dump() for item in audit["issues"]],
        "verification_report": verification_report,
        "simulation": simulation.model_dump(),
        "final_simulation_spec": simulation.model_dump(),
    }
