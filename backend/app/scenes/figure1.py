from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, List

from backend.app.schemas.scene import SceneDocument


ROOT_DIR = Path(__file__).resolve().parents[3]
REFERENCE_PATH = ROOT_DIR / "sample_data" / "figure1_reference.svg"

DEFAULT_STATE = {
    "switch_closed": False,
    "battery_voltage": 6.0,
    "resistor_value": 10.0,
    "rheostat_total": 20.0,
    "rheostat_ratio": 0.5,
}


def _component_map(scene: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {component["id"]: component for component in scene["components"]}


def _port_lookup(scene: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    lookup: Dict[str, Dict[str, float]] = {}
    for component in scene["components"]:
        if component["type"] == "junction":
            lookup[component["id"]] = {"x": component["x"], "y": component["y"]}
        for port in component.get("ports", []):
            lookup[f"{component['id']}.{port['id']}"] = {"x": port["x"], "y": port["y"]}
    return lookup


def resolve_wire_points(scene: Dict[str, Any], wire: Dict[str, Any]) -> List[Dict[str, float]]:
    lookup = _port_lookup(scene)
    points = [lookup[wire["start_ref"]], *wire.get("bends", []), lookup[wire["end_ref"]]]
    return [{"x": float(point["x"]), "y": float(point["y"])} for point in points]


def validate_figure1_geometry(scene: Dict[str, Any]) -> List[str]:
    validated_scene = SceneDocument.model_validate(scene).model_dump()
    lookup = _port_lookup(validated_scene)
    issues: List[str] = []
    for wire in validated_scene["wires"]:
        if wire["start_ref"] not in lookup:
            issues.append(f"Missing start_ref for {wire['id']}: {wire['start_ref']}")
        if wire["end_ref"] not in lookup:
            issues.append(f"Missing end_ref for {wire['id']}: {wire['end_ref']}")
    return issues


def _base_scene() -> Dict[str, Any]:
    return {
        "id": "figure-1",
        "title": "图 1 复刻式电路 Simulation",
        "canvas": {"width": 860, "height": 780},
        "components": [
            {
                "id": "switch",
                "type": "switch",
                "label": "S",
                "x": 38,
                "y": 252,
                "width": 110,
                "height": 250,
                "capabilities": {"toggleable": True},
                "style": {"stroke": "#111827"},
                "ports": [
                    {"id": "top", "x": 92, "y": 266},
                    {"id": "bottom", "x": 92, "y": 637},
                    {"id": "pivot", "x": 92, "y": 360},
                    {"id": "open_contact", "x": 36, "y": 470},
                    {"id": "closed_contact", "x": 92, "y": 470},
                ],
            },
            {
                "id": "battery",
                "type": "battery",
                "label": "E",
                "x": 145,
                "y": 580,
                "width": 120,
                "height": 115,
                "value": 6.0,
                "capabilities": {"editable_value": True},
                "ports": [
                    {"id": "left", "x": 92, "y": 637},
                    {"id": "right", "x": 390, "y": 637},
                ],
            },
            {
                "id": "resistor",
                "type": "resistor",
                "label": "R",
                "x": 430,
                "y": 242,
                "width": 150,
                "height": 48,
                "value": 10.0,
                "capabilities": {"editable_value": True},
                "ports": [
                    {"id": "left", "x": 430, "y": 266},
                    {"id": "right", "x": 580, "y": 266},
                ],
            },
            {
                "id": "rheostat",
                "type": "rheostat",
                "label": "P",
                "x": 390,
                "y": 618,
                "width": 170,
                "height": 42,
                "value": 20.0,
                "capabilities": {
                    "editable_value": True,
                    "slider_range": {"min_ratio": 0.0, "max_ratio": 1.0},
                },
                "ports": [
                    {"id": "left", "x": 390, "y": 637},
                    {"id": "right", "x": 560, "y": 637},
                    {"id": "slider_contact", "x": 474, "y": 618},
                ],
            },
            {
                "id": "ammeter",
                "type": "ammeter",
                "label": "A",
                "x": 695,
                "y": 420,
                "width": 90,
                "height": 90,
                "capabilities": {"removable": True},
                "ports": [
                    {"id": "top", "x": 740, "y": 420},
                    {"id": "bottom", "x": 740, "y": 510},
                ],
            },
            {
                "id": "voltmeter",
                "type": "voltmeter",
                "label": "V",
                "x": 500,
                "y": 84,
                "width": 112,
                "height": 112,
                "capabilities": {"removable": True},
                "ports": [
                    {"id": "left", "x": 500, "y": 140},
                    {"id": "right", "x": 612, "y": 140},
                ],
            },
            {"id": "junction_left", "type": "junction", "x": 430, "y": 266, "width": 18, "height": 18},
            {"id": "junction_right", "type": "junction", "x": 580, "y": 266, "width": 18, "height": 18},
            {"id": "junction_bottom", "type": "junction", "x": 560, "y": 637, "width": 18, "height": 18},
            {"id": "ammeter_top_node", "type": "junction", "x": 740, "y": 266, "width": 18, "height": 18},
            {"id": "ammeter_bottom_node", "type": "junction", "x": 740, "y": 637, "width": 18, "height": 18},
            {"id": "slider_tip", "type": "junction", "x": 474, "y": 540, "width": 18, "height": 18},
        ],
        "wires": [
            {
                "id": "main-left-top",
                "role": "main",
                "start_ref": "switch.top",
                "end_ref": "junction_left",
                "bends": [],
            },
            {
                "id": "resistor-right-link",
                "role": "main",
                "start_ref": "resistor.right",
                "end_ref": "junction_right",
                "bends": [],
            },
            {
                "id": "main-right-top",
                "role": "main",
                "start_ref": "junction_right",
                "end_ref": "ammeter_top_node",
                "bends": [],
            },
            {
                "id": "ammeter-upper",
                "role": "main",
                "start_ref": "ammeter_top_node",
                "end_ref": "ammeter.top",
                "bends": [],
            },
            {
                "id": "ammeter-lower",
                "role": "main",
                "start_ref": "ammeter.bottom",
                "end_ref": "ammeter_bottom_node",
                "bends": [],
            },
            {
                "id": "main-right-bottom",
                "role": "main",
                "start_ref": "ammeter_bottom_node",
                "end_ref": "junction_bottom",
                "bends": [{"x": 740, "y": 637}],
            },
            {
                "id": "main-bottom",
                "role": "main",
                "start_ref": "junction_bottom",
                "end_ref": "battery.right",
                "bends": [{"x": 390, "y": 637}],
            },
            {
                "id": "main-left-bottom",
                "role": "main",
                "start_ref": "battery.left",
                "end_ref": "switch.bottom",
                "bends": [],
            },
            {
                "id": "voltmeter-branch",
                "role": "meter",
                "start_ref": "junction_left",
                "end_ref": "voltmeter.left",
                "bends": [{"x": 430, "y": 140}],
            },
            {
                "id": "voltmeter-return",
                "role": "meter",
                "start_ref": "voltmeter.right",
                "end_ref": "junction_right",
                "bends": [{"x": 580, "y": 140}],
            },
            {
                "id": "slider-branch",
                "role": "pointer",
                "start_ref": "rheostat.slider_contact",
                "end_ref": "slider_tip",
                "bends": [],
            },
        ],
        "meter_anchors": [
            {"component_id": "ammeter", "x": 740, "y": 466},
            {"component_id": "voltmeter", "x": 556, "y": 140},
        ],
        "debug": {"status": "template", "overlay": "ports"},
    }


def build_figure1_scene() -> Dict[str, Any]:
    scene = SceneDocument.model_validate(_base_scene()).model_dump()
    return {
        "reference_image": {
            "id": "figure-1-reference",
            "svg": REFERENCE_PATH.read_text(encoding="utf-8"),
        },
        "scene": scene,
        "state": copy.deepcopy(DEFAULT_STATE),
    }


def compile_figure1_to_physics(scene: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    components = _component_map(scene)
    rheostat_effective = round(float(state["rheostat_total"]) * float(state["rheostat_ratio"]), 4)
    return {
        "metadata": {"title": scene["title"], "image_id": scene["id"]},
        "components": [
            {
                "id": "BAT1",
                "type": "voltage_source",
                "terminals": ["positive", "negative"],
                "value": float(state["battery_voltage"]),
                "source": "scene-template",
            },
            {
                "id": "R_FIXED",
                "type": "resistor",
                "terminals": ["a", "b"],
                "value": float(state["resistor_value"]),
                "source": "scene-template",
            },
            {
                "id": "R_SLIDER",
                "type": "resistor",
                "terminals": ["a", "b"],
                "value": max(rheostat_effective, 0.001),
                "source": "scene-template",
            },
            {
                "id": "SW1",
                "type": "switch",
                "terminals": ["a", "b"],
                "source": "scene-template",
            },
        ],
        "nodes": [{"id": "n1"}, {"id": "n2"}, {"id": "n3"}, {"id": "n0"}],
        "connections": [
            {"component_id": "BAT1", "terminal": "positive", "node_id": "n1"},
            {"component_id": "BAT1", "terminal": "negative", "node_id": "n0"},
            {"component_id": "SW1", "terminal": "a", "node_id": "n1"},
            {"component_id": "SW1", "terminal": "b", "node_id": "n2"},
            {"component_id": "R_FIXED", "terminal": "a", "node_id": "n2"},
            {"component_id": "R_FIXED", "terminal": "b", "node_id": "n3"},
            {"component_id": "R_SLIDER", "terminal": "a", "node_id": "n3"},
            {"component_id": "R_SLIDER", "terminal": "b", "node_id": "n0"},
        ],
        "parameters": {
            "switch_states": {"SW1": "closed" if state["switch_closed"] else "open"},
        },
        "simulation_config": {"analysis_type": "dc_operating_point"},
        "scene_metadata": {
            "enabled_components": {
                key: components[key]["enabled"]
                for key in ("ammeter", "voltmeter", "resistor", "rheostat", "switch", "battery")
            },
            "rheostat_ratio": float(state["rheostat_ratio"]),
            "rheostat_effective": rheostat_effective,
        },
    }


def simulate_figure1_scene(scene: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
    validated_scene = SceneDocument.model_validate(scene).model_dump()
    battery_voltage = float(state["battery_voltage"])
    resistor_value = max(float(state["resistor_value"]), 0.001)
    rheostat_total = max(float(state["rheostat_total"]), 0.001)
    rheostat_ratio = min(max(float(state["rheostat_ratio"]), 0.0), 1.0)
    rheostat_effective = rheostat_total * rheostat_ratio
    switch_closed = bool(state["switch_closed"])

    total_current = (
        battery_voltage / (resistor_value + max(rheostat_effective, 0.001))
        if switch_closed
        else 0.0
    )
    resistor_voltage = total_current * resistor_value if switch_closed else 0.0
    rheostat_voltage = total_current * rheostat_effective if switch_closed else 0.0

    return {
        "physics": compile_figure1_to_physics(
            validated_scene,
            {
                "switch_closed": switch_closed,
                "battery_voltage": battery_voltage,
                "resistor_value": resistor_value,
                "rheostat_total": rheostat_total,
                "rheostat_ratio": rheostat_ratio,
            },
        ),
        "meter_results": {
            "ammeter": round(total_current, 4),
            "voltmeter": round(resistor_voltage, 4),
        },
        "component_states": {
            "switch": {"state": "closed" if switch_closed else "open"},
            "battery": {"value": battery_voltage},
            "resistor": {"value": resistor_value},
            "rheostat": {
                "total": rheostat_total,
                "ratio": rheostat_ratio,
                "effective_resistance": round(rheostat_effective, 4),
            },
        },
        "visual_state": {
            "energized": switch_closed,
            "highlighted_wires": [
                wire["id"] for wire in validated_scene["wires"] if wire["role"] == "main"
            ]
            if switch_closed
            else [],
            "meter_visibility": {
                component["id"]: component["enabled"]
                for component in validated_scene["components"]
                if component["type"] in {"ammeter", "voltmeter"}
            },
        },
        "summary": {
            "source_voltage": battery_voltage,
            "total_current": round(total_current, 4),
            "resistor_voltage": round(resistor_voltage, 4),
            "rheostat_voltage": round(rheostat_voltage, 4),
        },
    }


def apply_figure1_edit(scene: Dict[str, Any], edit: Dict[str, Any]) -> Dict[str, Any]:
    validated = SceneDocument.model_validate(scene).model_dump()
    component_id = edit.get("component_id")
    action = edit.get("action")
    components = _component_map(validated)
    if component_id not in components:
        raise ValueError(f"Unknown component_id: {component_id}")
    target = components[component_id]
    if action == "remove_component":
        if not target["capabilities"]["removable"]:
            raise ValueError(f"Component is not removable: {component_id}")
        target["enabled"] = False
    elif action == "restore_component":
        target["enabled"] = True
    else:
        raise ValueError(f"Unsupported edit action: {action}")
    return validated
