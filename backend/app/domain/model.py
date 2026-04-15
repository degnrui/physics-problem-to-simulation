from typing import Dict, List

from pydantic import BaseModel, Field


class ForceItem(BaseModel):
    name: str
    direction: str
    magnitude: str
    category: str


class ForceCase(BaseModel):
    stage_id: str
    stage_label: str
    forces: List[ForceItem] = Field(default_factory=list)
    motion_state: str
    focus: str


class PhysicsModel(BaseModel):
    model_type: str
    research_object: str
    scenario: str
    forces: List[ForceItem] = Field(default_factory=list)
    force_cases: List[ForceCase] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    motion_state: str
    core_principles: List[str] = Field(default_factory=list)
    misconceptions: List[str] = Field(default_factory=list)
    derived_quantities: Dict[str, str] = Field(default_factory=dict)
