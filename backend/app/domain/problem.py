from typing import List, Optional

from pydantic import BaseModel, Field


class ProblemStage(BaseModel):
    id: str
    label: str
    description: str
    contact_state: str
    key_question: str


class ProblemInput(BaseModel):
    text: str = Field(..., description="Original physics problem text.")
    subject_hint: Optional[str] = Field(default="high-school-physics")
    topic_hint: Optional[str] = Field(default=None)
    mode: str = Field(default="rule-based")
    debug: bool = Field(default=False)


class StructuredProblem(BaseModel):
    summary: str
    research_object: str
    scenario: str
    known_conditions: List[str] = Field(default_factory=list)
    target_questions: List[str] = Field(default_factory=list)
    explicit_constraints: List[str] = Field(default_factory=list)
    implicit_constraints: List[str] = Field(default_factory=list)
    key_actions: List[str] = Field(default_factory=list)
    stages: List[ProblemStage] = Field(default_factory=list)
