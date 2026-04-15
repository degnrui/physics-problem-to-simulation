from __future__ import annotations

from typing import Any, Dict


def build_mechanics_harness_packet(normalized: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "mode": "agent_harness",
        "executor": "dev_proxy",
        "intent": "指导通用 GAI 从题干、解析与答案中完成物理模型提取、校验与仿真回证。",
        "inputs": {
            "problem_text": normalized.get("problem_text", ""),
            "solution_text": normalized.get("solution_text", ""),
            "final_answers": normalized.get("final_answers", ""),
            "has_image": bool(normalized.get("has_image")),
        },
        "required_outputs": [
            "problem_representation",
            "candidate_models",
            "selected_model",
            "solution_model",
            "conflict_items",
            "verification_report",
            "final_simulation_spec",
            "confidence_breakdown",
        ],
        "guardrails": [
            "不要把参考答案硬拟合成唯一模型。",
            "题干模型与解析模型必须独立抽取，再做对齐。",
            "有冲突时默认拦截并要求确认，而不是静默修正。",
            "必须输出不确定项和关键假设。",
        ],
        "developer_note": (
            "开发测试阶段不直接调用外部模型 API。"
            "由本地代理执行器按 harness 要求跑完整链路，用于验证 harness 设计是否足以指导最终产品中的 GAI。"
        ),
    }
