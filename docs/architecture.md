# Architecture

## Coordinator Graph

The application is organized around a coordinator graph with explicit stage review loops:

`request_analysis -> evidence_ingestion? -> domain_grounding -> instructional_modeling -> simulation_design -> runtime_package_assembly -> code_generation -> runtime_validation`

`publish_result` happens only after `runtime_validation` approves the generated runtime.

## State and Contracts

The canonical state object is `RunState`. It stores:

- request metadata
- workflow plan
- candidate artifacts in `artifacts`
- approved artifacts in `approved_artifacts`
- per-stage review state in `stage_status`
- retry / repair history in `execution_trace`
- generation outputs in `generated_files`
- final validated HTML in `delivery_runtime`

Downstream stages must read only from `approved_artifacts`.

## Review Loops

Every stage uses the same outer loop:

1. generate candidate output
2. validate candidate
3. approve candidate if validation passes
4. if repairable, repair and re-run validation / approval
5. otherwise fail the stage

Only `runtime_validation` may route back to a different stage, and it routes only to `code_generation`.

## Skillpacks

The live stage guidance is stored under `skillpacks/langgraph_runtime/`.

- every main stage and every `simulation_design` child node has its own skillpack directory
- each directory contains `SKILL.md`, `contract.json`, `validator.md`, and `repair.md`
- `backend/app/skillpacks.py` loads the active stage skillpack at runtime
- main stages prefer the text guidance under `skillpacks/optimized_skills/*.md` when available
- the coordinator records `skillpack_loaded` in `execution_trace` so runs show which skillpack guided each stage
- validators and package assembly read `contract.json` values directly, so skillpacks affect execution rather than serving as dead documentation

## `simulation_design` Subgraph

`simulation_design` is a subgraph with explicit child nodes:

- `scene_design`
- `control_design`
- `chart_measurement_design`
- `pedagogical_view_design`
- `design_merge`

Each child node has its own validator, repair, and approve rules. The parent stage approves only when all child nodes approve and the merged design is coherent.

## Frontend Contract

The frontend Studio reads only:

- `run_state.stage_status`
- `run_state.workflow_plan`
- `approved_artifacts`
- `artifacts`
- `execution_trace`
- `delivery_runtime`
- `generated_files`

Legacy compile-time report payloads are removed.
