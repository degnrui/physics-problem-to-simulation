from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "physics-problem-to-simulation"
    app_version: str = "0.1.0"


settings = Settings()

