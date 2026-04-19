# Controlled Agent Harness Design

Date: 2026-04-19

## Goal

Replace the current rule-router plus template-selector backend with a controlled agent harness that:

- keeps stage flow deterministic and inspectable;
- lets the model solve each stage with clear instructions and tools;
- validates outputs between stages instead of forcing every problem into a fixed family;
- records full traces for debugging, evaluation, and later product analytics.

The harness should improve the model's problem-solving quality by decomposition, tool access, and validation gates rather than by brittle hard-coded topic routing.

## Problem Statement

The current backend behaves like a workflow router:

- `planner.py` classifies a problem into a small set of hard-coded families;
- downstream code maps those families to fixed scene/template structures;
- new problem varieties either collapse into a generic fallback or require yet another hard-coded branch.

This has three structural problems:

1. It does not scale to the variety of real physics problems.
2. It couples problem understanding directly to rendering templates.
3. It gives poor leverage for prompt optimization because the model is not actually being guided through a reusable reasoning scaffold.

## Design Principles

1. Harness owns process, not content.
2. The model owns stage execution, not stage ordering.
3. Tools are explicit capabilities, not ad hoc side effects.
4. Every stage emits a structured artifact and a trace.
5. Validation happens between stages and can trigger local retries.
6. Persistence must be abstracted behind stores so the system can evolve before a database is added.

## Target Architecture

The new system has five core layers.

### 1. Stage Graph

A fixed, harness-owned stage graph defines the order of execution. The model cannot invent or skip stages in v1.

Recommended v1 stages:

1. `problem_understanding`
2. `physics_modeling`
3. `teaching_design`
4. `simulation_design`
5. `asset_planning`
6. `validation`

Each stage declares:

- input artifact dependencies;
- allowed tools;
- output schema;
- validator rules;
- retry budget.

### 2. Stage Executor

Each stage is executed by a controlled stage executor.

The executor assembles:

- stage instruction;
- normalized upstream artifacts;
- tool manifest for this stage;
- output schema;
- formatting and refusal rules;
- retry context if the stage is being rerun.

The executor returns:

- parsed stage artifact;
- execution metadata;
- debug trace.

### 3. Tool Registry

Tools are exposed as registered capabilities instead of being buried inside stage logic.

Examples:

- `document.parse_pdf`
- `document.parse_docx`
- `document.parse_image_ocr`
- `web.search`
- `resource.spotlight_action_search`
- `resource.spotlight_action_fetch`
- `simulation.openmaic_generate`
- `simulation.openmaic_edit`
- `knowledge.formula_lookup`

The registry defines for each tool:

- tool id;
- human-readable description;
- input schema;
- output schema;
- stage allowlist;
- timeout/retry policy;
- trace redaction rules.

### 4. Artifact Store and Trace Store

Every stage writes two outputs.

Artifact:

- the structured result consumed by later stages.

Trace:

- the operational record used by developers and evals.

Trace fields should include:

- `stage_name`
- `run_id`
- `attempt`
- `prompt`
- `tool_manifest`
- `tool_calls`
- `raw_model_response`
- `parsed_output`
- `validation_result`
- `error`
- `started_at`
- `finished_at`
- `elapsed_ms`

### 5. Validator and Retry Gate

Validation is explicit and stage-local.

If a stage fails validation:

- the harness does not advance;
- it records why validation failed;
- it reruns only that stage with a repair prompt and previous failure context.

Retry should be local and bounded. The default v1 rule should be:

- one initial attempt;
- one repair attempt for normal validation failures;
- hard fail after the second invalid output unless the stage is marked high-value and allowed a third attempt.

## Stage Definitions

### Stage 1: `problem_understanding`

Purpose:

- convert raw input into a normalized problem representation.

Inputs:

- raw problem text;
- optional attachment parse results;
- optional OCR output;
- optional image description.

Outputs:

- `problem_representation`
- `entities`
- `given_conditions`
- `unknowns`
- `constraints`
- `subquestions`
- `ambiguities`

Validation:

- research object exists;
- given conditions are separated from unknowns;
- constraints are explicit;
- no final answer leakage.

Allowed tools:

- document parsing;
- OCR/image parsing;
- web search only if the input references an external standard or named resource.

### Stage 2: `physics_modeling`

Purpose:

- produce a physics structure, not a render template.

Inputs:

- problem understanding artifact.

Outputs:

- `state_variables`
- `interactions`
- `phases`
- `governing_relations`
- `assumptions`
- `simplifications`
- `candidate_misconceptions`

Validation:

- variables and relations are internally consistent;
- assumptions are explicit;
- phase boundaries are justified;
- every relation is grounded in the problem or known physics.

Allowed tools:

- formula lookup;
- web search for niche references only when needed.

### Stage 3: `teaching_design`

Purpose:

- translate the model into classroom intent.

Inputs:

- problem understanding;
- physics model.

Outputs:

- `learning_objectives`
- `observation_targets`
- `teacher_prompts`
- `common_errors_to_surface`
- `recommended_sequence`
- `assessment_hooks`

Validation:

- each teaching objective maps to a physics relation or phase;
- observation targets are concrete and visible;
- prompts are teacher-usable.

Allowed tools:

- optional web search for pedagogy references later, but not required in v1.

### Stage 4: `simulation_design`

Purpose:

- convert teaching needs and physics structure into a simulation specification.

Inputs:

- physics model;
- teaching design.

Outputs:

- `simulation_spec`
- `visual_elements`
- `interactive_controls`
- `observable_mappings`
- `scene_timeline`
- `views_panels`
- `non_goals`

Validation:

- every control maps to a variable, phase, or teaching action;
- every visual element has a pedagogical reason;
- non-goals are present to constrain scope.

Allowed tools:

- optional reference tools for known engines or components.

### Stage 5: `asset_planning`

Purpose:

- identify which external capabilities or assets are required.

Inputs:

- simulation design artifact.

Outputs:

- `required_assets`
- `required_tools`
- `animation_actions`
- `resource_queries`
- `fallback_plan`

Validation:

- each requested tool has a reason;
- missing resources have fallback behavior;
- no unnecessary external dependency is introduced.

Allowed tools:

- spotlight action search;
- motion or animation generator metadata lookup;
- asset index tools.

### Stage 6: `validation`

Purpose:

- perform end-to-end consistency checks before downstream generation.

Inputs:

- all previous artifacts.

Outputs:

- `validation_report`
- `consistency_checks`
- `missing_items`
- `risk_flags`
- `retry_recommendations`
- `ready_for_generation`

Validation:

- this stage validates itself by producing a complete report;
- `ready_for_generation` can only be true when all required checks pass.

Allowed tools:

- no external tools in v1 unless a future evaluator service is added.

## Stage Contracts

Each stage contract should live in code as a declarative object rather than being spread across prompt strings.

Suggested fields:

```json
{
  "name": "physics_modeling",
  "description": "Build a physics structure from the normalized problem representation.",
  "input_artifacts": ["problem_understanding"],
  "allowed_tools": ["knowledge.formula_lookup"],
  "output_schema_ref": "schemas/physics_modeling.json",
  "validator_ref": "validators.physics_modeling",
  "max_attempts": 2
}
```

This makes stage policy inspectable, testable, and easy to evolve.

## Tool Invocation Model

The v1 harness should not allow arbitrary tool calling from the model runtime. Instead, tools should be exposed through a narrow, schema-driven call envelope.

Suggested interaction pattern:

1. model emits a structured tool request;
2. harness validates the request against the tool registry;
3. harness executes the tool;
4. harness injects tool result back into the same stage context;
5. model resumes and produces the final artifact.

This keeps the model flexible while preserving operational control.

## Output and Trace Schemas

There are two schema families.

### Artifact schemas

One schema per stage, versioned and stable enough for downstream consumption.

Suggested rule:

- every artifact has `schema_version`;
- every artifact has `stage_name`;
- every artifact has `produced_at`.

### Trace schemas

Operational schema for debugging and evals.

Suggested trace model:

```json
{
  "run_id": "string",
  "stage_name": "string",
  "attempt": 1,
  "prompt": "string",
  "tool_manifest": [],
  "tool_calls": [],
  "raw_model_response": "string",
  "parsed_output": {},
  "validation_result": {},
  "error": null,
  "started_at": "iso8601",
  "finished_at": "iso8601",
  "elapsed_ms": 0
}
```

The trace store is required for debugging and future evals even before a database exists.

## Persistence Strategy Without Database

The system should continue to use filesystem-backed storage for now, but behind stable interfaces.

Recommended interfaces:

- `RunStore`
- `ArtifactStore`
- `TraceStore`
- `ValidationStore`
- `ConversationStore`

Recommended v1 implementation:

- filesystem JSON/NDJSON per run.

Recommended next implementation after schema stabilization:

- SQLite for local development and simple querying;
- Postgres when user history, analytics, and concurrent production usage matter.

The key rule is:

- define the store interfaces now;
- postpone database migration until stage and trace schemas are stable.

## API Surface Changes

The API should shift from exposing only final results to exposing stage-native artifacts and traces.

Suggested endpoints:

- `POST /api/problem-to-simulation/runs`
- `GET /api/problem-to-simulation/runs/{run_id}`
- `GET /api/problem-to-simulation/runs/{run_id}/artifacts/{stage_name}`
- `GET /api/problem-to-simulation/runs/{run_id}/traces/{stage_name}`
- `GET /api/problem-to-simulation/runs/{run_id}/validation`
- `POST /api/problem-to-simulation/runs/{run_id}/retry/{stage_name}`

Trace endpoints should be developer-facing and gated later if the product adds multi-user auth.

## Evaluation Strategy

The harness is not complete without evals.

Recommended eval dimensions:

- schema completeness;
- physical consistency;
- teaching usefulness;
- simulation-spec usefulness;
- tool-use appropriateness;
- retry rate by stage;
- manual developer review outcomes.

Recommended dataset slices:

- single-stage force analysis;
- multi-stage contact transition;
- projectile motion;
- energy or elastic-motion problems;
- modeling-judgement problems;
- attachment-based inputs such as PDFs or images.

Each saved run should become future eval material.

## Migration Plan

### Phase 1: Stabilize Harness Core

- introduce declarative stage contracts;
- implement new artifact schemas;
- implement trace store abstraction;
- keep filesystem persistence.

### Phase 2: Replace Hard-Coded Planner

- remove family-based planner routing from the critical path;
- keep only lightweight input normalization;
- move problem understanding into the first controlled stage.

### Phase 3: Add Tool Registry

- register document, web, and resource tools;
- allow stage-scoped tool invocation;
- record all tool calls in traces.

### Phase 4: Add Validators and Local Retry

- add stage validators;
- implement repair prompts and bounded retries;
- expose validation artifacts and retry metadata.

### Phase 5: Prepare for Database

- freeze schemas after initial dogfooding;
- map file-backed stores to relational tables;
- add query views for runs, traces, and evals.

## Non-Goals for v1

- free-form planner-executor where the model invents arbitrary stage graphs;
- unrestricted tool execution;
- multi-agent orchestration;
- full production database rollout before schema stabilization;
- perfect generic physics simulation generation for all domains in one pass.

## Why This Design

This design deliberately trades some flexibility for reliability.

It avoids the current failure mode of rigid problem-family routing while also avoiding the opposite failure mode of giving the model too much freedom too early. The harness remains opinionated about process, validation, and tools. The model remains responsible for solving well-scoped stage tasks. This matches the intended product direction: controlled agent behavior, better output quality, and a system that can actually be debugged and improved over time.
