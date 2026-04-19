# Runtime Package Assembly Skill

## Purpose
Assemble a comprehensive runtime package from approved domain, instructional, and simulation design artifacts. Package includes generator target, required features, forbidden output modes, and final design specification.

## Input Schema (JSON)
{
  "domain_grounding": "object",
  "instructional_modeling": "object",
  "simulation_design": "object"
}

## Output Schema (JSON)
{
  "generator_target": "string",
  "must_have_features": "array",
  "forbidden_outputs": "array",
  "final_design_package": "object"
}

## Validator
- Ensure generator_target is defined
- Verify must_have_features match approved artifacts
- Confirm forbidden_outputs are properly listed
- Validate final_design_package structure and completeness

## Repair
- Add missing must_have_features from approved simulation_design
- Populate forbidden_outputs if missing
- Normalize final_design_package

## Approve
- Approve only if package references approved artifacts and is self-sufficient