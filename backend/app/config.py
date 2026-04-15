import os
from pathlib import Path
from typing import Dict

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "physics-problem-to-simulation"
    app_version: str = "0.1.0"
    model_provider: str = "rule-based"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5-mini"

    @property
    def llm_enabled(self) -> bool:
        return bool(self.openai_api_key)


def _read_env_file() -> Dict[str, str]:
    env_candidates = [
        Path(__file__).resolve().parents[1] / ".env.local",
        Path(__file__).resolve().parents[2] / ".env.local",
    ]
    for path in env_candidates:
        if not path.exists():
            continue
        values: Dict[str, str] = {}
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip()
        return values
    return {}


def _load_settings() -> Settings:
    file_values = _read_env_file()
    return Settings(
        model_provider=os.getenv("MODEL_PROVIDER", file_values.get("MODEL_PROVIDER", "rule-based")),
        openai_api_key=os.getenv("OPENAI_API_KEY", file_values.get("OPENAI_API_KEY", "")),
        openai_base_url=os.getenv(
            "OPENAI_BASE_URL", file_values.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        ),
        openai_model=os.getenv("OPENAI_MODEL", file_values.get("OPENAI_MODEL", "gpt-5-mini")),
    )


settings = _load_settings()
