import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Tuple

from app.config import settings


class ModelExecutor:
    def execute(
        self,
        *,
        worker_name: str,
        prompt: str,
        required_keys: List[str],
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if not settings.llm_enabled:
            return {}, self._metadata("rule-based", validation_passed=False)

        request_payload = {
            "model": settings.openai_model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a JSON-only worker inside a controlled harness. "
                        "Return a single JSON object and no markdown."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
        }
        request = urllib.request.Request(
            url=f"{settings.openai_base_url.rstrip('/')}/chat/completions",
            data=json.dumps(request_payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.openai_api_key}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return {}, self._metadata("fallback", validation_passed=False)

        content = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "{}")
        )
        if isinstance(content, list):
            content = "".join(
                item.get("text", "") for item in content if isinstance(item, dict)
            )
        try:
            candidate = json.loads(content)
        except json.JSONDecodeError:
            return {}, self._metadata("fallback", validation_passed=False)

        if not isinstance(candidate, dict):
            return {}, self._metadata("fallback", validation_passed=False)
        validation_passed = all(key in candidate for key in required_keys)
        if not validation_passed:
            return {}, self._metadata("fallback", validation_passed=False)
        return candidate, self._metadata("llm-assisted", validation_passed=True)

    def _metadata(self, mode: str, *, validation_passed: bool) -> Dict[str, Any]:
        return {
            "worker_name": "",
            "execution_mode": mode,
            "model_name": settings.openai_model if settings.llm_enabled else "",
            "validation_passed": validation_passed,
        }
