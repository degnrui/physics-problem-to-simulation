from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from app.domain.problem import ProblemInput

ArtifactMap = Dict[str, Dict[str, Any]]
StageBuilder = Callable[[ProblemInput, ArtifactMap], Dict[str, Any]]
StageValidator = Callable[[Dict[str, Any], ArtifactMap, ProblemInput], "ValidationResult"]
StageRepairer = Callable[[Dict[str, Any], "ValidationResult", ArtifactMap, ProblemInput], Dict[str, Any]]
StageCondition = Callable[[ArtifactMap, ProblemInput], bool]


@dataclass
class ValidationIssue:
    code: str
    severity: str
    field_path: str
    message: str
    repair_hint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "severity": self.severity,
            "field_path": self.field_path,
            "message": self.message,
            "repair_hint": self.repair_hint,
        }


@dataclass
class ValidationResult:
    pass_: bool
    repairable: bool
    score: int
    hard_blockers: List[str] = field(default_factory=list)
    issues: List[ValidationIssue] = field(default_factory=list)
    repair_hint: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pass": self.pass_,
            "repairable": self.repairable,
            "score": self.score,
            "hard_blockers": self.hard_blockers,
            "issues": [issue.to_dict() for issue in self.issues],
            "repair_hint": self.repair_hint,
        }


@dataclass
class StageContract:
    id: str
    stage_name: str
    artifact_name: str
    input_artifacts: List[str]
    required_keys: List[str]
    skill_path: str
    validator_path: str
    repair_path: Optional[str]
    builder: StageBuilder
    validator: StageValidator
    repairer: Optional[StageRepairer] = None
    max_attempts: int = 2
    conditional: bool = False
    should_run: Optional[StageCondition] = None


def validation_ok(score: int = 100) -> ValidationResult:
    return ValidationResult(pass_=True, repairable=False, score=score)


def missing_required_issues(payload: Dict[str, Any], required_keys: List[str]) -> List[ValidationIssue]:
    issues: List[ValidationIssue] = []
    for key in required_keys:
        value = payload.get(key)
        if value in (None, "", [], {}):
            issues.append(
                ValidationIssue(
                    code="MISSING_REQUIRED_FIELD",
                    severity="major",
                    field_path=key,
                    message=f"Missing or empty required field `{key}`.",
                    repair_hint=f"Populate `{key}` with a non-empty value.",
                )
            )
    return issues
