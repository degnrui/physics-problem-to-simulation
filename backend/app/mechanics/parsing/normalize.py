from __future__ import annotations

import base64
from typing import Any, Dict, Optional


def _compact_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return " ".join(value.replace("\u3000", " ").split())


def _preview_from_image(file_bytes: Optional[bytes], filename: Optional[str]) -> Dict[str, str]:
    if file_bytes:
        mime = "image/png"
        lowered = (filename or "").lower()
        if lowered.endswith(".jpg") or lowered.endswith(".jpeg"):
            mime = "image/jpeg"
        encoded = base64.b64encode(file_bytes).decode("ascii")
        return {"id": filename or "uploaded-mechanics-image", "data_url": f"data:{mime};base64,{encoded}"}
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' width='480' height='160'>"
        "<rect width='100%' height='100%' fill='#fffef9' rx='16'/>"
        "<text x='24' y='76' font-size='20' fill='#111827'>力学题文本输入</text>"
        "<text x='24' y='108' font-size='14' fill='#6b7280'>首版优先以题干/解析文本驱动抽模</text>"
        "</svg>"
    )
    return {"id": "mechanics-text-only", "svg": svg}


def normalize_mechanics_inputs(
    *,
    problem_text: Optional[str],
    solution_text: Optional[str],
    final_answers: Optional[str],
    image_bytes: Optional[bytes] = None,
    image_filename: Optional[str] = None,
) -> Dict[str, Any]:
    normalized_problem = _compact_text(problem_text)
    normalized_solution = _compact_text(solution_text)
    normalized_answers = _compact_text(final_answers)
    fragments = [fragment for fragment in [normalized_problem, normalized_solution, normalized_answers] if fragment]
    return {
        "problem_text": normalized_problem,
        "solution_text": normalized_solution,
        "final_answers": normalized_answers,
        "reference_image": _preview_from_image(image_bytes, image_filename),
        "paragraphs": fragments,
        "has_image": bool(image_bytes),
        "has_problem_text": bool(normalized_problem),
        "has_solution_text": bool(normalized_solution),
    }
