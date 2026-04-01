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

    def test_scene_template_builds_figure1_scene(self):
        build_figure1_scene = load_attr(
            "backend.app.scenes.figure1", "build_figure1_scene"
        )

        scene = build_figure1_scene()

        self.assertEqual(scene["scene"]["id"], "figure-1")
        self.assertEqual(scene["scene"]["canvas"]["width"], 860)
        component_types = {component["type"] for component in scene["scene"]["components"]}
        self.assertTrue(
            {
                "battery",
                "switch",
                "resistor",
                "rheostat",
                "ammeter",
                "voltmeter",
            }.issubset(component_types)
        )

    def test_figure1_simulation_returns_meter_results_when_closed(self):
        build_figure1_scene = load_attr(
            "backend.app.scenes.figure1", "build_figure1_scene"
        )
        simulate_scene = load_attr(
            "backend.app.scenes.figure1", "simulate_figure1_scene"
        )

        scene = build_figure1_scene()
        result = simulate_scene(
            scene["scene"],
            {
                "switch_closed": True,
                "battery_voltage": 6.0,
                "resistor_value": 10.0,
                "rheostat_total": 20.0,
                "rheostat_ratio": 0.5,
            },
        )

        self.assertAlmostEqual(result["meter_results"]["ammeter"], 0.3, places=3)
        self.assertAlmostEqual(result["meter_results"]["voltmeter"], 3.0, places=3)
        self.assertTrue(result["visual_state"]["energized"])
        self.assertEqual(result["component_states"]["switch"]["state"], "closed")

    def test_figure1_simulation_returns_zero_meters_when_open(self):
        build_figure1_scene = load_attr(
            "backend.app.scenes.figure1", "build_figure1_scene"
        )
        simulate_scene = load_attr(
            "backend.app.scenes.figure1", "simulate_figure1_scene"
        )

        scene = build_figure1_scene()
        result = simulate_scene(
            scene["scene"],
            {
                "switch_closed": False,
                "battery_voltage": 6.0,
                "resistor_value": 10.0,
                "rheostat_total": 20.0,
                "rheostat_ratio": 0.5,
            },
        )

        self.assertAlmostEqual(result["meter_results"]["ammeter"], 0.0, places=6)
        self.assertAlmostEqual(result["meter_results"]["voltmeter"], 0.0, places=6)
        self.assertFalse(result["visual_state"]["energized"])

    def test_figure1_simulation_decreases_current_as_slider_increases(self):
        build_figure1_scene = load_attr(
            "backend.app.scenes.figure1", "build_figure1_scene"
        )
        simulate_scene = load_attr(
            "backend.app.scenes.figure1", "simulate_figure1_scene"
        )

        scene = build_figure1_scene()
        low = simulate_scene(
            scene["scene"],
            {
                "switch_closed": True,
                "battery_voltage": 6.0,
                "resistor_value": 10.0,
                "rheostat_total": 20.0,
                "rheostat_ratio": 0.2,
            },
        )
        high = simulate_scene(
            scene["scene"],
            {
                "switch_closed": True,
                "battery_voltage": 6.0,
                "resistor_value": 10.0,
                "rheostat_total": 20.0,
                "rheostat_ratio": 0.8,
            },
        )

        self.assertGreater(low["meter_results"]["ammeter"], high["meter_results"]["ammeter"])
        self.assertGreater(
            low["meter_results"]["voltmeter"], high["meter_results"]["voltmeter"]
        )

    def test_scene_edit_supports_remove_and_restore(self):
        build_figure1_scene = load_attr(
            "backend.app.scenes.figure1", "build_figure1_scene"
        )
        apply_scene_edit = load_attr(
            "backend.app.scenes.figure1", "apply_figure1_edit"
        )

        scene = build_figure1_scene()["scene"]
        removed = apply_scene_edit(scene, {"action": "remove_component", "component_id": "voltmeter"})
        self.assertFalse(
            next(
                component for component in removed["components"] if component["id"] == "voltmeter"
            )["enabled"]
        )

        restored = apply_scene_edit(
            removed, {"action": "restore_component", "component_id": "voltmeter"}
        )
        self.assertTrue(
            next(
                component for component in restored["components"] if component["id"] == "voltmeter"
            )["enabled"]
        )

    def test_figure1_scene_api_returns_scene_and_simulation(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        response = client.get("/api/scenes/figure-1")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["scene"]["id"], "figure-1")
        self.assertIn("meter_results", payload["simulation"])

    def test_figure1_simulate_api_updates_meter_values(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        initial = client.get("/api/scenes/figure-1").json()
        response = client.post(
            "/api/scenes/figure-1/simulate",
            json={
                "scene": initial["scene"],
                "state": {
                    "switch_closed": True,
                    "battery_voltage": 6.0,
                    "resistor_value": 10.0,
                    "rheostat_total": 20.0,
                    "rheostat_ratio": 0.25,
                },
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertGreater(response.json()["meter_results"]["ammeter"], 0.0)

    def test_figure1_edit_api_rejects_unknown_component(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        initial = client.get("/api/scenes/figure-1").json()
        response = client.post(
            "/api/scenes/figure-1/edit",
            json={
                "scene": initial["scene"],
                "state": initial["state"],
                "edit": {"action": "remove_component", "component_id": "missing"},
            },
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
