from fastapi import APIRouter
from typing import Dict, Union

from app.config import settings

router = APIRouter()


@router.get("/health")
def health() -> Dict[str, Union[str, bool]]:
    return {
        "status": "ok",
        "model_provider": settings.model_provider,
        "llm_enabled": settings.llm_enabled,
    }
