# Domain Grounding Skill

## Purpose
Extract physics domain knowledge from problem input and evidence. Generate canonical symbol tables, equations, assumptions, and trustworthy evidence suitable for downstream simulation design.

## Input Schema (JSON)
{
  "request_analysis_output": "object",
  "uploaded_evidence": "array"
}

## Output Schema (JSON)
{
  "domain_type": "string",
  "symbol_table": "object",
  "canonical_equations": "array",
  "assumptions": "array",
  "trustworthy_evidence": "array"
}

## Validator
- Ensure domain_type is assigned
- Each symbol must have a description and unit
- Equations must reference existing symbols
- Assumptions must be grounded in trustworthy_evidence

## Repair
- Fill missing symbol metadata
- Remove unsupported equations/assumptions
- Rebuild trustworthy evidence links from input

## Approve
- Approve only if all equations, symbols, and assumptions are internally consistent and traceable to evidence