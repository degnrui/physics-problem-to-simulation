from __future__ import annotations

from typing import Any, Dict, List

from ..common import issue


def build_artifact(inputs: Dict[str, Dict[str, Any]], _: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    runtime_package = inputs["runtime_package_assembly"]
    return context["generator_client"].generate(runtime_package)


def validate_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    if not candidate.get("files"):
        issues.append(issue("MISSING_FILES", "code_generation requires generated files.", "files"))
    if not candidate.get("generator_metadata"):
        issues.append(issue("MISSING_METADATA", "code_generation requires generator metadata.", "generator_metadata"))
    if not candidate.get("primary_file"):
        issues.append(issue("MISSING_PRIMARY_FILE", "code_generation requires a primary_file.", "primary_file"))
    return issues


def approve_artifact(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    primary_file = candidate.get("primary_file")
    if primary_file and primary_file not in candidate.get("files", {}):
        return [issue("INVALID_PRIMARY_FILE", "primary_file must exist in generated files.", "primary_file")]
    return []
