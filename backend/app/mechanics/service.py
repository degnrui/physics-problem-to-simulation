from __future__ import annotations

import copy
import os
from typing import Any, Dict, Optional

from backend.app.mechanics.executor import run_executor
from backend.app.mechanics.harness import (
    build_mechanics_harness_packet,
)
from backend.app.mechanics.parsing import normalize_mechanics_inputs
from backend.app.mechanics.runtime import render_mechanics_runtime_frame
from backend.app.mechanics.scene import compile_mechanics_scene


def _confidence(problem_text: bool, solution_text: bool, conflicts: int, issues: int) -> Dict[str, float]:
    extraction = 0.86 if problem_text else 0.38
    solution = 0.94 if solution_text else 0.52
    audit = max(0.2, 0.95 - 0.12 * conflicts - 0.05 * issues)
    overall = round(max(0.25, min(0.98, extraction * 0.35 + solution * 0.35 + audit * 0.30)), 2)
    return {
        "overall": overall,
        "problem_extraction": round(extraction, 2),
        "solution_alignment": round(solution, 2),
        "audit": round(audit, 2),
    }


def recognize_mechanics_problem(
    *,
    problem_text: Optional[str],
    solution_text: Optional[str],
    final_answers: Optional[str],
    image_bytes: Optional[bytes] = None,
    image_filename: Optional[str] = None,
    preferred_model_id: Optional[str] = None,
) -> Dict[str, Any]:
    normalized = normalize_mechanics_inputs(
        problem_text=problem_text,
        solution_text=solution_text,
        final_answers=final_answers,
        image_bytes=image_bytes,
        image_filename=image_filename,
    )
    harness = build_mechanics_harness_packet(normalized)
    executor_mode = os.getenv("EXECUTOR_MODE", harness.get("executor", "dev_proxy"))
    executor_run = run_executor(
        harness,
        {"mode": executor_mode},
        preferred_model_id=preferred_model_id,
    )
    confidence_breakdown = _confidence(
        normalized["has_problem_text"],
        normalized["has_solution_text"],
        len(executor_run["conflict_items"]),
        len(executor_run["issues"]),
    )
    needs_confirmation = bool(executor_run["conflict_items"]) or not normalized["has_solution_text"]

    return {
        "reference_image": normalized["reference_image"],
        "harness": harness,
        "executor_run": {
            "executor": executor_run["executor"],
            "tool_trace": executor_run["tool_trace"],
            "intermediate_artifacts": executor_run["intermediate_artifacts"],
            "runtime_warnings": executor_run.get("runtime_warnings", []),
        },
        "problem_representation": executor_run["problem_representation"],
        "candidate_models": executor_run["candidate_models"],
        "selected_model": executor_run["selected_model"],
        "solution_model": executor_run["solution_model"],
        "conflict_items": executor_run["conflict_items"],
        "simulation": executor_run["simulation"],
        "verification_report": executor_run["verification_report"],
        "final_simulation_spec": executor_run["final_simulation_spec"],
        "needs_confirmation": needs_confirmation,
        "confidence_breakdown": confidence_breakdown,
        "issues": executor_run["issues"],
        "execution_mode": executor_mode,
        "normalized_input": {
            "problem_text": normalized["problem_text"],
            "solution_text": normalized["solution_text"],
            "final_answers": normalized["final_answers"],
            "has_image": normalized["has_image"],
        },
    }


def apply_mechanics_confirmation(
    session_payload: Dict[str, Any],
    updates: Dict[str, Any],
) -> Dict[str, Any]:
    normalized = copy.deepcopy(session_payload.get("normalized_input", {}))
    problem_text = normalized.get("problem_text")
    solution_text = normalized.get("solution_text")
    final_answers = normalized.get("final_answers")
    preferred_model_id = updates.get("selected_model_id") or session_payload.get("selected_model", {}).get("id")

    confirmed = recognize_mechanics_problem(
        problem_text=problem_text,
        solution_text=solution_text,
        final_answers=final_answers,
        preferred_model_id=preferred_model_id,
    )
    if updates.get("assumption_overrides"):
        for candidate in confirmed["candidate_models"]:
            if candidate["id"] == confirmed["selected_model"]["id"]:
                candidate["assumptions"].update(updates["assumption_overrides"])
                confirmed["selected_model"] = candidate
                break
    confirmed["needs_confirmation"] = False
    confirmed["conflict_items"] = []
    confirmed["issues"] = []
    return confirmed


def generate_mechanics_scene(session_payload: Dict[str, Any]) -> Dict[str, Any]:
    scene = compile_mechanics_scene(
        session_id=session_payload["session_id"],
        problem_representation=session_payload["problem_representation"],
        simulation_spec=session_payload["final_simulation_spec"],
        selected_model=session_payload["selected_model"],
    )
    payload = {
        "scene": scene.model_dump(),
        "verification_report": session_payload["verification_report"],
        "final_simulation_spec": session_payload["final_simulation_spec"],
    }
    session_payload["teaching_scene"] = payload["scene"]
    return payload


def simulate_mechanics_scene(
    session_payload: Dict[str, Any],
    *,
    stage_id: str,
    progress: float,
) -> Dict[str, Any]:
    scene_payload = session_payload.get("teaching_scene")
    if not scene_payload:
        scene_payload = generate_mechanics_scene(session_payload)["scene"]

    frame = render_mechanics_runtime_frame(
        scene=compile_mechanics_scene(
            session_id=session_payload["session_id"],
            problem_representation=session_payload["problem_representation"],
            simulation_spec=session_payload["final_simulation_spec"],
            selected_model=session_payload["selected_model"],
        ),
        stage_id=stage_id,
        progress=progress,
        simulation_spec=session_payload["final_simulation_spec"],
    )
    stage = next(
        (item for item in scene_payload["stages"] if item["id"] == stage_id),
        scene_payload["stages"][0],
    )
    return {
        "scene": scene_payload,
        "stage": stage,
        "frame": frame.model_dump(),
        "verification_report": session_payload["verification_report"],
    }
