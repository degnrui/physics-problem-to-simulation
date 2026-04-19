from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .state import utc_now_iso


class CheckpointStore:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.checkpoint_path = run_dir / "checkpoint.json"
        self.status_path = run_dir / "status.json"

    def write_checkpoint(self, state: Dict[str, Any]) -> None:
        payload = {
            "updated_at": utc_now_iso(),
            "run_state": state,
        }
        self._write_json(self.checkpoint_path, payload)

    def write_status(
        self,
        *,
        run_id: str,
        status: str,
        active_stage: str,
        workflow_plan: list[str],
        stage_status: Dict[str, Any],
        started_at: str,
        finished_at: str | None = None,
    ) -> Dict[str, Any]:
        payload = {
            "run_id": run_id,
            "status": status,
            "active_stage": active_stage,
            "workflow_plan": workflow_plan,
            "stage_status": stage_status,
            "started_at": started_at,
            "updated_at": utc_now_iso(),
            "finished_at": finished_at,
        }
        self._write_json(self.status_path, payload)
        return payload

    def read_status(self) -> Dict[str, Any]:
        return json.loads(self.status_path.read_text(encoding="utf-8"))

    def _write_json(self, path: Path, payload: Dict[str, Any]) -> None:
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_path.replace(path)
