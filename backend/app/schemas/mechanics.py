from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


IssueLevel = Literal["warning", "error"]
ConflictKind = Literal[
    "answer_mismatch",
    "law_mismatch",
    "insufficient_input",
    "assumption_gap",
]


class MechanicsIssue(BaseModel):
    id: str
    level: IssueLevel = "warning"
    message: str
    target: Optional[str] = None


class MechanicsConflictItem(BaseModel):
    id: str
    kind: ConflictKind
    severity: Literal["warning", "error"] = "warning"
    message: str
    target: Optional[str] = None
    expected: Optional[str] = None
    actual: Optional[str] = None
    recommendation: Optional[str] = None


class MechanicsQuantity(BaseModel):
    symbol: str
    value: Optional[float] = None
    unit: Optional[str] = None
    text: Optional[str] = None
    source: str = "text"


class MechanicsObject(BaseModel):
    id: str
    label: str
    category: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class MechanicsProblemRepresentation(BaseModel):
    summary: str
    objects: List[MechanicsObject] = Field(default_factory=list)
    known_quantities: List[MechanicsQuantity] = Field(default_factory=list)
    unknown_quantities: List[MechanicsQuantity] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    geometry: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    goals: List[str] = Field(default_factory=list)
    stages: List[str] = Field(default_factory=list)
    source_fragments: List[str] = Field(default_factory=list)


class MechanicsCandidateModel(BaseModel):
    id: str
    title: str
    confidence: float = Field(ge=0.0, le=1.0)
    state_variables: List[str] = Field(default_factory=list)
    governing_laws: List[str] = Field(default_factory=list)
    assumptions: Dict[str, bool] = Field(default_factory=dict)
    approximations: List[str] = Field(default_factory=list)
    applicability: List[str] = Field(default_factory=list)
    stage_map: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)


class MechanicsSolutionStep(BaseModel):
    id: str
    prompt: str
    law: Optional[str] = None
    equation: Optional[str] = None
    conclusion: Optional[str] = None
    evidence: Optional[str] = None


class MechanicsSolutionModel(BaseModel):
    available: bool = False
    answer_map: Dict[str, str] = Field(default_factory=dict)
    laws: List[str] = Field(default_factory=list)
    steps: List[MechanicsSolutionStep] = Field(default_factory=list)
    source_fragments: List[str] = Field(default_factory=list)


class MechanicsAnswerResult(BaseModel):
    key: str
    label: str
    value: float
    unit: str
    display_value: str
    expected_value: Optional[str] = None
    matches_reference: Optional[bool] = None


class MechanicsSimulationResult(BaseModel):
    model_id: str
    answers: Dict[str, MechanicsAnswerResult]
    stage_results: Dict[str, Any] = Field(default_factory=dict)
    derived_values: Dict[str, float] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)
    plots: List[Dict[str, Any]] = Field(default_factory=list)


class MechanicsRecognitionSession(BaseModel):
    session_id: str
    created_at: str
    reference_image: Dict[str, str]
    problem_representation: MechanicsProblemRepresentation
    candidate_models: List[MechanicsCandidateModel]
    selected_model: Optional[MechanicsCandidateModel] = None
    solution_model: MechanicsSolutionModel
    conflict_items: List[MechanicsConflictItem] = Field(default_factory=list)
    simulation: Optional[MechanicsSimulationResult] = None
    needs_confirmation: bool = True
    confidence_breakdown: Dict[str, float] = Field(default_factory=dict)
    issues: List[MechanicsIssue] = Field(default_factory=list)
    normalized_input: Dict[str, Any] = Field(default_factory=dict)
