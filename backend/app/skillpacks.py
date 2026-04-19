from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


class SkillpackStore:
    def __init__(self, root: Path | None = None) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        self.repo_root = repo_root
        self.root = root or repo_root / "skillpacks" / "langgraph_runtime"
        self.optimized_root = repo_root / "skillpacks" / "optimized_skills"
        self._cache: Dict[str, Dict[str, Any]] = {}

    def load(self, stage: str) -> Dict[str, Any]:
        if stage in self._cache:
            return self._cache[stage]
        stage_dir = self.root / stage
        if not stage_dir.exists():
            raise FileNotFoundError(f"Missing skillpack for stage `{stage}` at {stage_dir}")
        optimized_path = self.optimized_root / f"{stage.upper()}.md"
        skill_path = optimized_path if optimized_path.exists() else stage_dir / "SKILL.md"
        payload = {
            "stage": stage,
            "dir": str(stage_dir),
            "relative_dir": str(stage_dir.relative_to(self.repo_root)),
            "skill_path": str(skill_path),
            "skill_relative_path": str(skill_path.relative_to(self.repo_root)),
            "skill": skill_path.read_text(encoding="utf-8"),
            "contract": json.loads((stage_dir / "contract.json").read_text(encoding="utf-8")),
            "validator": (stage_dir / "validator.md").read_text(encoding="utf-8"),
            "repair": (stage_dir / "repair.md").read_text(encoding="utf-8"),
        }
        self._cache[stage] = payload
        return payload
