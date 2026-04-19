import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class RunStateStore:
    def __init__(self, run_dir: Path, task_plan: Dict[str, Any]) -> None:
        self.run_dir = run_dir
        self.status_path = run_dir / "status.json"
        self.task_plan = task_plan
        self.steps: List[Dict[str, Any]] = [
            {
                "id": task["id"],
                "label": task["type"],
                "status": "pending",
                "artifacts_written": [],
                "error": "",
                "execution_mode": "rule-based",
                "model_name": "",
                "validation_passed": True,
            }
            for task in task_plan["tasks"]
        ]

    def initialize(self, run_id: str, stage: str = "queued", status: str = "queued") -> Dict[str, Any]:
        now = utc_now_iso()
        payload = {
            "run_id": run_id,
            "status": status,
            "current_stage": stage,
            "current_step_index": 0,
            "total_steps": len(self.steps),
            "percent": 0,
            "started_at": now,
            "updated_at": now,
            "finished_at": None,
            "steps": self.steps,
        }
        self._write(payload)
        return payload

    def read(self) -> Dict[str, Any]:
        return json.loads(self.status_path.read_text(encoding="utf-8"))

    def mark_running(self, step_index: int, stage: str) -> Dict[str, Any]:
        payload = self.read()
        for idx, step in enumerate(payload["steps"]):
            if idx < step_index and step["status"] == "pending":
                step["status"] = "completed"
            elif idx == step_index:
                step["status"] = "running"
        payload["status"] = stage
        payload["current_stage"] = stage
        payload["current_step_index"] = step_index + 1
        payload["percent"] = int((step_index / max(payload["total_steps"], 1)) * 100)
        payload["updated_at"] = utc_now_iso()
        self._write(payload)
        return payload

    def mark_step_result(
        self,
        step_index: int,
        *,
        status: str,
        artifacts_written: Optional[List[str]] = None,
        error: str = "",
        execution_mode: str = "rule-based",
        model_name: str = "",
        validation_passed: bool = True,
        next_stage: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = self.read()
        step = payload["steps"][step_index]
        step["status"] = status
        step["artifacts_written"] = artifacts_written or []
        step["error"] = error
        step["execution_mode"] = execution_mode
        step["model_name"] = model_name
        step["validation_passed"] = validation_passed
        payload["updated_at"] = utc_now_iso()
        if next_stage:
            payload["current_stage"] = next_stage
        completed_steps = sum(1 for item in payload["steps"] if item["status"] == "completed")
        payload["percent"] = int((completed_steps / max(payload["total_steps"], 1)) * 100)
        self._write(payload)
        return payload

    def mark_skipped(
        self,
        step_index: int,
        *,
        artifacts_written: Optional[List[str]] = None,
        next_stage: Optional[str] = None,
    ) -> Dict[str, Any]:
        payload = self.read()
        step = payload["steps"][step_index]
        step["status"] = "skipped"
        step["artifacts_written"] = artifacts_written or []
        step["updated_at"] = utc_now_iso()
        payload["updated_at"] = utc_now_iso()
        if next_stage:
            payload["current_stage"] = next_stage
        completed_steps = sum(
            1 for item in payload["steps"] if item["status"] in {"completed", "skipped"}
        )
        payload["percent"] = int((completed_steps / max(payload["total_steps"], 1)) * 100)
        self._write(payload)
        return payload

    def mark_completed(self) -> Dict[str, Any]:
        payload = self.read()
        payload["status"] = "completed"
        payload["current_stage"] = "completed"
        payload["current_step_index"] = payload["total_steps"]
        payload["percent"] = 100
        payload["updated_at"] = utc_now_iso()
        payload["finished_at"] = utc_now_iso()
        self._write(payload)
        return payload

    def mark_failed(self, step_index: int, stage: str, error: str) -> Dict[str, Any]:
        payload = self.read()
        payload["status"] = "failed"
        payload["current_stage"] = stage
        payload["updated_at"] = utc_now_iso()
        payload["finished_at"] = utc_now_iso()
        if 0 <= step_index < len(payload["steps"]):
            payload["steps"][step_index]["status"] = "failed"
            payload["steps"][step_index]["error"] = error
        if payload["steps"]:
            payload["steps"][-1]["status"] = "failed"
            if not payload["steps"][-1]["error"]:
                payload["steps"][-1]["error"] = error
        self._write(payload)
        return payload

    def _write(self, payload: Dict[str, Any]) -> None:
        tmp_path = self.status_path.with_suffix(".json.tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp_path.replace(self.status_path)
