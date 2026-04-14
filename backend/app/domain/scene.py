from pydantic import BaseModel


class SimulationScene(BaseModel):
    scene_type: str
    template_id: str
    parameters: dict[str, float | str | bool] = {}
    notes: list[str] = []


class ProblemToSimulationResult(BaseModel):
    problem_summary: str
    structured_problem: dict
    physics_model: dict
    scene: dict
    warnings: list[str] = []

