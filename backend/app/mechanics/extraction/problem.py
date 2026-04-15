from __future__ import annotations

import re
from typing import Dict, List

from backend.app.schemas.mechanics import (
    MechanicsCandidateModel,
    MechanicsObject,
    MechanicsProblemRepresentation,
    MechanicsQuantity,
)


def _extract_number(text: str, symbol: str) -> float | None:
    patterns = {
        "R": r"R\s*=\s*([0-9.]+)",
        "L": r"L\s*=\s*([0-9.]+)",
        "v0": r"v0\s*=\s*([0-9.]+)",
        "m": r"m\s*=\s*([0-9.]+)",
        "M": r"M\s*=\s*([0-9.]+)",
        "mu": r"[μu]\s*=\s*([0-9.]+)",
        "theta": r"(30)\s*[°度]",
    }
    pattern = patterns.get(symbol)
    if not pattern:
        return None
    match = re.search(pattern, text)
    if not match:
        return None
    return float(match.group(1))


def _detect_belt_arc_problem(text: str) -> bool:
    cues = ["传送带", "圆弧轨道", "斜轨道", "摩擦", "滑痕"]
    return sum(cue in text for cue in cues) >= 3


def extract_problem_representation(normalized: Dict[str, str]) -> MechanicsProblemRepresentation:
    text = normalized.get("problem_text", "")
    quantities: List[MechanicsQuantity] = []
    symbol_map = {
        "R": "m",
        "L": "m",
        "v0": "m/s",
        "m": "kg",
        "M": "kg",
        "mu": "",
        "theta": "deg",
    }
    for symbol, unit in symbol_map.items():
        value = _extract_number(text, symbol)
        if value is None:
            continue
        quantities.append(
            MechanicsQuantity(symbol=symbol, value=value, unit=unit or None, text=f"{symbol}={value}", source="problem_text")
        )

    assumptions = []
    for cue in ["其余接触面均光滑", "不计空气阻力", "物块可视为质点", "传送带足够长"]:
        if cue in text:
            assumptions.append(cue)

    geometry = []
    if "30" in text:
        geometry.append("斜面倾角 30°")
    if "半圆弧轨道" in text or "半圆轨道" in text:
        geometry.append("半圆弧轨道")

    constraints = []
    for cue in ["水平传送带", "动摩擦因数", "恒定速率", "可动半圆弧轨道", "水平面与传送带处于同一高度"]:
        if cue in text:
            constraints.append(cue)

    goals = [
        "求 B 点速度",
        "求 B 到 C 摩擦力做功",
        "求滑痕长度",
        "求最高点压力",
    ]
    summary = "斜面-传送带-可动圆弧轨道的分段力学综合题"
    if not _detect_belt_arc_problem(text):
        summary = "待确认的力学题型"

    return MechanicsProblemRepresentation(
        summary=summary,
        objects=[
            MechanicsObject(id="block", label="物块", category="particle"),
            MechanicsObject(id="belt", label="传送带", category="kinematic_constraint"),
            MechanicsObject(id="arc", label="可动半圆弧轨道", category="moving_track"),
        ],
        known_quantities=quantities,
        unknown_quantities=[
            MechanicsQuantity(symbol="v_B", text="B 点速度", source="goal"),
            MechanicsQuantity(symbol="W_f", text="摩擦做功", source="goal"),
            MechanicsQuantity(symbol="dx", text="滑痕长度", source="goal"),
            MechanicsQuantity(symbol="N_top", text="最高点压力", source="goal"),
        ],
        constraints=constraints,
        geometry=geometry,
        assumptions=assumptions,
        goals=goals,
        stages=["斜面下滑", "传送带加速滑动", "进入可动圆弧", "到达最高点临界接触"],
        source_fragments=[text] if text else [],
    )


def build_candidate_models(problem: MechanicsProblemRepresentation) -> List[MechanicsCandidateModel]:
    base_stage_map = ["斜面动能定理", "传送带摩擦加速", "圆弧阶段水平动量守恒+机械能守恒", "最高点牛顿第二定律"]
    return [
        MechanicsCandidateModel(
            id="belt_arc_consistent",
            title="传送带共速 + 可动圆弧守恒模型",
            confidence=0.92 if problem.summary != "待确认的力学题型" else 0.58,
            state_variables=["v_B", "v_C", "v_block_top", "v_arc_top"],
            governing_laws=["动能定理", "牛顿第二定律", "机械能守恒", "水平方向动量守恒"],
            assumptions={
                "belt_reaches_speed": True,
                "ignore_air_drag": True,
                "point_mass": True,
                "smooth_except_belt": True,
            },
            approximations=["取 g=10m/s^2"],
            applicability=["斜面-传送带-可动圆弧组合题"],
            stage_map=base_stage_map,
            notes=["默认物块在传送带上先相对滑动，后达到带速"],
        ),
        MechanicsCandidateModel(
            id="belt_arc_guarded",
            title="保守审计模型",
            confidence=0.51,
            state_variables=["v_B", "v_exit"],
            governing_laws=["动能定理", "牛顿第二定律"],
            assumptions={
                "belt_reaches_speed": False,
                "treat_arc_as_fixed": False,
            },
            approximations=["只保证前两阶段可计算"],
            applicability=["输入不完整或解析存在冲突时作为兜底"],
            stage_map=["斜面动能定理", "传送带摩擦阶段待确认", "圆弧阶段待确认"],
            notes=["用于冲突拦截，不作为默认放行模型"],
        ),
    ]
