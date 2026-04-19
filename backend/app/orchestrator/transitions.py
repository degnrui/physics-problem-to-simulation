from __future__ import annotations

from .state import MAIN_STAGE_ORDER


def next_stage_name(stage: str) -> str | None:
    try:
        index = MAIN_STAGE_ORDER.index(stage)
    except ValueError:
        return None
    if index + 1 >= len(MAIN_STAGE_ORDER):
        return None
    return MAIN_STAGE_ORDER[index + 1]

