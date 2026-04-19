import json
import socket
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from app.config import settings

REQUEST_TIMEOUT_SECONDS = 240


class ModelExecutionTimeoutError(TimeoutError):
    def __init__(self, message: str, *, debug_trace: Dict[str, Any]) -> None:
        super().__init__(message)
        self.debug_trace = debug_trace


class ModelExecutor:
    def execute(
        self,
        *,
        worker_name: str,
        prompt: str,
        required_keys: List[str],
        debug: bool = False,
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
        started_at = datetime.now(timezone.utc)
        raw_response = ""
        payload: Dict[str, Any] = {}
        content: Any = "{}"
        reasoning_content: Any = None

        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                raw_response = response.read().decode("utf-8")
                payload = json.loads(raw_response)
        except urllib.error.HTTPError as exc:
            raw_response = exc.read().decode("utf-8", errors="replace")
            return {}, self._metadata(
                "fallback",
                validation_passed=False,
                worker_name=worker_name,
                debug_trace=self._debug_trace(
                    worker_name=worker_name,
                    request_payload=request_payload,
                    required_keys=required_keys,
                    started_at=started_at,
                    raw_response=raw_response,
                    error=exc,
                    debug=debug,
                ),
            )
        except urllib.error.URLError as exc:
            if self._is_timeout_error(exc):
                raise ModelExecutionTimeoutError(
                    str(exc.reason),
                    debug_trace=self._debug_trace(
                        worker_name=worker_name,
                        request_payload=request_payload,
                        required_keys=required_keys,
                        started_at=started_at,
                        raw_response=raw_response,
                        error=exc.reason if exc.reason else exc,
                        debug=debug,
                    ),
                )
            return {}, self._metadata(
                "fallback",
                validation_passed=False,
                worker_name=worker_name,
                debug_trace=self._debug_trace(
                    worker_name=worker_name,
                    request_payload=request_payload,
                    required_keys=required_keys,
                    started_at=started_at,
                    raw_response=raw_response,
                    error=exc,
                    debug=debug,
                ),
            )
        except (TimeoutError, socket.timeout) as exc:
            raise ModelExecutionTimeoutError(
                str(exc),
                debug_trace=self._debug_trace(
                    worker_name=worker_name,
                    request_payload=request_payload,
                    required_keys=required_keys,
                    started_at=started_at,
                    raw_response=raw_response,
                    error=exc,
                    debug=debug,
                ),
            )
        except json.JSONDecodeError as exc:
            return {}, self._metadata(
                "fallback",
                validation_passed=False,
                worker_name=worker_name,
                debug_trace=self._debug_trace(
                    worker_name=worker_name,
                    request_payload=request_payload,
                    required_keys=required_keys,
                    started_at=started_at,
                    raw_response=raw_response,
                    error=exc,
                    debug=debug,
                ),
            )

        content = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "{}")
        )
        reasoning_content = (
            payload.get("choices", [{}])[0]
            .get("message", {})
            .get("reasoning_content")
        )
        if isinstance(content, list):
            content = "".join(
                item.get("text", "") for item in content if isinstance(item, dict)
            )
        try:
            candidate = json.loads(content)
        except json.JSONDecodeError as exc:
            return {}, self._metadata(
                "fallback",
                validation_passed=False,
                worker_name=worker_name,
                debug_trace=self._debug_trace(
                    worker_name=worker_name,
                    request_payload=request_payload,
                    required_keys=required_keys,
                    started_at=started_at,
                    raw_response=raw_response,
                    content=content,
                    reasoning_content=reasoning_content,
                    error=exc,
                    debug=debug,
                ),
            )

        if not isinstance(candidate, dict):
            return {}, self._metadata(
                "fallback",
                validation_passed=False,
                worker_name=worker_name,
                debug_trace=self._debug_trace(
                    worker_name=worker_name,
                    request_payload=request_payload,
                    required_keys=required_keys,
                    started_at=started_at,
                    raw_response=raw_response,
                    content=content,
                    reasoning_content=reasoning_content,
                    parsed_candidate=candidate,
                    debug=debug,
                ),
            )
        validation_passed = all(key in candidate for key in required_keys)
        if not validation_passed:
            return {}, self._metadata(
                "fallback",
                validation_passed=False,
                worker_name=worker_name,
                debug_trace=self._debug_trace(
                    worker_name=worker_name,
                    request_payload=request_payload,
                    required_keys=required_keys,
                    started_at=started_at,
                    raw_response=raw_response,
                    content=content,
                    reasoning_content=reasoning_content,
                    parsed_candidate=candidate,
                    debug=debug,
                ),
            )
        return candidate, self._metadata(
            "llm-assisted",
            validation_passed=True,
            worker_name=worker_name,
            debug_trace=self._debug_trace(
                worker_name=worker_name,
                request_payload=request_payload,
                required_keys=required_keys,
                started_at=started_at,
                raw_response=raw_response,
                content=content,
                reasoning_content=reasoning_content,
                parsed_candidate=candidate,
                debug=debug,
            ),
        )

    def _metadata(
        self,
        mode: str,
        *,
        validation_passed: bool,
        worker_name: str,
        debug_trace: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "worker_name": "",
            "execution_mode": mode,
            "model_name": settings.openai_model if settings.llm_enabled else "",
            "validation_passed": validation_passed,
        }
        if debug_trace is not None:
            payload["debug_trace"] = debug_trace
        if worker_name:
            payload["worker_name"] = worker_name
        return payload

    def _is_timeout_error(self, error: urllib.error.URLError) -> bool:
        return isinstance(error.reason, (TimeoutError, socket.timeout))

    def _debug_trace(
        self,
        *,
        worker_name: str,
        request_payload: Dict[str, Any],
        required_keys: List[str],
        started_at: datetime,
        debug: bool,
        raw_response: str = "",
        content: Any = None,
        reasoning_content: Any = None,
        parsed_candidate: Any = None,
        error: Optional[Exception] = None,
    ) -> Optional[Dict[str, Any]]:
        if not debug:
            return None
        finished_at = datetime.now(timezone.utc)
        return {
            "worker_name": worker_name,
            "model_name": settings.openai_model if settings.llm_enabled else "",
            "timeout_seconds": REQUEST_TIMEOUT_SECONDS,
            "required_keys": required_keys,
            "started_at": started_at.isoformat(),
            "finished_at": finished_at.isoformat(),
            "elapsed_ms": int((finished_at - started_at).total_seconds() * 1000),
            "request_payload": request_payload,
            "response": {
                "raw_text": raw_response,
                "content": content,
                "reasoning_content": reasoning_content,
                "parsed_candidate": parsed_candidate,
            },
            "error": {
                "type": type(error).__name__,
                "message": str(error),
            }
            if error is not None
            else None,
        }
