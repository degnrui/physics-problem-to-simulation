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


MECHANICS_PROBLEM_TEXT = (
    "17. 某兴趣小组设计了一个传送装置，AB是倾角为30°的斜轨道，BC是以恒定速率v0顺时针转动的水平传送带，"
    "靠近C端有半径为R、质量为M置于光滑水平面上的可动半圆弧轨道。现有一质量为m的物块，从AB上距B点L的P点由静止下滑，"
    "经传送带末端C点滑入圆弧轨道。物块与传送带间的动摩擦因数为μ，其余接触面均光滑。"
    "已知R=0.36m，L=1.6m，v0=5m/s，m=0.2kg，M=1.8kg，μ=0.25。求物块滑到B点处的速度大小、"
    "从B运动到C过程中摩擦力对其做的功、在传送带上滑动过程中产生的滑痕长度、即将离开圆弧轨道最高点的瞬间受到轨道的压力大小。"
)

MECHANICS_SOLUTION_TEXT = (
    "滑块由P点到B点由动能定理得 mgsin30°L = 1/2 mv^2，解得 v=4m/s。"
    "物块滑上传送带后做匀加速运动直至与传送带共速，摩擦力对其做功 Wf = 1/2 mv0^2 - 1/2 mv^2 = 0.9J。"
    "加速度为 a=μg=2.5m/s^2，加速时间 t=(v0-v)/a=0.4s，滑痕长度 Δx=v0 t - (v0+v)t/2 = 0.2m。"
    "物块开始进入圆弧轨道到到达即将最高点由水平方向动量守恒和机械能守恒可知，1/2 mv0^2 = 1/2 mv1^2 + 1/2 Mv2^2 + 2mgR，"
    "解得 v1=0.8m/s。对滑块在最高点由牛顿第二定律得 F+mg = m(v1-v2)^2/R，解得 F=3N。"
)

MECHANICS_FINAL_ANSWERS = "4m/s;0.9J;0.2m;3N"


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

    def test_import_scene_json_api_accepts_scene_bundle(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        scene = {
            "id": "imported-demo",
            "title": "Imported",
            "canvas": {"width": 500, "height": 300},
            "components": [
                {
                    "id": "bat1",
                    "type": "battery",
                    "x": 80,
                    "y": 220,
                    "width": 80,
                    "height": 40,
                    "ports": [
                        {"id": "left", "x": 80, "y": 240},
                        {"id": "right", "x": 160, "y": 240},
                    ],
                },
                {
                    "id": "sw1",
                    "type": "switch",
                    "x": 180,
                    "y": 90,
                    "width": 80,
                    "height": 130,
                    "ports": [
                        {"id": "top", "x": 220, "y": 100},
                        {"id": "bottom", "x": 220, "y": 240},
                    ],
                },
                {
                    "id": "r1",
                    "type": "resistor",
                    "x": 280,
                    "y": 90,
                    "width": 80,
                    "height": 30,
                    "ports": [
                        {"id": "a", "x": 280, "y": 105},
                        {"id": "b", "x": 360, "y": 105},
                    ],
                    "value": 10.0,
                },
                {"id": "n1", "type": "junction", "x": 220, "y": 100, "width": 10, "height": 10},
                {"id": "n2", "type": "junction", "x": 360, "y": 105, "width": 10, "height": 10},
                {"id": "n0", "type": "junction", "x": 220, "y": 240, "width": 10, "height": 10},
            ],
            "wires": [
                {"id": "w1", "start_ref": "sw1.top", "end_ref": "r1.a", "role": "main"},
                {"id": "w2", "start_ref": "r1.b", "end_ref": "n2", "role": "main"},
                {"id": "w3", "start_ref": "bat1.right", "end_ref": "n1", "role": "main"},
                {"id": "w4", "start_ref": "bat1.left", "end_ref": "n0", "role": "main"},
                {"id": "w5", "start_ref": "sw1.bottom", "end_ref": "n0", "role": "main"},
            ],
            "meter_anchors": [],
            "circuit_topology": {
                "node_ids": ["n1", "n2", "n0"],
                "connections": [
                    {"component_id": "bat1", "terminal": "positive", "node_id": "n1"},
                    {"component_id": "bat1", "terminal": "negative", "node_id": "n0"},
                    {"component_id": "sw1", "terminal": "a", "node_id": "n1"},
                    {"component_id": "sw1", "terminal": "b", "node_id": "n2"},
                    {"component_id": "r1", "terminal": "a", "node_id": "n2"},
                    {"component_id": "r1", "terminal": "b", "node_id": "n0"},
                ],
            },
        }
        response = client.post(
            "/api/scenes/import-json",
            json={"scene": scene, "state": {"switch_closed": True, "battery_voltage": 6.0}},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["scene"]["id"], "imported-demo")
        self.assertIn("simulation", payload)

    def test_import_scene_json_defaults_to_open_switch_and_black_wires(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        scene = {
            "id": "imported-open-default",
            "title": "Imported Open Default",
            "canvas": {"width": 320, "height": 220},
            "components": [
                {
                    "id": "battery_1",
                    "type": "battery",
                    "x": 40,
                    "y": 180,
                    "width": 40,
                    "height": 20,
                    "ports": [{"id": "left", "x": 40, "y": 190}, {"id": "right", "x": 80, "y": 190}],
                },
                {
                    "id": "switch_1",
                    "type": "switch",
                    "x": 240,
                    "y": 20,
                    "width": 40,
                    "height": 40,
                    "ports": [{"id": "top", "x": 260, "y": 30}, {"id": "bottom", "x": 260, "y": 70}],
                },
                {
                    "id": "r1",
                    "type": "resistor",
                    "x": 120,
                    "y": 20,
                    "width": 50,
                    "height": 20,
                    "value": 10.0,
                    "ports": [{"id": "a", "x": 120, "y": 30}, {"id": "b", "x": 170, "y": 30}],
                },
                {"id": "n0", "type": "junction", "x": 40, "y": 30, "width": 10, "height": 10},
                {"id": "n1", "type": "junction", "x": 170, "y": 30, "width": 10, "height": 10},
                {"id": "n2", "type": "junction", "x": 260, "y": 30, "width": 10, "height": 10},
                {"id": "n3", "type": "junction", "x": 260, "y": 190, "width": 10, "height": 10},
            ],
            "wires": [{"id": "w", "role": "main", "start_ref": "n0", "end_ref": "n2"}],
            "meter_anchors": [],
            "circuit_topology": {
                "node_ids": ["n0", "n1", "n2", "n3"],
                "connections": [
                    {"component_id": "battery_1", "terminal": "negative", "node_id": "n0"},
                    {"component_id": "battery_1", "terminal": "positive", "node_id": "n3"},
                    {"component_id": "switch_1", "terminal": "a", "node_id": "n3"},
                    {"component_id": "switch_1", "terminal": "b", "node_id": "n2"},
                    {"component_id": "r1", "terminal": "a", "node_id": "n2"},
                    {"component_id": "r1", "terminal": "b", "node_id": "n0"},
                ],
            },
        }
        response = client.post("/api/scenes/import-json", json={"scene": scene})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertFalse(payload["state"]["switch_closed"])
        self.assertFalse(payload["simulation"]["visual_state"]["energized"])
        self.assertEqual(payload["simulation"]["visual_state"]["highlighted_wires"], [])

    def test_figure1_scene_geometry_has_no_open_wire_endpoints(self):
        build_figure1_scene = load_attr(
            "backend.app.scenes.figure1", "build_figure1_scene"
        )
        validate_geometry = load_attr(
            "backend.app.scenes.figure1", "validate_figure1_geometry"
        )

        payload = build_figure1_scene()
        issues = validate_geometry(payload["scene"])

        self.assertEqual(issues, [])

    def test_recognize_clean_circuit_image_returns_scene_and_simulation(self):
        import cv2
        import numpy as np

        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        image = np.full((900, 1200, 3), 255, dtype=np.uint8)
        stroke = (15, 23, 42)

        cv2.line(image, (180, 260), (620, 260), stroke, 10)
        cv2.line(image, (915, 260), (1070, 260), stroke, 10)
        cv2.line(image, (1070, 260), (1070, 780), stroke, 10)
        cv2.line(image, (1070, 780), (870, 780), stroke, 10)
        cv2.line(image, (565, 780), (390, 780), stroke, 10)
        cv2.line(image, (190, 780), (100, 780), stroke, 10)
        cv2.line(image, (100, 780), (100, 430), stroke, 10)

        cv2.circle(image, (100, 430), 22, stroke, 10)
        cv2.line(image, (98, 408), (28, 602), stroke, 10)
        cv2.line(image, (100, 455), (100, 344), stroke, 10)

        cv2.line(image, (205, 720), (205, 835), stroke, 10)
        cv2.line(image, (245, 690), (245, 855), stroke, 10)

        cv2.rectangle(image, (620, 225), (825, 330), stroke, 10)
        cv2.rectangle(image, (565, 740), (870, 835), stroke, 10)
        cv2.line(image, (720, 610), (720, 740), stroke, 10)
        cv2.line(image, (720, 740), (690, 675), stroke, 10)
        cv2.circle(image, (720, 650), 24, (255, 128, 0), -1)
        cv2.circle(image, (720, 650), 24, stroke, 8)

        cv2.line(image, (560, 260), (560, 105), stroke, 10)
        cv2.line(image, (560, 105), (680, 105), stroke, 10)
        cv2.line(image, (855, 105), (915, 105), stroke, 10)
        cv2.line(image, (915, 105), (915, 260), stroke, 10)
        cv2.circle(image, (767, 105), 88, stroke, 10)

        cv2.circle(image, (1070, 615), 78, stroke, 10)

        success, encoded = cv2.imencode(".png", image)
        self.assertTrue(success)

        client = TestClient(create_app())
        response = client.post(
            "/api/recognize",
            files={"file": ("clean-circuit.png", encoded.tobytes(), "image/png")},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["scene"]["id"], "recognized-clean-circuit")
        self.assertIn("simulation", payload)
        self.assertIn("detections", payload)
        self.assertIn("session_id", payload)
        self.assertIn("confidence_breakdown", payload)
        self.assertGreater(payload["simulation"]["meter_results"]["ammeter"], 0.0)

    def test_recognition_confirm_endpoint_applies_component_update(self):
        import cv2
        import numpy as np

        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        image = np.full((520, 860, 3), 255, dtype=np.uint8)
        stroke = (15, 23, 42)
        cv2.line(image, (100, 120), (760, 120), stroke, 8)
        cv2.line(image, (760, 120), (760, 400), stroke, 8)
        cv2.line(image, (760, 400), (100, 400), stroke, 8)
        cv2.line(image, (100, 400), (100, 120), stroke, 8)
        cv2.rectangle(image, (280, 95), (420, 150), stroke, 8)
        cv2.circle(image, (620, 120), 42, stroke, 8)
        cv2.line(image, (200, 360), (200, 450), stroke, 8)
        cv2.line(image, (230, 345), (230, 465), stroke, 8)
        success, encoded = cv2.imencode(".png", image)
        self.assertTrue(success)

        client = TestClient(create_app())
        recognize = client.post(
            "/api/recognize",
            files={"file": ("confirm.png", encoded.tobytes(), "image/png")},
        )
        self.assertEqual(recognize.status_code, 200)
        session = recognize.json()
        components = [
            component
            for component in session["scene"]["components"]
            if component["type"] != "junction"
        ]
        self.assertGreater(len(components), 0)

        response = client.post(
            f"/api/recognize/{session['session_id']}/confirm",
            json={
                "updates": {
                    "component_updates": [
                        {"id": components[0]["id"], "type": "resistor", "value": 22.0}
                    ],
                    "state_updates": [{"key": "switch_closed", "value": True}],
                }
            },
        )

        self.assertEqual(response.status_code, 200)
        confirmed = response.json()
        updated_component = next(
            item
            for item in confirmed["scene"]["components"]
            if item["id"] == components[0]["id"]
        )
        self.assertEqual(updated_component["type"], "resistor")
        self.assertAlmostEqual(updated_component["value"], 22.0, places=3)



    def test_mechanics_recognize_endpoint_returns_selected_model_for_consistent_solution(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        response = client.post(
            "/api/mechanics/recognize",
            data={
                "problem_text": MECHANICS_PROBLEM_TEXT,
                "solution_text": MECHANICS_SOLUTION_TEXT,
                "final_answers": MECHANICS_FINAL_ANSWERS,
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("problem_representation", payload)
        self.assertIn("candidate_models", payload)
        self.assertIn("selected_model", payload)
        self.assertIn("solution_model", payload)
        self.assertIn("simulation", payload)
        self.assertFalse(payload["needs_confirmation"])
        self.assertEqual(payload["selected_model"]["id"], "belt_arc_consistent")
        self.assertEqual(payload["simulation"]["answers"]["q1"]["display_value"], "4 m/s")
        self.assertEqual(payload["simulation"]["answers"]["q2"]["display_value"], "0.9 J")
        self.assertEqual(payload["simulation"]["answers"]["q3"]["display_value"], "0.2 m")
        self.assertEqual(payload["simulation"]["answers"]["q4"]["display_value"], "3 N")

    def test_mechanics_recognize_endpoint_flags_conflicts_for_mismatched_solution(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        response = client.post(
            "/api/mechanics/recognize",
            data={
                "problem_text": "斜面、传送带和半圆轨道综合题，已知R=0.36m，L=1.6m，v0=5m/s，m=0.2kg，M=1.8kg，μ=0.25。",
                "solution_text": "滑到B点速度是5m/s，摩擦做功0.4J，滑痕0.1m，压力1N。",
                "final_answers": "5m/s;0.4J;0.1m;1N",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["needs_confirmation"])
        self.assertGreaterEqual(len(payload["conflict_items"]), 1)
        self.assertTrue(any(item["kind"] == "answer_mismatch" for item in payload["conflict_items"]))

    def test_mechanics_recognize_endpoint_degrades_without_solution_text(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        response = client.post(
            "/api/mechanics/recognize",
            data={
                "problem_text": "斜面、传送带和半圆轨道综合题，已知R=0.36m，L=1.6m，v0=5m/s，m=0.2kg，M=1.8kg，μ=0.25。",
                "final_answers": "4m/s;0.9J;0.2m;3N",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["needs_confirmation"])
        self.assertLess(payload["confidence_breakdown"]["overall"], 0.9)
        self.assertEqual(payload["simulation"]["answers"]["q4"]["display_value"], "3 N")

    def test_mechanics_confirm_endpoint_accepts_candidate_override(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        session = client.post(
            "/api/mechanics/recognize",
            data={
                "problem_text": "斜面、传送带和半圆轨道综合题，已知R=0.36m，L=1.6m，v0=5m/s，m=0.2kg，M=1.8kg，μ=0.25。",
                "solution_text": "滑到B点速度是5m/s，摩擦做功0.4J，滑痕0.1m，压力1N。",
                "final_answers": "5m/s;0.4J;0.1m;1N",
            },
        ).json()

        response = client.post(
            f"/api/mechanics/{session['session_id']}/confirm",
            json={
                "updates": {
                    "selected_model_id": "belt_arc_consistent",
                    "assumption_overrides": {"belt_reaches_speed": True},
                }
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["selected_model"]["id"], "belt_arc_consistent")
        self.assertFalse(payload["needs_confirmation"])
        self.assertEqual(payload["simulation"]["answers"]["q1"]["display_value"], "4 m/s")

    def test_mechanics_harness_packet_declares_dev_proxy_execution(self):
        normalize_mechanics_inputs = load_attr(
            "backend.app.mechanics.parsing.normalize", "normalize_mechanics_inputs"
        )
        build_mechanics_harness_packet = load_attr(
            "backend.app.mechanics.harness", "build_mechanics_harness_packet"
        )

        normalized = normalize_mechanics_inputs(
            problem_text="斜面、传送带和半圆轨道综合题，已知R=0.36m，L=1.6m，v0=5m/s，m=0.2kg，M=1.8kg，μ=0.25。",
            solution_text="由动能定理得v=4m/s。",
            final_answers="4m/s;0.9J;0.2m;3N",
        )
        harness = build_mechanics_harness_packet(normalized)

        self.assertEqual(harness["mode"], "agent_harness")
        self.assertEqual(harness["executor"], "dev_proxy")
        self.assertIn("selected_model", harness["required_outputs"])
        self.assertTrue(any("不要把参考答案硬拟合" in item for item in harness["guardrails"]))

    def test_mechanics_recognize_response_includes_executor_artifacts(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        response = client.post(
            "/api/mechanics/recognize",
            data={
                "problem_text": "斜面、传送带和半圆轨道综合题，已知R=0.36m，L=1.6m，v0=5m/s，m=0.2kg，M=1.8kg，μ=0.25。",
                "solution_text": "由动能定理得v=4m/s，摩擦做功0.9J，滑痕0.2m，压力3N。",
                "final_answers": "4m/s;0.9J;0.2m;3N",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["execution_mode"], "dev_proxy")
        self.assertIn("executor_run", payload)
        self.assertIn("tool_trace", payload["executor_run"])
        self.assertGreaterEqual(len(payload["executor_run"]["tool_trace"]), 4)
        self.assertIn("verification_report", payload)
        self.assertIn("final_simulation_spec", payload)
        self.assertEqual(
            payload["final_simulation_spec"]["answers"]["q4"]["display_value"], "3 N"
        )

    def test_mechanics_dev_proxy_executor_runs_declared_tools(self):
        normalize_mechanics_inputs = load_attr(
            "backend.app.mechanics.parsing.normalize", "normalize_mechanics_inputs"
        )
        build_mechanics_harness_packet = load_attr(
            "backend.app.mechanics.harness", "build_mechanics_harness_packet"
        )
        run_dev_proxy_executor = load_attr(
            "backend.app.mechanics.executor.dev_proxy", "run_dev_proxy_executor"
        )

        normalized = normalize_mechanics_inputs(
            problem_text="斜面、传送带和半圆轨道综合题，已知R=0.36m，L=1.6m，v0=5m/s，m=0.2kg，M=1.8kg，μ=0.25。",
            solution_text="由动能定理得v=4m/s，摩擦做功0.9J，滑痕0.2m，压力3N。",
            final_answers="4m/s;0.9J;0.2m;3N",
        )
        harness = build_mechanics_harness_packet(normalized)
        result = run_dev_proxy_executor(harness, preferred_model_id=None)

        tool_names = [item["tool"] for item in result["tool_trace"]]
        self.assertEqual(tool_names[:4], [
            "extract_problem_representation",
            "build_candidate_models",
            "extract_solution_model",
            "simulate_candidate_models",
        ])
        self.assertIn("verification_report", result)
        self.assertEqual(result["selected_model"]["id"], "belt_arc_consistent")

    def test_mechanics_generate_scene_endpoint_returns_teaching_scene(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        session = client.post(
            "/api/mechanics/recognize",
            data={
                "problem_text": MECHANICS_PROBLEM_TEXT,
                "solution_text": MECHANICS_SOLUTION_TEXT,
                "final_answers": MECHANICS_FINAL_ANSWERS,
            },
        ).json()

        response = client.post(f"/api/mechanics/{session['session_id']}/generate-scene")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["scene"]["scene_id"], f"mechanics-{session['session_id']}")
        self.assertEqual(len(payload["scene"]["stages"]), 4)
        self.assertEqual(payload["scene"]["stages"][0]["id"], "slope")
        self.assertTrue(any(actor["id"] == "block" for actor in payload["scene"]["actors"]))
        self.assertTrue(any(panel["stage_id"] == "arc_top" for panel in payload["scene"]["lesson_panels"]))

    def test_mechanics_simulate_endpoint_returns_runtime_frame(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        session = client.post(
            "/api/mechanics/recognize",
            data={
                "problem_text": MECHANICS_PROBLEM_TEXT,
                "solution_text": MECHANICS_SOLUTION_TEXT,
                "final_answers": MECHANICS_FINAL_ANSWERS,
            },
        ).json()
        scene_payload = client.post(
            f"/api/mechanics/{session['session_id']}/generate-scene"
        ).json()

        response = client.post(
            f"/api/mechanics/{session['session_id']}/simulate",
            json={"stage_id": "belt", "progress": 0.5},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["stage"]["id"], "belt")
        self.assertIn("block", payload["frame"]["actors"])
        self.assertIn("belt_speed", payload["frame"]["overlays"])
        self.assertEqual(payload["frame"]["annotations"][0]["key"], "q2")
        self.assertEqual(payload["scene"]["scene_id"], scene_payload["scene"]["scene_id"])

    def test_mechanics_run_executor_supports_api_model_stub_contract(self):
        normalize_mechanics_inputs = load_attr(
            "backend.app.mechanics.parsing.normalize", "normalize_mechanics_inputs"
        )
        build_mechanics_harness_packet = load_attr(
            "backend.app.mechanics.harness", "build_mechanics_harness_packet"
        )
        run_executor = load_attr("backend.app.mechanics.executor", "run_executor")

        normalized = normalize_mechanics_inputs(
            problem_text=MECHANICS_PROBLEM_TEXT,
            solution_text=MECHANICS_SOLUTION_TEXT,
            final_answers=MECHANICS_FINAL_ANSWERS,
        )
        harness = build_mechanics_harness_packet(normalized)
        result = run_executor(harness, {"mode": "api_model"})

        self.assertEqual(result["executor"], "api_model")
        self.assertIn("runtime_warnings", result)
        self.assertGreaterEqual(len(result["runtime_warnings"]), 1)
        self.assertEqual(result["selected_model"]["id"], "belt_arc_consistent")

    def test_recognition_confirm_endpoint_rejects_unknown_session(self):
        create_app = load_attr("backend.app.main", "create_app")
        TestClient = load_attr("fastapi.testclient", "TestClient")

        client = TestClient(create_app())
        response = client.post(
            "/api/recognize/missing-session/confirm",
            json={"updates": {}},
        )

        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
