from __future__ import annotations

from typing import Any, Dict, List

from backend.app.schemas.mechanics import MechanicsTeachingScene


STAGE_ORDER = ["slope", "belt", "arc_entry", "arc_top"]


def _answer_value(spec: Dict[str, Any], key: str) -> str:
    answers = spec.get("answers", {})
    answer = answers.get(key, {})
    return answer.get("display_value", "")


def compile_mechanics_scene(
    *,
    session_id: str,
    problem_representation: Dict[str, Any],
    simulation_spec: Dict[str, Any],
    selected_model: Dict[str, Any],
) -> MechanicsTeachingScene:
    stage_results = simulation_spec.get("stage_results", {})
    v_b = stage_results.get("slope", {}).get("v_b", 0.0)
    belt_time = stage_results.get("belt", {}).get("time", 0.0)
    top_relative = stage_results.get("arc_top", {}).get("v_relative_top", 0.0)
    title = problem_representation.get("summary") or "力学教学仿真"

    scene = MechanicsTeachingScene.model_validate(
        {
            "scene_id": f"mechanics-{session_id}",
            "title": title,
            "canvas": {
                "width": 1120,
                "height": 720,
                "background": "dawn-grid",
                "coordinate_hint": "x-horizontal,y-vertical",
            },
            "actors": [
                {
                    "id": "block",
                    "kind": "particle",
                    "label": "物块",
                    "geometry": {"x": 84, "y": 152, "radius": 16},
                    "style": {"fill": "#d1495b", "stroke": "#111111"},
                },
                {
                    "id": "slope",
                    "kind": "track",
                    "label": "AB 斜轨道",
                    "geometry": {"x1": 72, "y1": 124, "x2": 332, "y2": 286},
                    "style": {"stroke": "#1f2937", "strokeWidth": 6},
                },
                {
                    "id": "belt",
                    "kind": "belt",
                    "label": "BC 传送带",
                    "geometry": {"x": 332, "y": 286, "width": 324, "height": 38},
                    "style": {"fill": "#f4d35e", "stroke": "#111111"},
                },
                {
                    "id": "arc",
                    "kind": "moving_track",
                    "label": "可动半圆弧轨道",
                    "geometry": {"cx": 796, "cy": 286, "radius": 122},
                    "style": {"stroke": "#0f766e", "strokeWidth": 6},
                },
            ],
            "stages": [
                {
                    "id": "slope",
                    "title": "斜面下滑",
                    "prompt": "先用动能定理把斜面阶段单独封闭。",
                    "focus": ["重力做功", "B 点速度", f"v_B={v_b} m/s"],
                    "duration": 1.0,
                },
                {
                    "id": "belt",
                    "title": "传送带共速",
                    "prompt": "观察物块相对传送带滑动，并用摩擦建立速度与位移。",
                    "focus": ["摩擦做功", "滑痕长度", f"共速时间={belt_time} s"],
                    "duration": 1.15,
                },
                {
                    "id": "arc_entry",
                    "title": "进入可动圆弧",
                    "prompt": "圆弧可动，水平方向系统动量要和能量关系一起看。",
                    "focus": ["水平动量守恒", "机械能关系", selected_model.get("title", "")],
                    "duration": 1.1,
                },
                {
                    "id": "arc_top",
                    "title": "最高点受力",
                    "prompt": "到最高点后只剩法向力与重力沿半径方向起作用。",
                    "focus": ["向心条件", "最高点压力", f"v_rel={top_relative} m/s"],
                    "duration": 1.0,
                },
            ],
            "annotations": [
                {"key": "q1", "stage_id": "slope", "label": "B 点速度", "value": _answer_value(simulation_spec, "q1"), "emphasis": "answer"},
                {"key": "q2", "stage_id": "belt", "label": "摩擦做功", "value": _answer_value(simulation_spec, "q2"), "emphasis": "answer"},
                {"key": "q3", "stage_id": "belt", "label": "滑痕长度", "value": _answer_value(simulation_spec, "q3"), "emphasis": "answer"},
                {"key": "q4", "stage_id": "arc_top", "label": "最高点压力", "value": _answer_value(simulation_spec, "q4"), "emphasis": "answer"},
            ],
            "charts": [
                {
                    "id": "speed",
                    "label": "物块速度",
                    "unit": "m/s",
                    "points": [
                        {"x": 0.0, "y": 0.0},
                        {"x": 0.33, "y": float(v_b)},
                        {"x": 0.66, "y": 5.0},
                        {"x": 1.0, "y": abs(float(top_relative))},
                    ],
                },
                {
                    "id": "energy",
                    "label": "系统机械能指示",
                    "unit": "J",
                    "points": [
                        {"x": 0.0, "y": 1.6},
                        {"x": 0.33, "y": 1.6},
                        {"x": 0.66, "y": 2.5},
                        {"x": 1.0, "y": 0.58},
                    ],
                },
            ],
            "lesson_panels": [
                {
                    "stage_id": "slope",
                    "headline": "把斜面阶段从系统里独立出来",
                    "question": "为什么这里可以直接用动能定理？",
                    "takeaway": "斜面光滑，只有重力做功，机械转化最直接。",
                    "bullets": ["高度差为 Lsin30°", "初速度为 0", "直接得到 v_B"],
                },
                {
                    "stage_id": "belt",
                    "headline": "摩擦既改速度，也留下滑痕",
                    "question": "为什么滑痕长度不是物块位移？",
                    "takeaway": "滑痕是带面位移与物块位移的相对差。",
                    "bullets": ["摩擦力恒定", "先滑动后共速", "同时输出功与滑痕"],
                },
                {
                    "stage_id": "arc_entry",
                    "headline": "可动圆弧改变了系统边界",
                    "question": "为什么这里要看水平方向动量？",
                    "takeaway": "圆弧放在光滑水平面上，系统水平方向外力为零。",
                    "bullets": ["块和轨道共同运动", "能量分配给两者", "排除不合实际根"],
                },
                {
                    "stage_id": "arc_top",
                    "headline": "最高点只需沿半径方向列式",
                    "question": "法向力为什么和重力一起提供向心作用？",
                    "takeaway": "最高点时向心方向竖直向下，法向力与重力同向。",
                    "bullets": ["先求相对速度", "再列 F+mg=mv²/R", "得到压力答案"],
                },
            ],
            "controls": [
                {"id": "play", "label": "播放", "kind": "transport"},
                {"id": "step", "label": "逐步", "kind": "transport"},
                {"id": "stage", "label": "阶段切换", "kind": "stage-selector"},
            ],
            "playback_steps": [
                {"stage_id": "slope", "checkpoint": 0.25, "headline": "重力做功建立速度"},
                {"stage_id": "belt", "checkpoint": 0.5, "headline": "摩擦驱动共速"},
                {"stage_id": "arc_entry", "checkpoint": 0.75, "headline": "轨道与物块共同运动"},
                {"stage_id": "arc_top", "checkpoint": 1.0, "headline": "最高点受力判定"},
            ],
        }
    )
    return scene


def stage_index(stage_id: str) -> int:
    try:
        return STAGE_ORDER.index(stage_id)
    except ValueError:
        return 0


def normalized_stage_progress(stage_id: str, progress: float) -> float:
    stage_position = stage_index(stage_id)
    return min(1.0, max(0.0, (stage_position + progress) / max(len(STAGE_ORDER) - 1, 1)))
