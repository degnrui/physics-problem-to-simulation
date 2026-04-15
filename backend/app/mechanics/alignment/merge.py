from __future__ import annotations

from typing import Dict, Iterable, Tuple

from backend.app.schemas.mechanics import (
    MechanicsCandidateModel,
    MechanicsSimulationResult,
    MechanicsSolutionModel,
)


def _score_candidate(
    candidate: MechanicsCandidateModel,
    simulation: MechanicsSimulationResult,
    solution: MechanicsSolutionModel,
) -> float:
    score = candidate.confidence
    if solution.available:
        matches = [answer.matches_reference for answer in simulation.answers.values() if answer.matches_reference is not None]
        score += 0.15 * sum(1 for item in matches if item)
        score -= 0.25 * sum(1 for item in matches if not item)
        shared_laws = len(set(candidate.governing_laws) & set(solution.laws))
        score += 0.03 * shared_laws
    return score


def select_best_candidate(
    candidates: Iterable[MechanicsCandidateModel],
    simulations: Dict[str, MechanicsSimulationResult],
    solution: MechanicsSolutionModel,
    preferred_model_id: str | None = None,
) -> Tuple[MechanicsCandidateModel, MechanicsSimulationResult]:
    candidate_map = {candidate.id: candidate for candidate in candidates}
    if preferred_model_id and preferred_model_id in candidate_map:
        chosen = candidate_map[preferred_model_id]
        return chosen, simulations[chosen.id]

    ranked = sorted(
        ((candidate, simulations[candidate.id], _score_candidate(candidate, simulations[candidate.id], solution)) for candidate in candidate_map.values()),
        key=lambda item: item[2],
        reverse=True,
    )
    best_candidate, best_simulation, _ = ranked[0]
    return best_candidate, best_simulation
