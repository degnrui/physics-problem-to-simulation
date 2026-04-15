import json
from pathlib import Path
from typing import Any, Dict


class ArtifactStore:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.artifacts_dir = run_dir / "artifacts"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

    def write_artifact(self, name: str, payload: Dict[str, Any]) -> Path:
        path = self.artifacts_dir / f"{name}.json"
        tmp_path = path.with_suffix(".json.tmp")
        tmp_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp_path.replace(path)
        return path

    def read_artifact(self, name: str) -> Dict[str, Any]:
        path = self.artifacts_dir / f"{name}.json"
        return json.loads(path.read_text(encoding="utf-8"))
