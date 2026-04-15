from __future__ import annotations

from typing import Any, Dict

from backend.app.mechanics.executor.dev_proxy import run_dev_proxy_executor


def run_api_model_executor(
    harness_packet: Dict[str, Any],
    preferred_model_id: str | None = None,
) -> Dict[str, Any]:
    result = run_dev_proxy_executor(harness_packet, preferred_model_id=preferred_model_id)
    warnings = list(result.get("runtime_warnings", []))
    warnings.append(
        {
            "code": "api_model_stub",
            "message": (
                "api_model executor 适配层已预留，但当前开发环境未注入真实模型调用。"
                "本次结果由 dev_proxy 代跑，用于验证 harness 契约和 teaching simulation 链路。"
            ),
        }
    )
    result["executor"] = "api_model"
    result["runtime_warnings"] = warnings
    return result
