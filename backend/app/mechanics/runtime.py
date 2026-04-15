from __future__ import annotations

from typing import Any, Dict

from backend.app.mechanics.scene import normalized_stage_progress, stage_index
from backend.app.schemas.mechanics import MechanicsRuntimeFrame, MechanicsTeachingScene


def _clamp(progress: float) -> float:
    return min(1.0, max(0.0, progress))


def _annotation_payload(scene: MechanicsTeachingScene, stage_id: str):
    return [
        {"key": item.key, "label": item.label, "value": item.value, "emphasis": item.emphasis}
        for item in scene.annotations
        if item.stage_id == stage_id
    ]


def render_mechanics_runtime_frame(
    *,
    scene: MechanicsTeachingScene,
    stage_id: str,
    progress: float,
    simulation_spec: Dict[str, Any],
) -> MechanicsRuntimeFrame:
    progress = _clamp(progress)
    global_progress = normalized_stage_progress(stage_id, progress)
    belt_time = float(simulation_spec.get("stage_results", {}).get("belt", {}).get("time", 0.4))
    belt_slip = float(simulation_spec.get("stage_results", {}).get("belt", {}).get("slip_length", 0.2))
    arc_top = simulation_spec.get("stage_results", {}).get("arc_top", {})
    q4 = simulation_spec.get("answers", {}).get("q4", {}).get("display_value", "")

    block_positions = {
        "slope": {"x": 84 + 248 * progress, "y": 152 + 134 * progress},
        "belt": {"x": 332 + 324 * progress, "y": 286},
        "arc_entry": {"x": 656 + 92 * progress, "y": 286 - 122 * progress},
        "arc_top": {"x": 796, "y": 164},
    }
    block_position = block_positions.get(stage_id, block_positions["slope"])

    actors = {
        "block": {
            "x": round(block_position["x"], 2),
            "y": round(block_position["y"], 2),
            "velocity": simulation_spec.get("answers", {}).get("q1", {}).get("display_value", ""),
            "highlight": stage_id,
        },
        "belt": {
            "x": 332,
            "y": 286,
            "offset": round(42 * progress if stage_id == "belt" else 0.0, 2),
            "speed": "5 m/s",
            "slip": f"{belt_slip} m",
        },
        "arc": {
            "cx": round(796 + 24 * progress if stage_id in {"arc_entry", "arc_top"} else 796, 2),
            "cy": 286,
            "relative_speed": f"{abs(float(arc_top.get('v_relative_top', 0.0)))} m/s",
        },
    }

    overlays = {
        "stage_index": stage_index(stage_id) + 1,
        "belt_speed": "5 m/s",
        "belt_sync_time": f"{belt_time} s",
        "top_normal_force": q4,
        "global_progress": round(global_progress, 3),
    }
    if stage_id == "arc_top":
        overlays["force_balance"] = "F + mg = m v_rel^2 / R"

    return MechanicsRuntimeFrame.model_validate(
        {
            "progress": progress,
            "actors": actors,
            "overlays": overlays,
            "annotations": _annotation_payload(scene, stage_id),
            "chart_series": [item.model_dump() for item in scene.charts],
        }
    )
