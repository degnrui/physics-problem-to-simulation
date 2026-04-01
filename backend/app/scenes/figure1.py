from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict

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
                "x": 60,
                "y": 180,
                "width": 70,
                "height": 180,
                "capabilities": {"toggleable": True},
                "style": {"stroke": "#111827"},
            },
            {
                "id": "battery",
                "type": "battery",
                "label": "E",
                "x": 145,
                "y": 615,
                "width": 120,
                "height": 62,
                "value": 6.0,
                "capabilities": {"editable_value": True},
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
            },
            {
                "id": "junction_left",
                "type": "junction",
                "x": 402,
                "y": 266,
                "width": 18,
                "height": 18,
            },
            {
                "id": "junction_right",
                "type": "junction",
                "x": 642,
                "y": 266,
                "width": 18,
                "height": 18,
            },
            {
                "id": "junction_bottom",
                "type": "junction",
                "x": 592,
                "y": 637,
                "width": 18,
                "height": 18,
            },
        ],
        "wires": [
            {
                "id": "main-left-top",
                "role": "main",
                "points": [{"x": 126, "y": 266}, {"x": 402, "y": 266}],
            },
            {
                "id": "main-right-vertical",
                "role": "main",
                "points": [{"x": 652, "y": 266}, {"x": 738, "y": 266}, {"x": 738, "y": 635}],
            },
            {
                "id": "main-bottom",
                "role": "main",
                "points": [{"x": 592, "y": 637}, {"x": 266, "y": 637}],
            },
            {
                "id": "main-left-bottom",
                "role": "main",
                "points": [{"x": 145, "y": 637}, {"x": 92, "y": 637}, {"x": 92, "y": 360}],
            },
            {
                "id": "voltmeter-branch",
                "role": "meter",
                "points": [{"x": 402, "y": 266}, {"x": 402, "y": 138}, {"x": 500, "y": 138}],
            },
            {
                "id": "voltmeter-return",
                "role": "meter",
                "points": [{"x": 612, "y": 138}, {"x": 642, "y": 138}, {"x": 642, "y": 266}],
            },
            {
                "id": "rheostat-pointer",
                "role": "pointer",
                "points": [{"x": 474, "y": 540}, {"x": 474, "y": 618}],
            },
        ],
        "meter_anchors": [
            {"component_id": "ammeter", "x": 740, "y": 466},
            {"component_id": "voltmeter", "x": 556, "y": 140},
        ],
        "debug": {"status": "template"},
    }


def _component_map(scene: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {component["id"]: component for component in scene["components"]}


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
        "physics": compile_figure1_to_physics(validated_scene, {
            "switch_closed": switch_closed,
            "battery_voltage": battery_voltage,
            "resistor_value": resistor_value,
            "rheostat_total": rheostat_total,
            "rheostat_ratio": rheostat_ratio,
        }),
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
