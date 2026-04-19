from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.health import router as health_router
from app.api.routes.pipeline import router as pipeline_router
from app.config import settings
from app.orchestrator.runner import _default_runs_root

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.state.runs_root = _default_runs_root()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5174", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router, prefix="/api")
app.include_router(pipeline_router, prefix="/api")
