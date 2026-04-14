from pydantic import BaseModel, Field


class ProblemInput(BaseModel):
    text: str = Field(..., description="Original physics problem text.")
    subject_hint: str | None = Field(default="high-school-physics")
    topic_hint: str | None = Field(default=None)


class StructuredProblem(BaseModel):
    summary: str
    knowns: list[str] = []
    unknowns: list[str] = []
    assumptions: list[str] = []

