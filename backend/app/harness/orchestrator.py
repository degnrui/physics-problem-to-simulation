import json
import shutil
from contextlib import suppress
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from app.domain.problem import ProblemInput
from app.harness.artifact_store import ArtifactStore
from app.harness.html_export import write_export_html
from app.harness.model_executor import ModelExecutionTimeoutError, ModelExecutor
from app.harness.run_logger import RunLogger
from app.harness.run_state import RunStateStore
from app.harness.task_registry import build_task_plan
from app.workers.modeler import build_physics_model
from app.workers.parser import build_problem_profile
from app.workers.pedagogy import build_teaching_plan
from app.workers.planner import build_plan_metadata
from app.workers.renderer import (
    build_delivery_bundle,
    build_renderer_payload,
    build_simulation_blueprint,
)
from app.workers.scene_builder import build_scene_spec, build_simulation_spec
from app.workers.validator import build_validation_report

STAGE_SEQUENCE = [
    "planning",
    "modeling",
    "pedagogy",
    "scene",
    "simulation",
    "simulation",
    "simulation",
    "simulation",
    "validation",
    "packaging",
]

_RUN_LOCK = threading.Lock()


def _default_runs_root() -> Path:
    return Path(__file__).resolve().parents[3] / "runs"


def _create_run_dir(runs_root: Path) -> Tuple[str, Path]:
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_id, run_dir


def plan_problem_to_simulation(problem: ProblemInput) -> Dict[str, Any]:
    planner_metadata = build_plan_metadata(problem)
    task_plan = build_task_plan(
        simulation_ready=planner_metadata["simulation_ready"],
        stage_type=planner_metadata["stage_type"],
        problem_family=planner_metadata["problem_family"],
        model_family=planner_metadata["model_family"],
        simulation_mode=planner_metadata["simulation_mode"],
    )
    return {
        "planner": planner_metadata,
        "task_plan": task_plan,
    }


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def _generation_record(metadata: Dict[str, Any], artifact_name: str) -> Dict[str, Any]:
    return {
        "artifact": artifact_name,
        "execution_mode": metadata["execution_mode"],
        "model_name": metadata.get("model_name", ""),
        "validation_passed": metadata["validation_passed"],
    }


def _run_llm_enhanced_worker(
    *,
    use_llm: bool,
    artifact_store: ArtifactStore,
    debug: bool,
    worker_name: str,
    artifact_name: str,
    prompt: str,
    required_keys: list[str],
    fallback_builder,
) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    metadata = {
        "execution_mode": "rule-based",
        "model_name": "",
        "validation_passed": True,
    }
    if use_llm:
        executor = ModelExecutor()
        try:
            llm_output, metadata = executor.execute(
                worker_name=worker_name,
                prompt=prompt,
                required_keys=required_keys,
                debug=debug,
            )
        except ModelExecutionTimeoutError as exc:
            if debug:
                artifact_store.write_artifact(f"llm_debug_{worker_name}", exc.debug_trace)
            raise
        if debug and metadata.get("debug_trace") is not None:
            artifact_store.write_artifact(f"llm_debug_{worker_name}", metadata["debug_trace"])
        if metadata["execution_mode"] == "llm-assisted":
            return llm_output, metadata, _generation_record(metadata, artifact_name)

    fallback_payload = fallback_builder()
    fallback_mode = "fallback" if metadata["execution_mode"] == "fallback" else "rule-based"
    fallback_metadata = {
        "execution_mode": fallback_mode,
        "model_name": metadata.get("model_name", ""),
        "validation_passed": True,
    }
    return fallback_payload, fallback_metadata, _generation_record(fallback_metadata, artifact_name)


def _status_stage(task_index: int, simulation_ready: bool) -> str:
    if not simulation_ready:
        sequence = ["planning", "modeling", "pedagogy", "validation", "packaging"]
        return sequence[task_index]
    return STAGE_SEQUENCE[task_index]


def run_problem_to_simulation_harness(
    problem: ProblemInput,
    *,
    runs_root: Optional[Path] = None,
) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    run_id, run_dir = _create_run_dir(root)
    return run_problem_to_simulation_harness_for_run(problem, run_id=run_id, run_dir=run_dir)


def run_problem_to_simulation_harness_for_run(
    problem: ProblemInput,
    *,
    run_id: str,
    run_dir: Path,
) -> Dict[str, Any]:
    artifact_store = ArtifactStore(run_dir)
    run_logger = RunLogger(run_dir)

    problem_request = {
        "text": problem.text,
        "subject_hint": problem.subject_hint,
        "topic_hint": problem.topic_hint,
        "mode": problem.mode,
        "debug": problem.debug,
    }
    _write_json(run_dir / "problem_request.json", problem_request)

    plan_payload = plan_problem_to_simulation(problem)
    _write_json(run_dir / "task_plan.json", plan_payload)

    planner = plan_payload["planner"]
    task_plan = plan_payload["task_plan"]
    state_store = RunStateStore(run_dir, task_plan)
    if not (run_dir / "status.json").exists():
        state_store.initialize(run_id, stage="queued", status="queued")
    generation_trace = []
    use_llm = problem.mode != "rule-based"

    try:
        state_store.mark_running(0, "planning")
        run_logger.log(
            run_id=run_id,
            task_id="task-0",
            task_type="planner",
            input_digest="problem_request",
            output_digest=f"simulation_ready={planner['simulation_ready']}, stage_type={planner['stage_type']}",
            artifacts_written=["task_plan"],
            status="completed",
            next_task="problem_profile",
        )
        state_store.mark_step_result(
            0,
            status="completed",
            artifacts_written=["task_plan"],
            execution_mode="rule-based",
            validation_passed=True,
            next_stage="modeling",
        )

        state_store.mark_running(1, "modeling")
        problem_profile, profile_meta, profile_trace = _run_llm_enhanced_worker(
            use_llm=use_llm,
            artifact_store=artifact_store,
            debug=problem.debug,
            worker_name="problem_profile",
            artifact_name="problem_profile",
            prompt=f"Extract a problem profile JSON from: {problem.text}",
            required_keys=["summary", "research_object", "scenario", "stages"],
            fallback_builder=lambda: build_problem_profile(problem, planner),
        )
        generation_trace.append(profile_trace)
        artifact_store.write_artifact("problem_profile", problem_profile)
        run_logger.log(
            run_id=run_id,
            task_id="task-1",
            task_type="problem_profile",
            input_digest=planner["stage_type"],
            output_digest=f"research_object={problem_profile['research_object']}",
            artifacts_written=["problem_profile"],
            status="completed",
            next_task="physics_model",
        )
        state_store.mark_step_result(
            1,
            status="completed",
            artifacts_written=["problem_profile"],
            execution_mode=profile_meta["execution_mode"],
            model_name=profile_meta["model_name"],
            validation_passed=profile_meta["validation_passed"],
            next_stage="pedagogy",
        )

        state_store.mark_running(2, "pedagogy")
        physics_model, model_meta, model_trace = _run_llm_enhanced_worker(
            use_llm=use_llm,
            artifact_store=artifact_store,
            debug=problem.debug,
            worker_name="physics_model",
            artifact_name="physics_model",
            prompt=f"Build a physics model JSON from profile: {json.dumps(problem_profile, ensure_ascii=False)}",
            required_keys=["model_type", "research_object", "force_cases", "misconceptions"],
            fallback_builder=lambda: build_physics_model(problem, problem_profile),
        )
        generation_trace.append(model_trace)
        artifact_store.write_artifact("physics_model", physics_model)
        run_logger.log(
            run_id=run_id,
            task_id="task-2",
            task_type="physics_model",
            input_digest=problem_profile["scenario"],
            output_digest=f"force_cases={len(physics_model.get('force_cases', []))}",
            artifacts_written=["physics_model"],
            status="completed",
            next_task="teaching_plan",
        )
        state_store.mark_step_result(
            2,
            status="completed",
            artifacts_written=["physics_model"],
            execution_mode=model_meta["execution_mode"],
            model_name=model_meta["model_name"],
            validation_passed=model_meta["validation_passed"],
            next_stage="scene" if planner["simulation_ready"] else "validation",
        )

        next_task_index = 3
        teaching_plan, teaching_meta, teaching_trace = _run_llm_enhanced_worker(
            use_llm=use_llm,
            artifact_store=artifact_store,
            debug=problem.debug,
            worker_name="teaching_plan",
            artifact_name="teaching_plan",
            prompt=(
                "Build a teaching plan JSON from the following profile and model: "
                f"{json.dumps({'problem_profile': problem_profile, 'physics_model': physics_model}, ensure_ascii=False)}"
            ),
            required_keys=["classroom_use", "primary_goal", "observation_targets", "teacher_prompts"],
            fallback_builder=lambda: build_teaching_plan(problem_profile, physics_model, planner),
        )
        generation_trace.append(teaching_trace)
        artifact_store.write_artifact("teaching_plan", teaching_plan)
        run_logger.log(
            run_id=run_id,
            task_id="task-3",
            task_type="teaching_plan",
            input_digest=physics_model["model_type"],
            output_digest=f"classroom_use={teaching_plan['classroom_use']}",
            artifacts_written=["teaching_plan"],
            status="completed",
            next_task="scene_spec" if planner["simulation_ready"] else "validation_report",
        )
        state_store.mark_step_result(
            next_task_index,
            status="completed",
            artifacts_written=["teaching_plan"],
            execution_mode=teaching_meta["execution_mode"],
            model_name=teaching_meta["model_name"],
            validation_passed=teaching_meta["validation_passed"],
            next_stage="scene" if planner["simulation_ready"] else "validation",
        )

        scene_spec: Optional[Dict[str, Any]] = None
        simulation_spec: Optional[Dict[str, Any]] = None
        simulation_blueprint: Optional[Dict[str, Any]] = None
        renderer_payload: Optional[Dict[str, Any]] = None
        delivery_bundle: Optional[Dict[str, Any]] = None
        status_index = 4

        if planner["simulation_ready"]:
            state_store.mark_running(status_index, "scene")
            scene_spec = build_scene_spec(problem_profile, physics_model, teaching_plan)
            artifact_store.write_artifact("scene_spec", scene_spec)
            run_logger.log(
                run_id=run_id,
                task_id="task-4",
                task_type="scene_spec",
                input_digest=teaching_plan["primary_goal"],
                output_digest=f"template_id={scene_spec['template_id']}",
                artifacts_written=["scene_spec"],
                status="completed",
                next_task="simulation_spec",
            )
            state_store.mark_step_result(
                status_index,
                status="completed",
                artifacts_written=["scene_spec"],
                next_stage="simulation",
            )
            status_index += 1

            state_store.mark_running(status_index, "simulation")
            simulation_spec = build_simulation_spec(scene_spec, teaching_plan)
            artifact_store.write_artifact("simulation_spec", simulation_spec)
            run_logger.log(
                run_id=run_id,
                task_id="task-5",
                task_type="simulation_spec",
                input_digest=scene_spec["template_id"],
                output_digest=f"renderer_mode={simulation_spec['renderer_mode']}",
                artifacts_written=["simulation_spec"],
                status="completed",
                next_task="simulation_blueprint",
            )
            state_store.mark_step_result(
                status_index,
                status="completed",
                artifacts_written=["simulation_spec"],
                next_stage="simulation",
            )
            status_index += 1

            state_store.mark_running(status_index, "simulation")
            simulation_blueprint = build_simulation_blueprint(
                planner, problem_profile, physics_model, scene_spec, simulation_spec
            )
            artifact_store.write_artifact("simulation_blueprint", simulation_blueprint)
            run_logger.log(
                run_id=run_id,
                task_id="task-6",
                task_type="simulation_blueprint",
                input_digest=simulation_spec["renderer_mode"],
                output_digest=f"delivery_mode={simulation_blueprint['delivery_mode']}",
                artifacts_written=["simulation_blueprint"],
                status="completed",
                next_task="renderer_payload",
            )
            state_store.mark_step_result(
                status_index,
                status="completed",
                artifacts_written=["simulation_blueprint"],
                next_stage="simulation",
            )
            status_index += 1

            state_store.mark_running(status_index, "simulation")
            renderer_payload = build_renderer_payload(planner, scene_spec, simulation_spec, teaching_plan)
            artifact_store.write_artifact("renderer_payload", renderer_payload)
            run_logger.log(
                run_id=run_id,
                task_id="task-7",
                task_type="renderer_payload",
                input_digest=scene_spec["template_id"],
                output_digest=f"component_key={renderer_payload['component_key']}",
                artifacts_written=["renderer_payload"],
                status="completed",
                next_task="delivery_bundle",
            )
            state_store.mark_step_result(
                status_index,
                status="completed",
                artifacts_written=["renderer_payload"],
                next_stage="validation",
            )
            status_index += 1

            state_store.mark_running(status_index, "validation")
            delivery_bundle = build_delivery_bundle(simulation_blueprint, renderer_payload, teaching_plan)
            artifact_store.write_artifact("delivery_bundle", delivery_bundle)
            run_logger.log(
                run_id=run_id,
                task_id="task-8",
                task_type="delivery_bundle",
                input_digest=renderer_payload["component_key"],
                output_digest=f"primary_view={delivery_bundle['primary_view']}",
                artifacts_written=["delivery_bundle"],
                status="completed",
                next_task="validation_report",
            )
            state_store.mark_step_result(
                status_index,
                status="completed",
                artifacts_written=["delivery_bundle"],
                next_stage="validation",
            )
            status_index += 1

        state_store.mark_running(status_index, "validation")
        validation_report = build_validation_report(
            planner=planner,
            problem_profile=problem_profile,
            physics_model=physics_model,
            teaching_plan=teaching_plan,
            scene_spec=scene_spec,
            simulation_spec=simulation_spec,
        )
        validation_report["generation_trace"] = generation_trace
        validation_report["export_ready"] = bool(
            planner["simulation_ready"] and validation_report["ready_for_delivery"]
        )
        artifact_store.write_artifact("validation_report", validation_report)
        run_logger.log(
            run_id=run_id,
            task_id="task-9" if planner["simulation_ready"] else "task-4",
            task_type="validation_report",
            input_digest=planner["stage_type"],
            output_digest=f"ready={validation_report['ready_for_delivery']}",
            artifacts_written=["validation_report"],
            status="completed",
            next_task="teaching_simulation_package" if planner["simulation_ready"] else "teaching_analysis_package",
        )
        state_store.mark_step_result(
            status_index,
            status="completed",
            artifacts_written=["validation_report"],
            next_stage="packaging",
        )
        status_index += 1

        if delivery_bundle is not None:
            delivery_bundle["exportable"] = validation_report["export_ready"]
            delivery_bundle["export_mode"] = "single-file-html"
            delivery_bundle["export_includes"] = [
                "scene_spec",
                "simulation_spec",
                "renderer_payload",
                "delivery_bundle",
            ]
            artifact_store.write_artifact("delivery_bundle", delivery_bundle)

        final_key = "teaching_simulation_package" if planner["simulation_ready"] else "teaching_analysis_package"
        final_package = {
            "run_id": run_id,
            "planner": planner,
            "task_plan": task_plan,
            "problem_profile": problem_profile,
            "physics_model": physics_model,
            "teaching_plan": teaching_plan,
            "scene_spec": scene_spec,
            "simulation_spec": simulation_spec,
            "simulation_blueprint": simulation_blueprint,
            "renderer_payload": renderer_payload,
            "delivery_bundle": delivery_bundle,
            "validation_report": validation_report,
            "task_log": run_logger.events,
        }
        artifact_store.write_artifact(final_key, final_package)
        _write_json(run_dir / "final_package.json", final_package)

        state_store.mark_running(status_index, "packaging")
        state_store.mark_step_result(
            status_index,
            status="completed",
            artifacts_written=[final_key],
            next_stage="completed",
        )
        state_store.mark_completed()
        return final_package
    except Exception as exc:  # pragma: no cover - failure path is stateful
        with _RUN_LOCK:
            state_store = RunStateStore(run_dir, task_plan)
            try:
                current = state_store.read()
            except FileNotFoundError:
                return {}
            failing_index = min(max(current["current_step_index"] - 1, 0), current["total_steps"] - 1)
            state_store.mark_failed(failing_index, current["current_stage"], str(exc))
        raise


def create_problem_to_simulation_run(
    problem: ProblemInput,
    *,
    runs_root: Optional[Path] = None,
) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    run_id, run_dir = _create_run_dir(root)
    plan_payload = plan_problem_to_simulation(problem)
    _write_json(run_dir / "problem_request.json", problem.model_dump())
    _write_json(run_dir / "task_plan.json", plan_payload)
    state_store = RunStateStore(run_dir, plan_payload["task_plan"])
    state_store.initialize(run_id)

    def _background_runner() -> None:
        with suppress(FileNotFoundError):
            run_problem_to_simulation_harness_for_run(problem, run_id=run_id, run_dir=run_dir)

    thread = threading.Thread(target=_background_runner, daemon=True)
    thread.start()
    payload = state_store.read()
    return {
        "run_id": run_id,
        "status": payload["status"],
        "route": f"/simulation/{run_id}",
        "status_url": f"/api/problem-to-simulation/runs/{run_id}",
    }


def read_run_status(run_id: str, *, runs_root: Optional[Path] = None) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    status_path = root / run_id / "status.json"
    last_error: Optional[Exception] = None
    for _ in range(3):
        try:
            return json.loads(status_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    return json.loads(status_path.read_text(encoding="utf-8"))


def read_run_result(run_id: str, *, runs_root: Optional[Path] = None) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    return json.loads((root / run_id / "final_package.json").read_text(encoding="utf-8"))


def read_run_artifact(run_id: str, artifact_name: str, *, runs_root: Optional[Path] = None) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    artifact_store = ArtifactStore(root / run_id)
    return artifact_store.read_artifact(artifact_name)


def export_run_html(run_id: str, *, runs_root: Optional[Path] = None) -> Dict[str, Any]:
    root = runs_root or _default_runs_root()
    run_dir = root / run_id
    final_package = read_run_result(run_id, runs_root=root)
    export_path = write_export_html(run_dir / "exports", final_package)
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

    return {
        "run_id": run_id,
        "deleted": True,
    }


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
            final_package = {}
            final_path = run_dir / "final_package.json"
            if final_path.exists():
                final_package = json.loads(final_path.read_text(encoding="utf-8"))
            planner = final_package.get("planner", {})
            problem_profile = final_package.get("problem_profile", {})
            validation_report = final_package.get("validation_report", {})
            items.append(
                {
                    "run_id": status["run_id"],
                    "title": problem_profile.get("summary")
                    or problem_profile.get("scenario")
                    or status["run_id"],
                    "status": status["status"],
                    "updated_at": status.get("updated_at"),
                    "problem_family": planner.get("problem_family", ""),
                    "model_family": planner.get("model_family", ""),
                    "simulation_mode": planner.get("simulation_mode", ""),
                    "export_ready": bool(validation_report.get("export_ready")),
                }
            )
    items.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    return {"items": items[:limit]}
