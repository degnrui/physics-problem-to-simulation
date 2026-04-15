from __future__ import annotations

import math
from typing import Dict

from backend.app.schemas.mechanics import (
    MechanicsAnswerResult,
    MechanicsCandidateModel,
    MechanicsProblemRepresentation,
    MechanicsSimulationResult,
)


def _quantity_value(problem: MechanicsProblemRepresentation, symbol: str, default: float) -> float:
    for quantity in problem.known_quantities:
        if quantity.symbol == symbol and quantity.value is not None:
            return float(quantity.value)
    return default


def _round(value: float) -> float:
    return round(value + 1e-9, 4)


def _format_answer(value: float, unit: str) -> str:
    if abs(value - round(value)) < 1e-9:
        rendered = str(int(round(value)))
    else:
        rendered = f"{value:.3f}".rstrip("0").rstrip(".")
    return f"{rendered} {unit}".strip()


def _solve_top_stage(v0: float, m: float, M: float, R: float, g: float) -> Dict[str, float]:
    mass_ratio = m / M
    a = 1.0 + mass_ratio
    b = -2.0 * mass_ratio * v0
    c = mass_ratio * v0 * v0 + 4.0 * g * R - v0 * v0
    discriminant = max(0.0, b * b - 4 * a * c)
    roots = [
        (-b + math.sqrt(discriminant)) / (2 * a),
        (-b - math.sqrt(discriminant)) / (2 * a),
    ]
    candidates = []
    for v_block in roots:
        v_arc = m * (v0 - v_block) / M
        candidates.append((v_block, v_arc, v_block - v_arc))
    feasible = [item for item in candidates if item[2] < 0]
    chosen = feasible[0] if feasible else candidates[0]
    return {"v_block_top": chosen[0], "v_arc_top": chosen[1], "v_relative_top": chosen[2]}


def simulate_candidate_model(
    problem: MechanicsProblemRepresentation,
    candidate: MechanicsCandidateModel,
    expected_answers: Dict[str, str] | None = None,
) -> MechanicsSimulationResult:
    g = 10.0
    theta = math.radians(_quantity_value(problem, "theta", 30.0))
    L = _quantity_value(problem, "L", 1.6)
    v0 = _quantity_value(problem, "v0", 5.0)
    m = _quantity_value(problem, "m", 0.2)
    M = _quantity_value(problem, "M", 1.8)
    mu = _quantity_value(problem, "mu", 0.25)
    R = _quantity_value(problem, "R", 0.36)

    v_b = math.sqrt(max(0.0, 2 * g * math.sin(theta) * L))
    a_belt = mu * g
    if candidate.assumptions.get("belt_reaches_speed", False):
        belt_time = max(0.0, (v0 - v_b) / max(a_belt, 1e-6))
        work = 0.5 * m * max(0.0, v0 * v0 - v_b * v_b)
        slip = max(0.0, v0 * belt_time - (v_b + v0) * belt_time / 2)
        v_entry = v0
    else:
        belt_time = max(0.0, (v0 - v_b) / max(a_belt, 1e-6))
        work = 0.5 * m * max(0.0, (v_b + a_belt * belt_time) ** 2 - v_b * v_b)
        slip = max(0.0, (v0 - v_b) * belt_time / 3)
        v_entry = min(v0, v_b + a_belt * belt_time * 0.6)

    top_stage = _solve_top_stage(v_entry, m, M, R, g)
    normal_force = m * (top_stage["v_relative_top"] ** 2) / R - m * g

    answer_specs = {
        "q1": ("B 点速度", v_b, "m/s"),
        "q2": ("摩擦力做功", work, "J"),
        "q3": ("滑痕长度", slip, "m"),
        "q4": ("最高点压力", normal_force, "N"),
    }
    answers = {}
    for key, (label, value, unit) in answer_specs.items():
        rounded = _round(value)
        display = _format_answer(rounded, unit)
        expected = expected_answers.get(key) if expected_answers else None
        normalized_expected = (expected or "").replace(" ", "")
        matches = None
        if expected:
            matches = normalized_expected == display.replace(" ", "")
        answers[key] = MechanicsAnswerResult(
            key=key,
            label=label,
            value=rounded,
            unit=unit,
            display_value=display,
            expected_value=expected,
            matches_reference=matches,
        )

    return MechanicsSimulationResult(
        model_id=candidate.id,
        answers=answers,
        stage_results={
            "slope": {"v_b": _round(v_b)},
            "belt": {"time": _round(belt_time), "acceleration": _round(a_belt), "slip_length": _round(slip)},
            "arc_top": {key: _round(value) for key, value in top_stage.items()},
        },
        derived_values={
            "g": g,
            "theta_rad": theta,
            "belt_acceleration": _round(a_belt),
        },
        summary={
            "selected_model": candidate.title,
            "belt_reaches_speed": candidate.assumptions.get("belt_reaches_speed", False),
        },
    )
