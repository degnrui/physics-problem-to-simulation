from __future__ import annotations

from pathlib import Path


class SkillRegistry:
    def __init__(self, base_dir: Path | None = None) -> None:
        self.base_dir = base_dir or (
            Path(__file__).resolve().parents[3] / "skillpacks" / "physics_sim_agent_v2_package"
        )

    def read(self, relative_path: str) -> str:
        path = self.base_dir / relative_path
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8").strip()

    def stage_prompt(self, stage_dir: str, kind: str) -> str:
        return self.read(f"{stage_dir}/{kind}.md")

    def prompt_bundle(self, *, skill_path: str, validator_path: str, repair_path: str | None) -> dict:
        return {
            "skill": self.read(skill_path),
            "validator": self.read(validator_path),
            "repair": self.read(repair_path) if repair_path else "",
        }
