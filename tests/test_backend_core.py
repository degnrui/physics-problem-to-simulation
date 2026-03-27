import importlib
import unittest


def load_attr(module_name: str, attr_name: str):
    try:
        module = importlib.import_module(module_name)
    except ImportError as exc:
        raise AssertionError(f"Could not import {module_name}: {exc}") from exc
    try:
        return getattr(module, attr_name)
    except AttributeError as exc:
        raise AssertionError(f"Missing {attr_name} in {module_name}") from exc


class BackendCoreTests(unittest.TestCase):
    def test_physics_json_schema_accepts_minimal_series_circuit(self):
        PhysicsJsonDocument = load_attr(
            "backend.app.schemas.physics", "PhysicsJsonDocument"
        )

        document = PhysicsJsonDocument.model_validate(
            {
                "metadata": {"title": "Series sample"},
                "components": [
                    {
                        "id": "V1",
                        "type": "voltage_source",
                        "terminals": ["positive", "negative"],
                        "value": 10.0,
                        "source": "manual",
                    },
                    {
                        "id": "R1",
                        "type": "resistor",
                        "terminals": ["a", "b"],
                        "value": 5.0,
                        "source": "manual",
                    },
                ],
                "nodes": [{"id": "n1"}, {"id": "n0"}],
                "connections": [
                    {"component_id": "V1", "terminal": "positive", "node_id": "n1"},
                    {"component_id": "V1", "terminal": "negative", "node_id": "n0"},
                    {"component_id": "R1", "terminal": "a", "node_id": "n1"},
                    {"component_id": "R1", "terminal": "b", "node_id": "n0"},
                ],
                "parameters": {},
                "simulation_config": {"analysis_type": "dc_operating_point"},
            }
        )

        self.assertEqual(document.components[0].id, "V1")
        self.assertEqual(document.components[1].type, "resistor")

    def test_compile_detection_promotes_candidates_to_editable_topology(self):
        compile_detection_to_physics = load_attr(
            "backend.app.abstraction.compiler", "compile_detection_to_physics"
        )

        payload = {
            "metadata": {"image_id": "sample"},
            "components": [
                {
                    "id": "candidate_v1",
                    "type": "voltage_source",
                    "bbox": {"x": 30, "y": 20, "width": 20, "height": 40},
                    "confidence": 0.95,
                    "source": "vision",
                },
                {
                    "id": "candidate_r1",
                    "type": "resistor",
                    "bbox": {"x": 120, "y": 20, "width": 50, "height": 30},
                    "confidence": 0.88,
                    "source": "vision",
                },
            ],
            "wires": [
                {
                    "id": "wire-1",
                    "points": [[50, 40], [120, 40]],
                    "confidence": 0.83,
                    "source": "vision",
                }
            ],
            "nodes": [
                {"id": "n1", "x": 50, "y": 40, "source": "vision"},
                {"id": "n2", "x": 120, "y": 40, "source": "vision"},
            ],
            "texts": [],
        }

        physics = compile_detection_to_physics(payload)

        self.assertEqual(physics["metadata"]["image_id"], "sample")
        self.assertGreaterEqual(len(physics["components"]), 2)
        self.assertTrue(any(item["type"] == "resistor" for item in physics["components"]))
        self.assertGreaterEqual(len(physics["nodes"]), 2)

    def test_dc_solver_handles_simple_series_circuit(self):
        simulate_circuit = load_attr("backend.app.simulation.solver", "simulate_circuit")

        result = simulate_circuit(
            {
                "metadata": {"title": "Series"},
                "components": [
                    {
                        "id": "V1",
                        "type": "voltage_source",
                        "terminals": ["positive", "negative"],
                        "value": 12.0,
                        "source": "manual",
                    },
                    {
                        "id": "R1",
                        "type": "resistor",
                        "terminals": ["a", "b"],
                        "value": 6.0,
                        "source": "manual",
                    },
                ],
                "nodes": [{"id": "n1"}, {"id": "n0"}],
                "connections": [
                    {"component_id": "V1", "terminal": "positive", "node_id": "n1"},
                    {"component_id": "V1", "terminal": "negative", "node_id": "n0"},
                    {"component_id": "R1", "terminal": "a", "node_id": "n1"},
                    {"component_id": "R1", "terminal": "b", "node_id": "n0"},
                ],
                "parameters": {},
                "simulation_config": {"analysis_type": "dc_operating_point"},
            }
        )

        self.assertAlmostEqual(result["component_results"]["R1"]["current"], 2.0, places=3)
        self.assertAlmostEqual(result["component_results"]["R1"]["voltage_drop"], 12.0, places=3)

    def test_dc_solver_handles_parallel_resistors(self):
        simulate_circuit = load_attr("backend.app.simulation.solver", "simulate_circuit")

        result = simulate_circuit(
            {
                "metadata": {"title": "Parallel"},
                "components": [
                    {
                        "id": "V1",
                        "type": "voltage_source",
                        "terminals": ["positive", "negative"],
                        "value": 12.0,
                        "source": "manual",
                    },
                    {
                        "id": "R1",
                        "type": "resistor",
                        "terminals": ["a", "b"],
                        "value": 6.0,
                        "source": "manual",
                    },
                    {
                        "id": "R2",
                        "type": "resistor",
                        "terminals": ["a", "b"],
                        "value": 3.0,
                        "source": "manual",
                    },
                ],
                "nodes": [{"id": "n1"}, {"id": "n0"}],
                "connections": [
                    {"component_id": "V1", "terminal": "positive", "node_id": "n1"},
                    {"component_id": "V1", "terminal": "negative", "node_id": "n0"},
                    {"component_id": "R1", "terminal": "a", "node_id": "n1"},
                    {"component_id": "R1", "terminal": "b", "node_id": "n0"},
                    {"component_id": "R2", "terminal": "a", "node_id": "n1"},
                    {"component_id": "R2", "terminal": "b", "node_id": "n0"},
                ],
                "parameters": {},
                "simulation_config": {"analysis_type": "dc_operating_point"},
            }
        )

        self.assertAlmostEqual(result["component_results"]["R1"]["current"], 2.0, places=3)
        self.assertAlmostEqual(result["component_results"]["R2"]["current"], 4.0, places=3)
        self.assertAlmostEqual(result["summary"]["total_current"], 6.0, places=3)

    def test_dc_solver_handles_open_switch(self):
        simulate_circuit = load_attr("backend.app.simulation.solver", "simulate_circuit")

        result = simulate_circuit(
            {
                "metadata": {"title": "Open switch"},
                "components": [
                    {
                        "id": "V1",
                        "type": "voltage_source",
                        "terminals": ["positive", "negative"],
                        "value": 9.0,
                        "source": "manual",
                    },
                    {
                        "id": "S1",
                        "type": "switch",
                        "terminals": ["a", "b"],
                        "source": "manual",
                    },
                    {
                        "id": "R1",
                        "type": "resistor",
                        "terminals": ["a", "b"],
                        "value": 9.0,
                        "source": "manual",
                    },
                ],
                "nodes": [{"id": "n1"}, {"id": "n2"}, {"id": "n0"}],
                "connections": [
                    {"component_id": "V1", "terminal": "positive", "node_id": "n1"},
                    {"component_id": "V1", "terminal": "negative", "node_id": "n0"},
                    {"component_id": "S1", "terminal": "a", "node_id": "n1"},
                    {"component_id": "S1", "terminal": "b", "node_id": "n2"},
                    {"component_id": "R1", "terminal": "a", "node_id": "n2"},
                    {"component_id": "R1", "terminal": "b", "node_id": "n0"},
                ],
                "parameters": {"switch_states": {"S1": "open"}},
                "simulation_config": {"analysis_type": "dc_operating_point"},
            }
        )

        self.assertAlmostEqual(result["summary"]["total_current"], 0.0, places=6)
        self.assertEqual(result["component_results"]["S1"]["state"], "open")


if __name__ == "__main__":
    unittest.main()
