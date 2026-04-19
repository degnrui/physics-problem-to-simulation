from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class RuntimeArtifactStore:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = run_dir
        self.artifacts_dir = run_dir / "artifacts"
        self.generated_dir = run_dir / "generated"
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)

    def write_json_artifact(self, name: str, payload: Dict[str, Any]) -> Path:
        path = self.artifacts_dir / f"{name}.json"
        tmp_path = path.with_suffix(".json.tmp")
        tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp_path.replace(path)
        return path

    def read_json_artifact(self, name: str) -> Dict[str, Any]:
        return json.loads((self.artifacts_dir / f"{name}.json").read_text(encoding="utf-8"))

    def write_generated_files(self, files: Dict[str, str]) -> Dict[str, str]:
        written: Dict[str, str] = {}
        for name, content in files.items():
            path = self.generated_dir / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            written[name] = str(path)
        return written
