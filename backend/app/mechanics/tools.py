from __future__ import annotations

from typing import Any, Dict, List

from backend.app.mechanics.alignment import select_best_candidate
from backend.app.mechanics.audit import audit_mechanics_models
from backend.app.mechanics.extraction import (
    build_candidate_models,
    extract_problem_representation,
    extract_solution_model,
)
from backend.app.mechanics.simulation import simulate_candidate_model


def extract_problem_representation_tool(normalized: Dict[str, Any]):
    return extract_problem_representation(normalized)


def build_candidate_models_tool(problem_representation):
    return build_candidate_models(problem_representation)


def extract_solution_model_tool(normalized: Dict[str, Any]):
    return extract_solution_model(normalized)


def simulate_candidate_models_tool(problem_representation, candidates, solution_model):
    return {
        candidate.id: simulate_candidate_model(
            problem_representation, candidate, expected_answers=solution_model.answer_map
        )
        for candidate in candidates
    }


def select_best_candidate_tool(candidates, simulations, solution_model, preferred_model_id=None):
    return select_best_candidate(
        candidates, simulations, solution_model, preferred_model_id=preferred_model_id
    )


def audit_selected_candidate_tool(problem_representation, selected_model, simulation, solution_model):
    return audit_mechanics_models(problem_representation, selected_model, simulation, solution_model)
