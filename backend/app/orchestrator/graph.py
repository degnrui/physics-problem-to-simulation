from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from app.workflows import (
    code_generation,
    domain_grounding,
    evidence_ingestion,
    instructional_modeling,
    request_analysis,
    runtime_package_assembly,
    runtime_validation,
    simulation_design,
)

from .review import StageFailure, StageRetry, run_stage_review
from .state import MAIN_STAGE_ORDER, SIMULATION_DESIGN_SUBGRAPH, append_trace, set_stage_status


@dataclass
class CoordinatorGraph:
    stage_order: list[str]
    subgraphs: Dict[str, list[str]]

    def run(self, state: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        stage_index = 0
        while stage_index < len(self.stage_order):
            stage = self.stage_order[stage_index]
            workflow_plan = state["workflow_plan"]
            if stage not in workflow_plan:
                set_stage_status(state, stage=stage, status="skipped", attempts=0, issues=[])
                append_trace(state, stage=stage, event="skipped")
                stage_index += 1
                continue

            context["checkpoints"].write_checkpoint(state)
            context["checkpoints"].write_status(
                run_id=state["run_id"],
                status="running",
                active_stage=stage,
                workflow_plan=workflow_plan,
                stage_status=state["stage_status"],
                started_at=context["started_at"],
            )
            state["active_stage"] = stage

            try:
                if stage == "simulation_design":
                    simulation_design.run_simulation_design_subgraph(state, context)
                else:
                    self._run_single_stage(state, stage, context)
                if stage == "code_generation":
                    generated = state["approved_artifacts"]["code_generation"]
                    state["generated_files"] = generated["files"]
                    context["artifact_store"].write_generated_files(generated["files"])
                if stage == "runtime_package_assembly":
                    state["runtime_package"] = state["approved_artifacts"]["runtime_package_assembly"]
                if stage == "runtime_validation":
                    approved = state["approved_artifacts"]["runtime_validation"]
                    state["delivery_runtime"] = {
                        "primary_file": approved["primary_file"],
                        "html": approved["html"],
                    }
                stage_index += 1
            except StageRetry as retry:
                if retry.retry_stage != "code_generation":
                    raise
                code_attempts = state["stage_status"]["code_generation"]["attempts"]
                if code_attempts >= 3:
                    set_stage_status(state, stage=retry.stage, status="failed", attempts=1, issues=retry.issues)
                    raise StageFailure(retry.stage, retry.issues)
                stage_index = self.stage_order.index(retry.retry_stage)
            except StageFailure:
                raise

        return state

    def _run_single_stage(self, state: Dict[str, Any], stage: str, context: Dict[str, Any]) -> Dict[str, Any]:
        approved = state["approved_artifacts"]
        if stage == "request_analysis":
            inputs = {}
            worker = request_analysis.build_artifact
            validator = request_analysis.validate_artifact
            approver = request_analysis.approve_artifact
            repairer = request_analysis.repair_artifact
            max_attempts = 2
            retry_stage = None
        elif stage == "evidence_ingestion":
            inputs = {"request_analysis": approved["request_analysis"]}
            worker = evidence_ingestion.build_artifact
            validator = evidence_ingestion.validate_artifact
            approver = evidence_ingestion.approve_artifact
            repairer = evidence_ingestion.repair_artifact
            max_attempts = 2
            retry_stage = None
        elif stage == "domain_grounding":
            inputs = {
                "request_analysis": approved["request_analysis"],
                **({"evidence_ingestion": approved["evidence_ingestion"]} if "evidence_ingestion" in approved else {}),
            }
            worker = domain_grounding.build_artifact
            validator = domain_grounding.validate_artifact
            approver = domain_grounding.approve_artifact
            repairer = domain_grounding.repair_artifact
            max_attempts = 2
            retry_stage = None
        elif stage == "instructional_modeling":
            inputs = {
                "request_analysis": approved["request_analysis"],
                "domain_grounding": approved["domain_grounding"],
            }
            worker = instructional_modeling.build_artifact
            validator = instructional_modeling.validate_artifact
            approver = instructional_modeling.approve_artifact
            repairer = instructional_modeling.repair_artifact
            max_attempts = 2
            retry_stage = None
        elif stage == "runtime_package_assembly":
            inputs = {
                "domain_grounding": approved["domain_grounding"],
                "instructional_modeling": approved["instructional_modeling"],
                "simulation_design": approved["simulation_design"],
            }
            worker = runtime_package_assembly.build_artifact
            validator = runtime_package_assembly.validate_artifact
            approver = runtime_package_assembly.approve_artifact
            repairer = runtime_package_assembly.repair_artifact
            max_attempts = 2
            retry_stage = None
        elif stage == "code_generation":
            inputs = {"runtime_package_assembly": approved["runtime_package_assembly"]}
            worker = code_generation.build_artifact
            validator = code_generation.validate_artifact
            approver = code_generation.approve_artifact
            repairer = None
            max_attempts = 3
            retry_stage = None
        else:
            inputs = {
                "runtime_package_assembly": approved["runtime_package_assembly"],
                "code_generation": approved["code_generation"],
            }
            worker = runtime_validation.build_artifact
            validator = runtime_validation.validate_artifact
            approver = runtime_validation.approve_artifact
            repairer = None
            max_attempts = 1
            retry_stage = "code_generation"
        return run_stage_review(
            state=state,
            stage=stage,
            inputs=inputs,
            worker=worker,
            validator=validator,
            approver=approver,
            repairer=repairer,
            max_attempts=max_attempts,
            retry_stage=retry_stage,
            context=context,
        )


def create_coordinator_graph() -> CoordinatorGraph:
    return CoordinatorGraph(
        stage_order=MAIN_STAGE_ORDER,
        subgraphs={"simulation_design": SIMULATION_DESIGN_SUBGRAPH},
    )
