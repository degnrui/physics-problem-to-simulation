from fastapi import APIRouter

from backend.app.domain.problem import ProblemInput
from backend.app.pipeline.problem_to_simulation import run_problem_to_simulation

router = APIRouter()


@router.post("/problem-to-simulation")
def problem_to_simulation(payload: ProblemInput) -> dict:
    result = run_problem_to_simulation(payload)
    return result.model_dump()

