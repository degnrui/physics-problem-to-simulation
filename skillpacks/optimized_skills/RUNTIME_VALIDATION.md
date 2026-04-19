# Runtime Validation Skill

## Purpose
Validate generated simulation runtime to ensure interactivity, correctness of controls, chart bindings, and overall simulation integrity.

## Input Schema (JSON)
{
  "generated_files": "object",
  "runtime_package": "object"
}

## Output Schema (JSON)
{
  "validation_report": "object",
  "delivery_runtime": "HTML string"
}

## Validator
- Ensure primary runtime file exists and is HTML
- Check canvas or simulation viewport presence
- Verify play, pause, reset buttons exist
- At least one additional state-changing control exists
- Chart and measurement panels are bound to runtime state
- Reject payload-shell, report-shell, or empty placeholders

## Repair
- No direct HTML patching
- Emit structured issues for code_generation retry
- Identify missing controls, chart elements, state-change bindings

## Approve
- Approve only if all interactivity and shell checks pass
- Route failures back to code_generation
- Stop publish if attempts exhausted