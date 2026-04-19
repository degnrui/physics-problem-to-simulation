from __future__ import annotations

from typing import Any, Dict, List

from app.harness.stage_builders import build_stage_contracts


def build_task_plan(run_profiling: Dict[str, Any]) -> Dict[str, object]:
    tasks: List[Dict[str, object]] = []
    for contract in build_stage_contracts():
        tasks.append(
            {
                "id": contract.id,
                "type": contract.stage_name,
                "artifact_name": contract.artifact_name,
                "worker": "stage_runtime",
                "conditional": contract.conditional,
                "input_artifacts": contract.input_artifacts,
            }
        )

    return {
        "input_profile": run_profiling["input_profile"],
        "run_mode": run_profiling["run_mode"],
        "information_density": run_profiling["information_density"],
        "experience_mode": run_profiling["experience_mode"],
        "tasks": tasks,
    }
