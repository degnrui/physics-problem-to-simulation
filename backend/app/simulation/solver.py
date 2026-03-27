from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np

from backend.app.schemas.physics import PhysicsJsonDocument


@dataclass
class DisjointSet:
    parent: Dict[str, str]

    def find(self, item: str) -> str:
        parent = self.parent.setdefault(item, item)
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left: str, right: str) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root != right_root:
            self.parent[right_root] = left_root


def _component_nodes(document: PhysicsJsonDocument) -> Dict[str, Dict[str, str]]:
    mapping: Dict[str, Dict[str, str]] = {}
    for connection in document.connections:
        mapping.setdefault(connection.component_id, {})[connection.terminal] = connection.node_id
    return mapping


def simulate_circuit(payload: Dict[str, Any]) -> Dict[str, Any]:
    document = PhysicsJsonDocument.model_validate(payload)
    component_nodes = _component_nodes(document)
    switch_states = document.parameters.get("switch_states", {})

    dsu = DisjointSet(parent={node.id: node.id for node in document.nodes})
    for component in document.components:
        if component.type == "switch" and switch_states.get(component.id, "closed") == "closed":
            node_map = component_nodes.get(component.id, {})
            if len(node_map) == 2:
                nodes = list(node_map.values())
                dsu.union(nodes[0], nodes[1])

    canonical_nodes = sorted({dsu.find(node.id) for node in document.nodes})
    if not canonical_nodes:
        raise ValueError("Circuit must define at least one node")

    voltage_source = next(
        (component for component in document.components if component.type == "voltage_source"),
        None,
    )
    if voltage_source is None:
        raise ValueError("At least one voltage source is required")

    source_nodes = component_nodes[voltage_source.id]
    positive_node = dsu.find(source_nodes["positive"])
    ground_node = dsu.find(source_nodes["negative"])
    fixed_voltages = {ground_node: 0.0, positive_node: float(voltage_source.value)}

    unknown_nodes = [node for node in canonical_nodes if node not in fixed_voltages]
    node_index = {node: index for index, node in enumerate(unknown_nodes)}
    conductance = np.zeros((len(unknown_nodes), len(unknown_nodes)))
    rhs = np.zeros(len(unknown_nodes))

    resistor_components = []
    for component in document.components:
        if component.type != "resistor":
            continue
        node_map = component_nodes.get(component.id, {})
        left = dsu.find(node_map[component.terminals[0]])
        right = dsu.find(node_map[component.terminals[1]])
        resistor_components.append((component.id, left, right, float(component.value)))

    for _, left, right, resistance in resistor_components:
        if resistance <= 0:
            raise ValueError("Resistor value must be positive")
        conduct = 1.0 / resistance
        if left in node_index:
            conductance[node_index[left], node_index[left]] += conduct
        if right in node_index:
            conductance[node_index[right], node_index[right]] += conduct
        if left in node_index and right in node_index:
            conductance[node_index[left], node_index[right]] -= conduct
            conductance[node_index[right], node_index[left]] -= conduct
        elif left in node_index and right in fixed_voltages:
            rhs[node_index[left]] += conduct * fixed_voltages[right]
        elif right in node_index and left in fixed_voltages:
            rhs[node_index[right]] += conduct * fixed_voltages[left]

    solved = np.linalg.solve(conductance, rhs) if len(unknown_nodes) else np.array([])
    node_voltages = {node: fixed_voltages[node] for node in fixed_voltages}
    for node, index in node_index.items():
        node_voltages[node] = float(solved[index])

    component_results: Dict[str, Dict[str, Any]] = {}
    total_current = 0.0
    for component in document.components:
        node_map = component_nodes.get(component.id, {})
        terminals = {
            terminal: dsu.find(node_map[terminal]) for terminal in component.terminals if terminal in node_map
        }
        if component.type == "voltage_source":
            component_results[component.id] = {
                "voltage": float(component.value),
                "positive_node": terminals.get("positive"),
                "negative_node": terminals.get("negative"),
            }
            continue
        if component.type == "switch":
            state = switch_states.get(component.id, "closed")
            component_results[component.id] = {"state": state}
            continue
        left = terminals[component.terminals[0]]
        right = terminals[component.terminals[1]]
        voltage_drop = node_voltages[left] - node_voltages[right]
        current = voltage_drop / float(component.value)
        total_current += current if left == positive_node else 0.0
        component_results[component.id] = {
            "current": float(current),
            "voltage_drop": float(voltage_drop),
            "left_node": left,
            "right_node": right,
        }

    if not resistor_components:
        total_current = 0.0
    else:
        total_current = sum(
            result.get("current", 0.0)
            for result in component_results.values()
            if result.get("left_node") == positive_node
        )

    return {
        "normalized_circuit": document.model_dump(),
        "node_results": {
            node: {"voltage": voltage} for node, voltage in sorted(node_voltages.items())
        },
        "component_results": component_results,
        "summary": {
            "source_voltage": float(voltage_source.value),
            "total_current": float(total_current),
        },
        "view_model": {
            "highlights": [
                {
                    "component_id": component_id,
                    "label": (
                        f"I={result['current']:.3f} A"
                        if "current" in result
                        else result.get("state", "source")
                    ),
                }
                for component_id, result in component_results.items()
            ]
        },
    }
