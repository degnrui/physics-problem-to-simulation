from fastapi import FastAPI

from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.pipeline import router as pipeline_router
from backend.app.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.include_router(health_router, prefix="/api")
app.include_router(pipeline_router, prefix="/api")

