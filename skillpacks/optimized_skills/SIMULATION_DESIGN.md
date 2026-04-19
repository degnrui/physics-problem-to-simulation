# Simulation Design Skill

## Purpose
Generate a structured simulation design artifact from approved domain knowledge and instructional modeling output. The design includes scene objects, controls, charts, measurement panels, and pedagogical views.

## Input Schema (JSON)
{
  "domain_grounding": "object",
  "instructional_modeling": "object",
  "request_analysis": "object"
}

## Output Schema (JSON)
{
  "scene_design": "object",
  "control_design": "object",
  "chart_measurement_design": "object",
  "pedagogical_view_design": "object",
  "design_merge": "object"
}

## Validator
- All scene objects exist and have correct metadata
- Controls include play/pause/reset and at least one state-changing parameter
- Charts/measurement panels map to scene state
- Pedagogical views provide teacher/student presets
- design_merge validates cross-node consistency

## Repair
- Fill missing scene objects and defaults
- Add required controls
- Normalize chart bindings
- Correct pedagogical view defaults

## Approve
- Approve only if all child nodes are approved and merged design is coherent
- Reject if any sub-artifact is incomplete or inconsistent