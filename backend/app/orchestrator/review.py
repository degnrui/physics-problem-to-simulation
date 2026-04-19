from __future__ import annotations

from typing import Any, Callable, Dict, List

from .state import append_trace, set_stage_status

Inputs = Dict[str, Dict[str, Any]]
Worker = Callable[[Inputs, Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
Validator = Callable[[Dict[str, Any], Inputs, Dict[str, Any], Dict[str, Any]], List[Dict[str, Any]]]
Repairer = Callable[[Dict[str, Any], List[Dict[str, Any]], Inputs, Dict[str, Any], Dict[str, Any]], Dict[str, Any]]
Approver = Callable[[Dict[str, Any], Inputs, Dict[str, Any], Dict[str, Any]], List[Dict[str, Any]]]


class StageFailure(RuntimeError):
    def __init__(self, stage: str, issues: List[Dict[str, Any]]) -> None:
        super().__init__(stage)
        self.stage = stage
        self.issues = issues


class StageRetry(RuntimeError):
    def __init__(self, stage: str, retry_stage: str, issues: List[Dict[str, Any]]) -> None:
        super().__init__(stage)
        self.stage = stage
        self.retry_stage = retry_stage
        self.issues = issues


def run_stage_review(
    *,
    state: Dict[str, Any],
    stage: str,
    inputs: Inputs,
    worker: Worker,
    validator: Validator,
    approver: Approver,
    context: Dict[str, Any],
    repairer: Repairer | None = None,
    max_attempts: int = 2,
    retry_stage: str | None = None,
) -> Dict[str, Any]:
    stage_skillpack = context["skillpack_store"].load(stage)
    stage_context = {**context, "stage_skillpack": stage_skillpack}
    append_trace(
        state,
        stage=stage,
        event="skillpack_loaded",
        details={
            "path": stage_skillpack["relative_dir"],
            "skill_path": stage_skillpack["skill_relative_path"],
        },
    )
    attempts = 0
    candidate = worker(inputs, state, stage_context)
    append_trace(state, stage=stage, event="generated", details={"attempt": 1})

    while attempts < max_attempts:
        attempts += 1
        state["active_stage"] = stage
        state["artifacts"][stage] = candidate
        context["artifact_store"].write_json_artifact(stage, candidate)

        issues = validator(candidate, inputs, state, stage_context)
        if not issues:
            issues = approver(candidate, inputs, state, stage_context)

        if not issues:
            state["approved_artifacts"][stage] = candidate
            context["artifact_store"].write_json_artifact(stage, candidate)
            set_stage_status(state, stage=stage, status="approved", attempts=attempts, issues=[])
            append_trace(state, stage=stage, event="approved", details={"attempt": attempts})
            return candidate

        if repairer is None:
            if retry_stage:
                set_stage_status(state, stage=stage, status="needs_repair", attempts=attempts, issues=issues)
                append_trace(
                    state,
                    stage=stage,
                    event="retry_requested",
                    details={"attempt": attempts, "issues": issues, "retry_stage": retry_stage},
                )
                raise StageRetry(stage, retry_stage, issues)
            set_stage_status(state, stage=stage, status="failed", attempts=attempts, issues=issues)
            append_trace(state, stage=stage, event="failed", details={"attempt": attempts, "issues": issues})
            raise StageFailure(stage, issues)

        if attempts >= max_attempts:
            set_stage_status(state, stage=stage, status="failed", attempts=attempts, issues=issues)
            append_trace(state, stage=stage, event="failed", details={"attempt": attempts, "issues": issues})
            raise StageFailure(stage, issues)

        set_stage_status(state, stage=stage, status="needs_repair", attempts=attempts, issues=issues)
        append_trace(state, stage=stage, event="repair_requested", details={"attempt": attempts, "issues": issues})
        candidate = repairer(candidate, issues, inputs, state, stage_context)
        append_trace(state, stage=stage, event="repair_applied", details={"attempt": attempts + 1})

    raise StageFailure(stage, [{"code": "UNREACHABLE", "message": "review loop exhausted"}])
