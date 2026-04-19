# Code Generation Skill

## Purpose
Generate the simulation runtime files (HTML, JS, CSS, metadata) from approved runtime package, ensuring all scene objects, controls, charts, and pedagogical views are correctly represented and executable.

## Input Schema (JSON)
{
  "runtime_package": "object"
}

## Output Schema (JSON)
{
  "generated_files": "object mapping filenames to content",
  "primary_runtime_file": "string",
  "provider_metadata": "object"
}

## Validator
- Ensure primary_runtime_file exists
- All scene objects and controls have JS bindings
- Charts and measurement panels correctly link to runtime state
- Generated HTML includes canvas and interactive controls

## Repair
- Normalize file names and content structures
- Retry generation for missing bindings
- Do not hand-edit HTML manually

## Approve
- Approve only if all runtime files are present and interactive
- Reject if any critical element (canvas, control, chart) is missing or unbound