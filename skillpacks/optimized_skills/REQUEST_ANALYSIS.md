# Request Analysis Skill

## Purpose
Classify incoming physics problem requests, extract evidence needs, and plan workflow paths for downstream processing. Provides structured output for all subsequent skills.

## Input Schema (JSON)
{
  "problem_text": "string",
  "uploaded_references": "array",
  "previous_simulations": "array"
}

## Output Schema (JSON)
{
  "request_mode": "new_simulation | revision_existing_simulation",
  "input_profile": "string",
  "information_density": "low | medium | high",
  "has_existing_simulation": "boolean",
  "workflow_plan": "array of stage ids",
  "evidence_needed": "boolean"
}

## Validator
- Require all top-level fields
- workflow_plan must be non-empty
- request_mode and has_existing_simulation must be consistent

## Repair
- Infer missing classification fields using heuristics
- Fill workflow_plan defaults based on input profile

## Approve
- Approve only if all routing fields are complete and consistent
- Reject if plan contains unknown stage ids