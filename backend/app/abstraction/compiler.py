from __future__ import annotations

from typing import Any, Dict

from backend.app.schemas.physics import DetectionDocument


DEFAULT_TERMINALS = {
    "voltage_source": ["positive", "negative"],
    "resistor": ["a", "b"],
    "switch": ["a", "b"],
}


def compile_detection_to_physics(payload: Dict[str, Any]) -> Dict[str, Any]:
    detection = DetectionDocument.model_validate(payload)
    physics = {
        "metadata": detection.metadata.model_dump(),
        "components": [],
        "nodes": [{"id": node.id} for node in detection.nodes],
        "connections": [],
        "parameters": {"switch_states": {}},
        "simulation_config": {"analysis_type": "dc_operating_point"},
    }

    sorted_nodes = sorted(detection.nodes, key=lambda item: (item.x, item.y))
    if len(sorted_nodes) < 2:
        sorted_nodes = sorted(detection.nodes, key=lambda item: item.id)

    for component in detection.components:
        physics["components"].append(
            {
                "id": component.id,
                "type": component.type,
                "terminals": DEFAULT_TERMINALS[component.type],
                "value": 10.0 if component.type == "voltage_source" else 100.0
                if component.type == "resistor"
                else None,
                "source": component.source,
                "confidence": component.confidence,
                "bbox": component.bbox.model_dump(),
            }
        )

    if len(sorted_nodes) >= 2:
        left_node = sorted_nodes[0].id
        right_node = sorted_nodes[-1].id
        for component in physics["components"]:
            terminals = component["terminals"]
            physics["connections"].append(
                {
                    "component_id": component["id"],
                    "terminal": terminals[0],
                    "node_id": left_node,
                }
            )
            physics["connections"].append(
                {
                    "component_id": component["id"],
                    "terminal": terminals[1],
                    "node_id": right_node,
                }
            )
            if component["type"] == "switch":
                physics["parameters"]["switch_states"][component["id"]] = "open"

    return physics
