from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List

MAIN_STAGE_ORDER = [
    "request_analysis",
    "evidence_ingestion",
    "domain_grounding",
    "instructional_modeling",
    "simulation_design",
    "runtime_package_assembly",
    "code_generation",
    "runtime_validation",
]

SIMULATION_DESIGN_SUBGRAPH = [
    "scene_design",
    "control_design",
    "chart_measurement_design",
    "pedagogical_view_design",
    "design_merge",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def score_from_issues(issues: List[Dict[str, Any]]) -> int:
    return max(0, 100 - len(issues) * 20)


def new_stage_status(name: str, status: str = "pending") -> Dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "attempts": 0,
        "score": 0,
        "issues": [],
    }


def build_initial_stage_status() -> Dict[str, Dict[str, Any]]:
    status = {name: new_stage_status(name) for name in MAIN_STAGE_ORDER}
    status.update({name: new_stage_status(name) for name in SIMULATION_DESIGN_SUBGRAPH})
    return status


def new_run_state(request_text: str, request_profile: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "run_id": "",
        "request_text": request_text,
        "request_mode": "new_simulation",
        "request_profile": deepcopy(request_profile),
        "workflow_plan": [],
        "active_stage": "queued",
        "artifacts": {},
        "approved_artifacts": {},
        "stage_status": build_initial_stage_status(),
        "execution_trace": [],
        "runtime_package": None,
        "generated_files": {},
        "delivery_runtime": None,
        "final_result": None,
    }


def append_trace(
    state: Dict[str, Any],
    *,
    stage: str,
    event: str,
    details: Dict[str, Any] | None = None,
) -> None:
    entry = {
        "timestamp": utc_now_iso(),
        "stage": stage,
        "event": event,
    }
    if details:
        entry.update(details)
    state["execution_trace"].append(entry)


def set_stage_status(
    state: Dict[str, Any],
    *,
    stage: str,
    status: str,
    attempts: int,
    issues: List[Dict[str, Any]],
) -> None:
    state["stage_status"][stage] = {
        "name": stage,
        "status": status,
        "attempts": attempts,
        "score": score_from_issues(issues),
        "issues": issues,
    }

