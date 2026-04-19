from __future__ import annotations

from typing import Any, Dict, List

from ..common import issue, required_fields


def build_artifact(inputs: Dict[str, Dict[str, Any]], _: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    runtime_package = inputs["runtime_package_assembly"]
    return context["generator_client"].generate(runtime_package)


def validate_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for key in required_fields(___, ["files", "generator_metadata", "primary_file"]):
        if not candidate.get(key):
            issues.append(issue("MISSING_FIELD", f"code_generation requires `{key}`.", key))
    return issues


def approve_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    primary_file = candidate.get("primary_file")
    if primary_file and primary_file not in candidate.get("files", {}):
        return [issue("INVALID_PRIMARY_FILE", "primary_file must exist in generated files.", "primary_file")]
    return []
