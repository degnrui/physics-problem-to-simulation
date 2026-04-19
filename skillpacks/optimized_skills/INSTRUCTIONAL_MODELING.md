# Instructional Modeling Skill

## Purpose
Generate a structured teaching design document from physics problem input and domain grounding. The skill produces concrete learning goals, observation priorities, misconception handling, interaction guidelines, and mapping to simulation design artifacts.

## Input Schema (JSON)
{
  "request_text": "string",
  "domain_grounding": {
    "domain_type": "string",
    "symbol_table": "object",
    "equations": "array",
    "assumptions": "array",
    "trustworthy_evidence": "array"
  }
}

## Output Schema (JSON)
{
  "learning_goals": "array of strings",
  "observation_priorities": "array of objects",
  "misconception_plan": "array of objects",
  "interaction_priorities": "array of objects",
  "audience_mode": "teacher/student/both",
  "mapping_to_simulation": "object defining objects, controls, charts, measurement panels"
}

## Validator
- Ensure all top-level keys are present
- Each learning goal references approved domain knowledge
- Observation priorities map to at least one domain entity
- Interaction priorities are actionable in simulation design

## Repair
- Fill missing references from domain grounding
- Remove ungrounded claims
- Normalize terminology and data structures

## Approve
- Approve if all mappings can be translated to simulation_design inputs
- Reject if any learning goal or observation cannot be grounded