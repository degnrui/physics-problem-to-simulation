from __future__ import annotations

from typing import Any, Dict, Optional

from backend.app.mechanics.executor.api_model import run_api_model_executor
from backend.app.mechanics.executor.dev_proxy import run_dev_proxy_executor


def run_executor(
    harness_packet: Dict[str, Any],
    config: Optional[Dict[str, Any]] = None,
    preferred_model_id: Optional[str] = None,
) -> Dict[str, Any]:
    mode = (config or {}).get("mode", harness_packet.get("executor", "dev_proxy"))
    if mode == "api_model":
        return run_api_model_executor(harness_packet, preferred_model_id=preferred_model_id)
    return run_dev_proxy_executor(harness_packet, preferred_model_id=preferred_model_id)


__all__ = ["run_dev_proxy_executor", "run_api_model_executor", "run_executor"]
