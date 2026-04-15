from __future__ import annotations

import re
from typing import Dict, List

from backend.app.schemas.mechanics import MechanicsSolutionModel, MechanicsSolutionStep


def _extract_answer_tokens(final_answers: str) -> Dict[str, str]:
    if not final_answers:
        return {}
    raw_parts = [item.strip() for item in re.split(r"[;；\n]+", final_answers) if item.strip()]
    keys = ["q1", "q2", "q3", "q4"]
    return {key: raw_parts[index] for index, key in enumerate(keys[: len(raw_parts)])}


def extract_solution_model(normalized: Dict[str, str]) -> MechanicsSolutionModel:
    solution_text = normalized.get("solution_text", "")
    final_answers = normalized.get("final_answers", "")
    answer_map = _extract_answer_tokens(final_answers)
    if not solution_text and not answer_map:
        return MechanicsSolutionModel(available=False)

    laws: List[str] = []
    law_cues = {
        "动能定理": "动能定理",
        "机械能守恒": "机械能守恒",
        "动量守恒": "水平方向动量守恒",
        "牛顿第二定律": "牛顿第二定律",
    }
    for cue, law in law_cues.items():
        if cue in solution_text:
            laws.append(law)

    step_specs = [
        ("q1", "第1问", "动能定理", r"(mgsin30°L[^。]*?v=4m/s|解得\s*v=4m/s)"),
        ("q2", "第2问", "动能定理", r"(Wf[^。]*?0\.9J|摩擦力对其做功[^。]*?0\.9J)"),
        ("q3", "第3问", "牛顿第二定律", r"(滑痕[^。]*?0\.2m|Δx[^。]*?0\.2m)"),
        ("q4", "第4问", "牛顿第二定律", r"(F[^。]*?3N|压力[^。]*?3N)"),
    ]
    steps: List[MechanicsSolutionStep] = []
    for key, prompt, law, pattern in step_specs:
        evidence_match = re.search(pattern, solution_text)
        steps.append(
            MechanicsSolutionStep(
                id=key,
                prompt=prompt,
                law=law if law in laws or not laws else None,
                conclusion=answer_map.get(key),
                evidence=evidence_match.group(1) if evidence_match else None,
            )
        )

    return MechanicsSolutionModel(
        available=bool(solution_text or answer_map),
        answer_map=answer_map,
        laws=laws,
        steps=steps,
        source_fragments=[solution_text] if solution_text else [],
    )
