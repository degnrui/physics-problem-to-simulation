from __future__ import annotations

from typing import Any, Dict, List

from app.orchestrator.review import run_stage_review
from app.orchestrator.state import append_trace, set_stage_status

from ..common import issue


def _scene_build(inputs: Dict[str, Dict[str, Any]], _: Dict[str, Any], __: Dict[str, Any]) -> Dict[str, Any]:
    domain = inputs["domain_grounding"]["domain_type"]
    return {
        "template_family": f"{domain}_studio",
        "entities": [
            {"id": "primary-body", "kind": "body"},
            {"id": "reference-axis", "kind": "axis"},
        ],
        "spatial_layout": {"camera": "front", "anchor": "center"},
        "state_anchors": ["position", "velocity", "energy"],
    }


def _scene_validate(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for key in ["template_family", "entities", "spatial_layout", "state_anchors"]:
        if candidate.get(key) in (None, "", [], {}):
            issues.append(issue("MISSING_FIELD", f"scene_design missing `{key}`.", key))
    if not any(entity.get("id") == "primary-body" for entity in candidate.get("entities", [])):
        issues.append(issue("MISSING_PRIMARY_ENTITY", "scene_design requires a primary-body entity.", "entities"))
    return issues


def _scene_repair(
    _: Dict[str, Any],
    __: List[Dict[str, Any]],
    inputs: Dict[str, Dict[str, Any]],
    ___: Dict[str, Any],
    ____: Dict[str, Any],
) -> Dict[str, Any]:
    return _scene_build(inputs, {}, {})


def _scene_approve(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    if "position" not in candidate.get("state_anchors", []):
        return [issue("MISSING_POSITION", "scene_design must expose a position state anchor.", "state_anchors")]
    return []


def _control_build(inputs: Dict[str, Dict[str, Any]], _: Dict[str, Any], __: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "controls": [
            {"id": "play", "label": "Play", "input_type": "button", "default": "play", "state_binding": "isPlaying"},
            {"id": "pause", "label": "Pause", "input_type": "button", "default": "pause", "state_binding": "isPlaying"},
            {"id": "reset", "label": "Reset", "input_type": "button", "default": "reset", "state_binding": "time"},
            {"id": "mass", "label": "Mass", "input_type": "range", "default": "1.0", "state_binding": "mass", "min": "0.5", "max": "3.0"},
        ],
        "runtime_state": ["isPlaying", "time", "mass"],
    }


def _control_validate(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    controls = candidate.get("controls") or []
    ids = {control.get("id") for control in controls}
    for required in {"play", "pause", "reset"}:
        if required not in ids:
            issues.append(issue("MISSING_CONTROL", f"control_design requires `{required}`.", "controls"))
    if not any(control.get("id") not in {"play", "pause", "reset"} for control in controls):
        issues.append(issue("NO_STATE_CONTROL", "control_design needs an additional state-changing control.", "controls"))
    return issues


def _control_repair(
    _: Dict[str, Any],
    __: List[Dict[str, Any]],
    inputs: Dict[str, Dict[str, Any]],
    ___: Dict[str, Any],
    ____: Dict[str, Any],
) -> Dict[str, Any]:
    return _control_build(inputs, {}, {})


def _control_approve(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    for control in candidate.get("controls", []):
        if not control.get("state_binding"):
            return [issue("MISSING_BINDING", "Every control needs a state_binding.", "controls")]
    return []


def _chart_build(inputs: Dict[str, Dict[str, Any]], _: Dict[str, Any], __: Dict[str, Any]) -> Dict[str, Any]:
    priorities = inputs["instructional_modeling"]["observation_priorities"]
    return {
        "charts": [{"id": "state-chart", "title": priorities[0], "state_binding": "mass"}],
        "measurement_panels": [{"id": "measurement-panel", "title": "Measurement Panel", "state_binding": "mass"}],
    }


def _chart_validate(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not candidate.get("charts") and not candidate.get("measurement_panels"):
        return [issue("MISSING_EVIDENCE_UI", "chart_measurement_design requires charts or measurement panels.", "charts")]
    return []


def _chart_repair(
    _: Dict[str, Any],
    __: List[Dict[str, Any]],
    inputs: Dict[str, Dict[str, Any]],
    ___: Dict[str, Any],
    ____: Dict[str, Any],
) -> Dict[str, Any]:
    return _chart_build(inputs, {}, {})


def _chart_approve(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    for item in candidate.get("charts", []) + candidate.get("measurement_panels", []):
        if not item.get("state_binding"):
            return [issue("MISSING_BINDING", "Charts and measurement panels need state bindings.", "charts")]
    return []


def _view_build(inputs: Dict[str, Dict[str, Any]], _: Dict[str, Any], __: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "teacher": {"id": "teacher", "default_panels": ["canvas", "measurement-panel", "state-chart"], "summary": "Lead with evidence and explanation."},
        "student": {"id": "student", "default_panels": ["canvas", "controls", "state-chart"], "summary": "Explore the parameter-response link."},
    }


def _view_validate(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for key in ["teacher", "student"]:
        if candidate.get(key) in (None, {}):
            issues.append(issue("MISSING_PRESET", f"pedagogical_view_design missing `{key}` preset.", key))
    return issues


def _view_repair(
    _: Dict[str, Any],
    __: List[Dict[str, Any]],
    inputs: Dict[str, Dict[str, Any]],
    ___: Dict[str, Any],
    ____: Dict[str, Any],
) -> Dict[str, Any]:
    return _view_build(inputs, {}, {})


def _view_approve(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    for preset in candidate.values():
        if "canvas" not in preset.get("default_panels", []):
            return [issue("MISSING_CANVAS_PANEL", "Every preset must show the canvas panel.", "default_panels")]
    return []


def _merge_build(inputs: Dict[str, Dict[str, Any]], _: Dict[str, Any], __: Dict[str, Any]) -> Dict[str, Any]:
    controls = inputs["control_design"]["controls"]
    charts = inputs["chart_measurement_design"]["charts"]
    measurements = inputs["chart_measurement_design"]["measurement_panels"]
    scene = inputs["scene_design"]
    views = inputs["pedagogical_view_design"]
    return {
        "title": "Physics Runtime Studio",
        "subtitle": "Validated interactive runtime package",
        "scene": scene,
        "controls": controls,
        "charts": charts,
        "measurement_panels": measurements,
        "pedagogical_views": views,
    }


def _merge_validate(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    if not candidate.get("controls"):
        issues.append(issue("MISSING_CONTROLS", "design_merge requires controls.", "controls"))
    if not candidate.get("charts") and not candidate.get("measurement_panels"):
        issues.append(issue("MISSING_EVIDENCE_UI", "design_merge requires charts or measurement panels.", "charts"))
    return issues


def _merge_repair(
    _: Dict[str, Any],
    __: List[Dict[str, Any]],
    inputs: Dict[str, Dict[str, Any]],
    ___: Dict[str, Any],
    ____: Dict[str, Any],
) -> Dict[str, Any]:
    return _merge_build(inputs, {}, {})


def _merge_approve(candidate: Dict[str, Any], _: Dict[str, Dict[str, Any]], __: Dict[str, Any], ___: Dict[str, Any]) -> List[Dict[str, Any]]:
    teacher_panels = candidate["pedagogical_views"]["teacher"]["default_panels"]
    if "measurement-panel" not in teacher_panels and "state-chart" not in teacher_panels:
        return [issue("MISSING_TEACHER_EVIDENCE", "Teacher preset must include evidence surfaces.", "pedagogical_views")]
    return []


SUBNODE_DEFINITIONS = {
    "scene_design": (_scene_build, _scene_validate, _scene_repair, _scene_approve),
    "control_design": (_control_build, _control_validate, _control_repair, _control_approve),
    "chart_measurement_design": (_chart_build, _chart_validate, _chart_repair, _chart_approve),
    "pedagogical_view_design": (_view_build, _view_validate, _view_repair, _view_approve),
    "design_merge": (_merge_build, _merge_validate, _merge_repair, _merge_approve),
}


def run_simulation_design_subgraph(state: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    approved_inputs = {
        "request_analysis": state["approved_artifacts"]["request_analysis"],
        "domain_grounding": state["approved_artifacts"]["domain_grounding"],
        "instructional_modeling": state["approved_artifacts"]["instructional_modeling"],
    }
    subgraph_inputs = dict(approved_inputs)
    append_trace(state, stage="simulation_design", event="subgraph_started")
    for node in ["scene_design", "control_design", "chart_measurement_design", "pedagogical_view_design", "design_merge"]:
        builder, validator, repairer, approver = SUBNODE_DEFINITIONS[node]
        candidate = run_stage_review(
            state=state,
            stage=node,
            inputs=subgraph_inputs,
            worker=builder,
            validator=validator,
            approver=approver,
            repairer=repairer,
            context=context,
        )
        subgraph_inputs[node] = candidate
    final_design = {
        **subgraph_inputs["design_merge"],
        "controls": subgraph_inputs["control_design"]["controls"],
        "charts": subgraph_inputs["chart_measurement_design"]["charts"],
        "measurement_panels": subgraph_inputs["chart_measurement_design"]["measurement_panels"],
        "scene": subgraph_inputs["scene_design"],
        "pedagogical_views": subgraph_inputs["pedagogical_view_design"],
    }
    state["artifacts"]["simulation_design"] = final_design
    state["approved_artifacts"]["simulation_design"] = final_design
    context["artifact_store"].write_json_artifact("simulation_design", final_design)
    set_stage_status(state, stage="simulation_design", status="approved", attempts=1, issues=[])
    append_trace(state, stage="simulation_design", event="approved", details={"child_nodes": list(SUBNODE_DEFINITIONS.keys())})
    return final_design
