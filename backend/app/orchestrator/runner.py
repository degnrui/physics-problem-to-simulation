from __future__ import annotations

import json
import shutil
import threading
import uuid
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from app.domain.problem import ProblemInput
from app.skillpacks import SkillpackStore
from app.runtime import RuntimeArtifactStore, RuntimeGeneratorClient, export_delivery_runtime

from .checkpoints import CheckpointStore
from .graph import create_coordinator_graph
from .planner import analyze_request_text
from .review import StageFailure
from .state import MAIN_STAGE_ORDER, append_trace, new_run_state, utc_now_iso

_RUN_LOCK = threading.Lock()


def _default_runs_root() -> Path:
    return Path(__file__).resolve().parents[3] / "runs"


def _create_run_dir(runs_root: Path) -> Tuple[str, Path]:
    run_id = utc_now_iso().replace(":", "").replace("-", "").replace(".", "") + "-" + uuid.uuid4().hex[:8]
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_id, run_dir


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def _result_payload(state: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "run_id": state["run_id"],
        "run_state": {
            "request_mode": state["request_mode"],
            "request_profile": state["request_profile"],
            "workflow_plan": state["workflow_plan"],
            "active_stage": state["active_stage"],
            "stage_status": state["stage_status"],
        },
        "artifacts": state["artifacts"],
        "approved_artifacts": state["approved_artifacts"],
        "runtime_package": state["runtime_package"],
        "generated_files": state["generated_files"],
        "delivery_runtime": state["delivery_runtime"],
        "execution_trace": state["execution_trace"],
    }


def plan_problem_to_simulation(problem: ProblemInput) -> Dict[str, Any]:
    request_profile = {
        "subject_hint": problem.subject_hint,
        "topic_hint": problem.topic_hint,
        "mode": problem.mode,
        "debug": problem.debug,
    }
    state = new_run_state(problem.text, request_profile)
    analysis = analyze_request_text(problem.text)
    state["request_mode"] = analysis["request_mode"]
    state["workflow_plan"] = analysis["recommended_plan"]
    state["artifacts"]["request_analysis"] = analysis
    state["approved_artifacts"]["request_analysis"] = analysis
    state["active_stage"] = "request_analysis"
    return _result_payload(state)


def run_problem_to_simulation_harness(
    problem: ProblemInput,
    *,
    runs_root: Optional[Path] = None,
) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    run_id, run_dir = _create_run_dir(root)
    return run_problem_to_simulation_harness_for_run(problem, run_id=run_id, run_dir=run_dir)


def run_problem_to_simulation_harness_for_run(problem: ProblemInput, *, run_id: str, run_dir: Path) -> Dict[str, Any]:
    request_profile = {
        "subject_hint": problem.subject_hint,
        "topic_hint": problem.topic_hint,
        "mode": problem.mode,
        "debug": problem.debug,
    }
    started_at = utc_now_iso()
    artifact_store = RuntimeArtifactStore(run_dir)
    checkpoints = CheckpointStore(run_dir)
    graph = create_coordinator_graph()
    state = new_run_state(problem.text, request_profile)
    state["run_id"] = run_id
    _write_json(run_dir / "problem_request.json", problem.model_dump())

    context = {
        "artifact_store": artifact_store,
        "checkpoints": checkpoints,
        "generator_client": RuntimeGeneratorClient(),
        "skillpack_store": SkillpackStore(),
        "started_at": started_at,
    }

    checkpoints.write_status(
        run_id=run_id,
        status="queued",
        active_stage="queued",
        workflow_plan=[],
        stage_status=state["stage_status"],
        started_at=started_at,
    )
    try:
        request_analysis = analyze_request_text(problem.text)
        state["request_mode"] = request_analysis["request_mode"]
        state["workflow_plan"] = request_analysis["recommended_plan"]
        checkpoints.write_status(
            run_id=run_id,
            status="running",
            active_stage="request_analysis",
            workflow_plan=state["workflow_plan"],
            stage_status=state["stage_status"],
            started_at=started_at,
        )
        graph.run(state, context)
        result = _result_payload(state)
        state["final_result"] = result
        _write_json(run_dir / "final_package.json", result)
        checkpoints.write_checkpoint(state)
        checkpoints.write_status(
            run_id=run_id,
            status="completed",
            active_stage="completed",
            workflow_plan=state["workflow_plan"],
            stage_status=state["stage_status"],
            started_at=started_at,
            finished_at=utc_now_iso(),
        )
        return result
    except StageFailure as exc:
        append_trace(state, stage=exc.stage, event="graph_failed", details={"issues": exc.issues})
        checkpoints.write_checkpoint(state)
        checkpoints.write_status(
            run_id=run_id,
            status="failed",
            active_stage=exc.stage,
            workflow_plan=state["workflow_plan"] or MAIN_STAGE_ORDER,
            stage_status=state["stage_status"],
            started_at=started_at,
            finished_at=utc_now_iso(),
        )
        raise


def create_problem_to_simulation_run(
    problem: ProblemInput,
    *,
    runs_root: Optional[Path] = None,
) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    run_id, run_dir = _create_run_dir(root)
    request_profile = {
        "subject_hint": problem.subject_hint,
        "topic_hint": problem.topic_hint,
        "mode": problem.mode,
        "debug": problem.debug,
    }
    initial_state = new_run_state(problem.text, request_profile)
    CheckpointStore(run_dir).write_status(
        run_id=run_id,
        status="queued",
        active_stage="queued",
        workflow_plan=[],
        stage_status=initial_state["stage_status"],
        started_at=utc_now_iso(),
    )
    _write_json(run_dir / "problem_request.json", problem.model_dump())

    def _background_runner() -> None:
        with suppress(FileNotFoundError):
            run_problem_to_simulation_harness_for_run(problem, run_id=run_id, run_dir=run_dir)

    thread = threading.Thread(target=_background_runner, daemon=True)
    thread.start()
    return {
        "run_id": run_id,
        "status": "queued",
        "route": f"/simulation/{run_id}",
        "status_url": f"/api/problem-to-simulation/runs/{run_id}",
    }


def read_run_status(run_id: str, *, runs_root: Optional[Path] = None) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    return CheckpointStore(root / run_id).read_status()


def read_run_result(run_id: str, *, runs_root: Optional[Path] = None) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    return json.loads((root / run_id / "final_package.json").read_text(encoding="utf-8"))


def read_run_artifact(run_id: str, artifact_name: str, *, runs_root: Optional[Path] = None) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    return RuntimeArtifactStore(root / run_id).read_json_artifact(artifact_name)


def export_run_html(run_id: str, *, runs_root: Optional[Path] = None) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    run_dir = root / run_id
    final_package = read_run_result(run_id, runs_root=root)
    export_path = export_delivery_runtime(run_dir / "exports", final_package["delivery_runtime"])
    return {
        "run_id": run_id,
        "export_mode": "single-file-html",
        "download_url": f"/api/problem-to-simulation/runs/{run_id}/export-html",
        "path": str(export_path),
    }


def export_html_path(run_id: str, *, runs_root: Optional[Path] = None) -> Path:
    root = runs_root or _default_runs_root()
    return root / run_id / "exports" / "simulation.html"


def delete_run(run_id: str, *, runs_root: Optional[Path] = None) -> Dict[str, Any]:
    root = (runs_root or _default_runs_root()).resolve()
    run_dir = (root / run_id).resolve()
    if run_dir.parent != root or not run_dir.exists() or not run_dir.is_dir():
        raise FileNotFoundError(run_id)
    with _RUN_LOCK:
        shutil.rmtree(run_dir)
    return {"run_id": run_id, "deleted": True}


def list_recent_runs(*, runs_root: Optional[Path] = None, limit: int = 12) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    items = []
    if not root.exists():
        return {"items": items}
    for run_dir in sorted(root.iterdir(), reverse=True):
        if not run_dir.is_dir():
            continue
        status_path = run_dir / "status.json"
        if not status_path.exists():
            continue
        with suppress(json.JSONDecodeError, FileNotFoundError):
            status = json.loads(status_path.read_text(encoding="utf-8"))
            result = {}
            result_path = run_dir / "final_package.json"
            if result_path.exists():
                result = json.loads(result_path.read_text(encoding="utf-8"))
            request_analysis = result.get("approved_artifacts", {}).get("request_analysis", {})
            items.append(
                {
                    "run_id": status["run_id"],
                    "title": request_analysis.get("request_mode", run_dir.name),
                    "status": status["status"],
                    "updated_at": status.get("updated_at"),
                    "input_profile": request_analysis.get("input_profile", ""),
                    "request_mode": request_analysis.get("request_mode", ""),
                }
            )
    items.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    return {"items": items[:limit]}
