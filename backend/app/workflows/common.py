from __future__ import annotations

from typing import Any, Dict, List


def issue(code: str, message: str, field: str = "") -> Dict[str, Any]:
    return {"code": code, "message": message, "field": field}


def split_sentences(text: str) -> List[str]:
    cleaned = (
        text.replace("\n", " ")
        .replace("。", ".")
        .replace("！", ".")
        .replace("？", ".")
        .replace("；", ".")
    )
    parts = [segment.strip() for segment in cleaned.split(".")]
    return [segment for segment in parts if segment]


def detect_domain_type(text: str) -> str:
    lowered = text.lower()
    if "摆" in text or "pendulum" in lowered:
        return "small_angle_pendulum"
    if "平抛" in text or "projectile" in lowered or "钢球" in text:
        return "projectile_motion"
    if "橡皮绳" in text or "回复力" in text or "restoring" in lowered:
        return "restoring_force"
    return "force_analysis"


def contract_value(context: Dict[str, Any], key: str, default: Any) -> Any:
    skillpack = context.get("stage_skillpack") or {}
    contract = skillpack.get("contract") or {}
    return contract.get(key, default)


def required_fields(context: Dict[str, Any], default: List[str]) -> List[str]:
    values = contract_value(context, "required_fields", default)
    return values if isinstance(values, list) and values else default
