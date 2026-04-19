from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from app.domain.problem import ProblemInput
from app.harness.orchestrator import (
    create_problem_to_simulation_run,
    delete_run,
    export_html_path,
    export_run_html,
    list_recent_runs,
    plan_problem_to_simulation,
    read_run_artifact,
    read_run_result,
    read_run_status,
    run_problem_to_simulation_harness,
)

router = APIRouter()


def _runs_root(request: Request) -> Optional[Path]:
    return getattr(request.app.state, "runs_root", None)


@router.post("/problem-to-simulation")
def problem_to_simulation(payload: ProblemInput) -> dict:
    return run_problem_to_simulation_harness(payload, runs_root=None)


@router.post("/problem-to-simulation/plan")
def problem_to_simulation_plan(payload: ProblemInput) -> dict:
    return plan_problem_to_simulation(payload)


@router.post("/problem-to-simulation/run")
def problem_to_simulation_run(payload: ProblemInput) -> dict:
    return run_problem_to_simulation_harness(payload)


@router.post("/problem-to-simulation/runs", status_code=202)
def create_run(payload: ProblemInput, request: Request) -> dict:
    return create_problem_to_simulation_run(payload, runs_root=_runs_root(request))


@router.get("/problem-to-simulation/runs")
def get_recent_runs(request: Request) -> dict:
    return list_recent_runs(runs_root=_runs_root(request))


@router.get("/problem-to-simulation/runs/{run_id}")
def get_run_status(run_id: str, request: Request) -> dict:
    try:
        return read_run_status(run_id, runs_root=_runs_root(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc


@router.delete("/problem-to-simulation/runs/{run_id}")
def remove_run(run_id: str, request: Request) -> dict:
    try:
        return delete_run(run_id, runs_root=_runs_root(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Run not found") from exc


@router.get("/problem-to-simulation/runs/{run_id}/result")
def get_run_result(run_id: str, request: Request) -> dict:
    status = read_run_status(run_id, runs_root=_runs_root(request))
    if status["status"] != "completed":
        raise HTTPException(status_code=409, detail="Run is not completed")
    return read_run_result(run_id, runs_root=_runs_root(request))


@router.get("/problem-to-simulation/runs/{run_id}/artifacts/{artifact_name}")
def get_run_artifact(run_id: str, artifact_name: str, request: Request) -> dict:
    try:
        return read_run_artifact(run_id, artifact_name, runs_root=_runs_root(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Artifact not found") from exc


@router.post("/problem-to-simulation/runs/{run_id}/export-html")
def create_run_export(run_id: str, request: Request) -> dict:
    status = read_run_status(run_id, runs_root=_runs_root(request))
    if status["status"] != "completed":
        raise HTTPException(status_code=409, detail="Run is not completed")
    result = read_run_result(run_id, runs_root=_runs_root(request))
    if not result["final_validation"].get("export_ready"):
        raise HTTPException(status_code=409, detail="Run is not exportable")
    return export_run_html(run_id, runs_root=_runs_root(request))


@router.get("/problem-to-simulation/runs/{run_id}/export-html")
def get_run_export(run_id: str, request: Request) -> FileResponse:
    try:
        path = export_html_path(run_id, runs_root=_runs_root(request))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Export not found") from exc
    if not path.exists():
        raise HTTPException(status_code=404, detail="Export not found")
    return FileResponse(path, media_type="text/html; charset=utf-8", filename="simulation.html")
