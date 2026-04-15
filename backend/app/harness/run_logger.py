import json
from pathlib import Path
from typing import Any, Dict, List


class RunLogger:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.log_path = run_dir / "task_log.ndjson"
        self.events: List[Dict[str, Any]] = []

    def log(
        self,
        *,
        run_id: str,
        task_id: str,
        task_type: str,
        input_digest: str,
        output_digest: str,
        artifacts_written: List[str],
        status: str,
        next_task: str = "",
        error: str = "",
    ) -> Dict[str, Any]:
        event = {
            "run_id": run_id,
            "task_id": task_id,
            "task_type": task_type,
            "input_digest": input_digest,
            "output_digest": output_digest,
            "artifacts_written": artifacts_written,
            "status": status,
            "error": error,
            "next_task": next_task,
        }
        self.events.append(event)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
        return event
