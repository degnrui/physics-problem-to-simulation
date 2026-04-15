from typing import Any, Dict, List

from pydantic import BaseModel, Field


class SimulationScene(BaseModel):
    scene_type: str
    template_id: str
    coordinate_system: str
    visual_elements: List[Dict[str, Any]] = Field(default_factory=list)
    controls: List[Dict[str, Any]] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    notes: List[str] = Field(default_factory=list)


class StageLog(BaseModel):
    task_id: str
    task_type: str
    status: str
    input_summary: str
    output_digest: str
    warnings: List[str] = Field(default_factory=list)
    debug_notes: List[str] = Field(default_factory=list)
    next_task: str = ""


class ProblemToSimulationResult(BaseModel):
    problem_summary: str
    structured_problem: Dict[str, Any]
    physics_model: Dict[str, Any]
    scene: Dict[str, Any]
    stage_logs: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
