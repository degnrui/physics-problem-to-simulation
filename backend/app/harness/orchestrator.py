from __future__ import annotations

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
from app.harness.skill_registry import SkillRegistry
from app.harness.stage_builders import (
    build_run_profiling,
    build_stage_contracts,
)
from app.harness.stage_runtime import StageContract, ValidationResult
from app.harness.task_registry import build_task_plan

_RUN_LOCK = threading.Lock()


def _default_runs_root() -> Path:
    return Path(__file__).resolve().parents[3] / "runs"


def _create_run_dir(runs_root: Path) -> Tuple[str, Path]:
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:8]
    run_dir = runs_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_id, run_dir


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def plan_problem_to_simulation(problem: ProblemInput) -> Dict[str, Any]:
    run_profiling = build_run_profiling(problem, {})
    task_plan = build_task_plan(run_profiling)
    return {
        "run_profiling": run_profiling,
        "task_plan": task_plan,
        "stage_graph": [task["type"] for task in task_plan["tasks"]],
    }


def _generation_record(metadata: Dict[str, Any], artifact_name: str) -> Dict[str, Any]:
    return {
        "artifact": artifact_name,
        "execution_mode": metadata["execution_mode"],
        "model_name": metadata.get("model_name", ""),
        "validation_passed": metadata["validation_passed"],
    }


def _build_stage_prompt(
    contract: StageContract,
    skill_registry: SkillRegistry,
    problem: ProblemInput,
    stage_inputs: Dict[str, Dict[str, Any]],
) -> str:
    prompt_bundle = skill_registry.prompt_bundle(
        skill_path=contract.skill_path,
        validator_path=contract.validator_path,
        repair_path=contract.repair_path,
    )
    return (
        f"{prompt_bundle['skill']}\n\n"
        f"Problem request:\n{json.dumps(problem.model_dump(), ensure_ascii=False, indent=2)}\n\n"
        f"Input artifacts:\n{json.dumps(stage_inputs, ensure_ascii=False, indent=2)}\n\n"
        f"Return a JSON object with keys: {', '.join(contract.required_keys)}."
    )


def _run_llm_enhanced_stage(
    *,
    contract: StageContract,
    problem: ProblemInput,
    stage_inputs: Dict[str, Dict[str, Any]],
    use_llm: bool,
    artifact_store: ArtifactStore,
    debug: bool,
    skill_registry: SkillRegistry,
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
                worker_name=contract.stage_name,
                prompt=_build_stage_prompt(contract, skill_registry, problem, stage_inputs),
                required_keys=contract.required_keys,
                debug=debug,
            )
        except ModelExecutionTimeoutError as exc:
            if debug:
                artifact_store.write_artifact(f"llm_debug_{contract.stage_name}", exc.debug_trace)
            raise
        except StopIteration:
            llm_output, metadata = {}, {
                "execution_mode": "fallback",
                "model_name": "",
                "validation_passed": False,
            }
        if debug and metadata.get("debug_trace") is not None:
            artifact_store.write_artifact(f"llm_debug_{contract.stage_name}", metadata["debug_trace"])
        if metadata["execution_mode"] == "llm-assisted":
            return llm_output, metadata, _generation_record(metadata, contract.artifact_name)

    fallback_payload = contract.builder(problem, stage_inputs)
    fallback_mode = "fallback" if metadata["execution_mode"] == "fallback" else "rule-based"
    fallback_metadata = {
        "execution_mode": fallback_mode,
        "model_name": metadata.get("model_name", ""),
        "validation_passed": True,
    }
    return fallback_payload, fallback_metadata, _generation_record(fallback_metadata, contract.artifact_name)


def _write_stage_output(
    *,
    artifact_store: ArtifactStore,
    artifact_name: str,
    payload: Dict[str, Any],
) -> None:
    artifact_store.write_artifact(artifact_name, payload)


def _validation_artifact_name(stage_name: str) -> str:
    return f"{stage_name}_validation"


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
    skill_registry = SkillRegistry()
    stage_contracts = build_stage_contracts()

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

    task_plan = plan_payload["task_plan"]
    state_store = RunStateStore(run_dir, task_plan)
    if not (run_dir / "status.json").exists():
        state_store.initialize(run_id, stage="queued", status="queued")

    use_llm = problem.mode != "rule-based"
    artifacts: Dict[str, Dict[str, Any]] = {}
    stage_validations: Dict[str, Dict[str, Any]] = {}
    generation_trace = []

    try:
        for index, contract in enumerate(stage_contracts):
            stage_inputs = {name: artifacts[name] for name in contract.input_artifacts if name in artifacts}
            should_run = True
            if contract.conditional and contract.should_run is not None:
                should_run = contract.should_run(artifacts, problem)

            state_store.mark_running(index, contract.stage_name)

            if not should_run:
                if contract.stage_name == "evidence_completion":
                    skipped_payload = contract.builder(problem, stage_inputs)
                    artifacts[contract.artifact_name] = skipped_payload
                    validation_payload = ValidationResult(pass_=True, repairable=False, score=100).to_dict()
                    stage_validations[contract.stage_name] = validation_payload
                    _write_stage_output(
                        artifact_store=artifact_store,
                        artifact_name=contract.artifact_name,
                        payload=skipped_payload,
                    )
                    artifact_store.write_artifact(_validation_artifact_name(contract.stage_name), validation_payload)
                    run_logger.log(
                        run_id=run_id,
                        task_id=contract.id,
                        task_type=contract.stage_name,
                        input_digest="conditional-skip",
                        output_digest="completion_status=skipped",
                        artifacts_written=[contract.artifact_name, _validation_artifact_name(contract.stage_name)],
                        status="skipped",
                        next_task=stage_contracts[index + 1].stage_name if index + 1 < len(stage_contracts) else "",
                    )
                    state_store.mark_skipped(
                        index,
                        artifacts_written=[contract.artifact_name, _validation_artifact_name(contract.stage_name)],
                        next_stage=stage_contracts[index + 1].stage_name if index + 1 < len(stage_contracts) else "completed",
                    )
                    continue

                run_logger.log(
                    run_id=run_id,
                    task_id=contract.id,
                    task_type=contract.stage_name,
                    input_digest="conditional-skip",
                    output_digest="skipped",
                    artifacts_written=[],
                    status="skipped",
                    next_task=stage_contracts[index + 1].stage_name if index + 1 < len(stage_contracts) else "",
                )
                state_store.mark_skipped(
                    index,
                    next_stage=stage_contracts[index + 1].stage_name if index + 1 < len(stage_contracts) else "completed",
                )
                continue

            payload, metadata, trace_entry = _run_llm_enhanced_stage(
                contract=contract,
                problem=problem,
                stage_inputs=stage_inputs,
                use_llm=use_llm,
                artifact_store=artifact_store,
                debug=problem.debug,
                skill_registry=skill_registry,
            )
            validation = contract.validator(payload, artifacts | stage_inputs, problem)
            attempt = 1

            while not validation.pass_ and validation.repairable and contract.repairer is not None and attempt < contract.max_attempts:
                payload = contract.repairer(payload, validation, artifacts | stage_inputs, problem)
                validation = contract.validator(payload, artifacts | stage_inputs, problem)
                attempt += 1

            validation_payload = validation.to_dict()
            stage_validations[contract.stage_name] = validation_payload
            artifacts[contract.artifact_name] = payload
            generation_trace.append(trace_entry)

            _write_stage_output(
                artifact_store=artifact_store,
                artifact_name=contract.artifact_name,
                payload=payload,
            )
            artifact_store.write_artifact(_validation_artifact_name(contract.stage_name), validation_payload)

            artifacts_written = [contract.artifact_name, _validation_artifact_name(contract.stage_name)]
            run_logger.log(
                run_id=run_id,
                task_id=contract.id,
                task_type=contract.stage_name,
                input_digest=",".join(contract.input_artifacts) or "problem_request",
                output_digest=f"score={validation.score}",
                artifacts_written=artifacts_written,
                status="completed" if validation.pass_ else "failed",
                next_task=stage_contracts[index + 1].stage_name if index + 1 < len(stage_contracts) else "",
            )
            state_store.mark_step_result(
                index,
                status="completed" if validation.pass_ else "failed",
                artifacts_written=artifacts_written,
                execution_mode=metadata["execution_mode"],
                model_name=metadata["model_name"],
                validation_passed=validation.pass_,
                next_stage=stage_contracts[index + 1].stage_name if index + 1 < len(stage_contracts) else "completed",
            )

            if not validation.pass_:
                raise ValueError(
                    f"Stage `{contract.stage_name}` failed validation: {validation.repair_hint or 'unknown validation error'}"
                )

        artifact_store.write_artifact("generation_trace", {"entries": generation_trace})

        final_package = {
            "run_id": run_id,
            "task_plan": task_plan,
            "stage_graph": [task["type"] for task in task_plan["tasks"]],
            "artifacts": artifacts,
            "stage_validations": stage_validations,
            "generation_trace": generation_trace,
            "run_profiling": artifacts.get("run_profiling"),
            "evidence_completion": artifacts.get("evidence_completion"),
            "knowledge_grounding": artifacts.get("knowledge_grounding"),
            "structured_task_model": artifacts.get("structured_task_model"),
            "instructional_design_brief": artifacts.get("instructional_design_brief"),
            "physics_model": artifacts.get("physics_model"),
            "representation_interaction_design": artifacts.get("representation_interaction_design"),
            "experience_mode_adaptation": artifacts.get("experience_mode_adaptation"),
            "simulation_spec_generation": artifacts.get("simulation_spec_generation"),
            "final_validation": artifacts.get("final_validation"),
            "compile_delivery": artifacts.get("compile_delivery"),
            "task_log": run_logger.events,
        }
        artifact_store.write_artifact("teaching_simulation_package", final_package)
        _write_json(run_dir / "final_package.json", final_package)
        state_store.mark_completed()
        return final_package
    except Exception as exc:  # pragma: no cover
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
            run_profiling = final_package.get("run_profiling", {})
            structured_task_model = final_package.get("structured_task_model", {})
            final_validation = final_package.get("final_validation", {})
            items.append(
                {
                    "run_id": status["run_id"],
                    "title": structured_task_model.get("summary")
                    or structured_task_model.get("scenario")
                    or run_dir.name,
                    "status": status["status"],
                    "updated_at": status.get("updated_at"),
                    "input_profile": run_profiling.get("input_profile", ""),
                    "experience_mode": run_profiling.get("experience_mode", ""),
                    "score": final_validation.get("score", 0),
                    "export_ready": bool(final_validation.get("export_ready")),
                }
            )
    items.sort(key=lambda item: item.get("updated_at") or "", reverse=True)
    return {"items": items[:limit]}
