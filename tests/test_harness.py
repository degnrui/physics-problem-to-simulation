import json
import os
import socket
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.config import settings
from app.main import app
from app.domain.problem import ProblemInput
from app.harness.model_executor import (
    ModelExecutionTimeoutError,
    ModelExecutor,
    REQUEST_TIMEOUT_SECONDS,
)
from app.harness.orchestrator import (
    plan_problem_to_simulation,
    run_problem_to_simulation_harness,
)


CAT_STAGE_PROBLEM = (
    "小猫从地面蹬地后跃起，在空中追逐前方飞行的蝴蝶。"
    "请分别分析小猫蹬地阶段和腾空阶段的受力情况，并判断在腾空后哪些力仍然存在。"
)

MODELING_PROBLEM = (
    "围绕跳水、空中转体、百米冲刺和攀岩四类运动情境，判断在什么研究目标下可以把运动员近似看成质点，并说明原因。"
)

PROJECTILE_PROBLEM = (
    "如图所示，在水平桌面上放置一斜面，在桌边水平放置一块高度可调的木板。"
    "让钢球从斜面上同一位置静止滚下，越过桌边后做平抛运动。"
    "当木板离桌面的竖直距离为h时，钢球在木板上的落点离桌边的水平距离为x。"
)

ELASTIC_PROBLEM = (
    "如图所示，两根相同的橡皮绳，一端连接质量为m的物块，另一端固定在水平桌面上的A、B两点。"
    "物块处于AB连线的中点C时，橡皮绳为原长。现将物块沿AB中垂线水平拉至桌面上的O点静止释放。"
    "已知CO距离为L，物块与桌面间的动摩擦因数为μ，橡皮绳始终处于弹性限度内，不计空气阻力。"
)

GENERIC_TRANSITION_PROBLEM = (
    "篮球离开手后在空中飞向篮板，碰到篮板后反弹。"
    "请比较篮球在飞行阶段和碰板阶段的受力情况，并说明哪些力发生了变化。"
)


class HarnessOrchestratorTests(unittest.TestCase):
    def test_plan_builds_simulation_route_for_staged_force_problem(self) -> None:
        result = plan_problem_to_simulation(
            ProblemInput(text=CAT_STAGE_PROBLEM, topic_hint="force-analysis")
        )

        self.assertTrue(result["planner"]["simulation_ready"])
        self.assertEqual(result["planner"]["stage_type"], "cat-jump")
        self.assertEqual(result["task_plan"]["tasks"][0]["type"], "problem_profile")
        self.assertEqual(result["task_plan"]["tasks"][-1]["type"], "teaching_simulation_package")

    def test_plan_builds_simulation_route_for_generic_contact_transition_problem(self) -> None:
        result = plan_problem_to_simulation(
            ProblemInput(text=GENERIC_TRANSITION_PROBLEM, topic_hint="force-analysis")
        )

        self.assertTrue(result["planner"]["simulation_ready"])
        self.assertEqual(result["planner"]["problem_family"], "force-analysis")
        self.assertEqual(result["planner"]["stage_type"], "contact-impact")

    def test_plan_builds_analysis_only_route_for_modeling_problem(self) -> None:
        result = plan_problem_to_simulation(
            ProblemInput(text=MODELING_PROBLEM, topic_hint="force-analysis")
        )

        self.assertFalse(result["planner"]["simulation_ready"])
        self.assertEqual(result["planner"]["stage_type"], "modeling-judgement")
        self.assertEqual(result["task_plan"]["tasks"][-1]["type"], "teaching_analysis_package")

    def test_run_writes_artifacts_and_final_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_problem_to_simulation_harness(
                ProblemInput(text=CAT_STAGE_PROBLEM, topic_hint="force-analysis"),
                runs_root=Path(temp_dir),
            )

            run_dir = Path(temp_dir) / result["run_id"]
            self.assertTrue((run_dir / "task_plan.json").exists())
            self.assertTrue((run_dir / "task_log.ndjson").exists())
            self.assertTrue((run_dir / "artifacts" / "problem_profile.json").exists())
            self.assertTrue((run_dir / "artifacts" / "physics_model.json").exists())
            self.assertTrue((run_dir / "artifacts" / "teaching_plan.json").exists())
            self.assertTrue((run_dir / "artifacts" / "scene_spec.json").exists())
            self.assertTrue((run_dir / "artifacts" / "simulation_spec.json").exists())
            self.assertTrue((run_dir / "artifacts" / "simulation_blueprint.json").exists())
            self.assertTrue((run_dir / "artifacts" / "renderer_payload.json").exists())
            self.assertTrue((run_dir / "artifacts" / "delivery_bundle.json").exists())
            self.assertTrue((run_dir / "artifacts" / "validation_report.json").exists())
            self.assertTrue((run_dir / "final_package.json").exists())
            self.assertEqual(result["validation_report"]["route"], "simulation")
            self.assertGreaterEqual(len(result["task_log"]), 9)

            final_package = json.loads((run_dir / "final_package.json").read_text(encoding="utf-8"))
            self.assertEqual(final_package["problem_profile"]["research_object"], "小猫")
            self.assertIn("simulation_blueprint", final_package)
            self.assertIn("renderer_payload", final_package)
            self.assertIn("delivery_bundle", final_package)
            self.assertTrue((run_dir / "status.json").exists())

    def test_run_builds_staged_force_scene_for_generic_contact_transition_problem(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_problem_to_simulation_harness(
                ProblemInput(text=GENERIC_TRANSITION_PROBLEM, topic_hint="force-analysis"),
                runs_root=Path(temp_dir),
            )

            self.assertEqual(result["planner"]["stage_type"], "contact-impact")
            self.assertEqual(result["scene_spec"]["template_id"], "force-analysis-staged-v1")
            parameters = result["scene_spec"]["parameters"]
            stage_options = parameters["stage_options"]
            self.assertEqual(len(stage_options), 2)
            self.assertEqual(stage_options[0]["label"], "飞行阶段")
            self.assertEqual(stage_options[1]["label"], "接触阶段")

    def test_plan_routes_projectile_problem_to_projectile_motion_family(self) -> None:
        result = plan_problem_to_simulation(
            ProblemInput(text=PROJECTILE_PROBLEM, topic_hint="high-school-physics")
        )

        self.assertEqual(result["planner"]["problem_family"], "projectile-motion")
        self.assertEqual(result["planner"]["model_family"], "projectile-motion")
        self.assertEqual(result["planner"]["simulation_mode"], "trajectory-lab")

    def test_plan_routes_elastic_problem_to_symmetric_elastic_motion_family(self) -> None:
        result = plan_problem_to_simulation(
            ProblemInput(text=ELASTIC_PROBLEM, topic_hint="high-school-physics")
        )

        self.assertEqual(result["planner"]["problem_family"], "elastic-motion")
        self.assertEqual(result["planner"]["model_family"], "symmetric-elastic-motion")
        self.assertEqual(result["planner"]["simulation_mode"], "restoring-force-lab")

    def test_run_builds_elastic_motion_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_problem_to_simulation_harness(
                ProblemInput(text=ELASTIC_PROBLEM, topic_hint="high-school-physics"),
                runs_root=Path(temp_dir),
            )

            self.assertEqual(result["planner"]["model_family"], "symmetric-elastic-motion")
            self.assertEqual(result["problem_profile"]["research_object"], "物块")
            self.assertEqual(result["scene_spec"]["template_id"], "elastic-restoring-motion-v1")
            self.assertEqual(result["simulation_spec"]["renderer_mode"], "parameterized-motion-preview")
            self.assertEqual(result["simulation_blueprint"]["delivery_mode"], "interactive-teaching-demo")
            self.assertEqual(result["renderer_payload"]["component_key"], "elastic-restoring-motion")
            self.assertEqual(result["delivery_bundle"]["primary_view"], "simulation-viewport")
            self.assertEqual(result["validation_report"]["route"], "simulation")

    def test_task_plan_includes_post_package_simulation_tasks(self) -> None:
        result = plan_problem_to_simulation(
            ProblemInput(text=ELASTIC_PROBLEM, topic_hint="high-school-physics")
        )

        task_types = [task["type"] for task in result["task_plan"]["tasks"]]
        self.assertIn("simulation_blueprint", task_types)
        self.assertIn("renderer_payload", task_types)
        self.assertIn("delivery_bundle", task_types)

    def test_elastic_package_meets_simulation_lab_quality_bar(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_problem_to_simulation_harness(
                ProblemInput(text=ELASTIC_PROBLEM, topic_hint="high-school-physics"),
                runs_root=Path(temp_dir),
            )

            blueprint = result["simulation_blueprint"]
            delivery_bundle = result["delivery_bundle"]
            renderer_payload = result["renderer_payload"]

            self.assertEqual(blueprint["delivery_mode"], "interactive-teaching-demo")
            self.assertTrue(blueprint["minimum_quality_bar"]["interactive_controls"])
            self.assertTrue(blueprint["minimum_quality_bar"]["time_playback"])
            self.assertTrue(blueprint["minimum_quality_bar"]["linked_charts"])
            self.assertTrue(blueprint["minimum_quality_bar"]["teacher_guidance"])
            self.assertTrue(blueprint["minimum_quality_bar"]["option_diagnosis"])
            self.assertIn("linked charts", blueprint["render_priority"])
            self.assertIn("playback and seek controls", blueprint["render_priority"])

            self.assertEqual(renderer_payload["layout_mode"], "simulation-lab")

            self.assertIn("linked-charts", delivery_bundle["secondary_views"])
            self.assertIn("playback-panel", delivery_bundle["secondary_views"])
            self.assertIn("teacher-guidance", delivery_bundle["secondary_views"])
            self.assertIn("option-diagnosis", delivery_bundle["secondary_views"])
            self.assertIn("parameter-controls", delivery_bundle["secondary_views"])

            required_panels = {
                "simulation_canvas",
                "linked_charts",
                "parameter_controls",
                "playback_panel",
                "teacher_guidance",
                "option_diagnosis",
            }
            self.assertTrue(required_panels.issubset(set(delivery_bundle["panel_contract"].keys())))

    def test_renderer_payload_carries_frontend_design_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_problem_to_simulation_harness(
                ProblemInput(text=ELASTIC_PROBLEM, topic_hint="high-school-physics"),
                runs_root=Path(temp_dir),
            )

            renderer_payload = result["renderer_payload"]
            delivery_bundle = result["delivery_bundle"]

            self.assertEqual(renderer_payload["layout_mode"], "simulation-lab")
            self.assertEqual(renderer_payload["design_system"]["theme_key"], "impeccable-lab")
            self.assertEqual(renderer_payload["design_system"]["density"], "comfortable")
            self.assertIn("workspace", renderer_payload["composition"])
            self.assertIn("simulation", renderer_payload["composition"])
            self.assertIn("inspector", renderer_payload["composition"])

            inspector = delivery_bundle["inspector_contract"]
            self.assertIn("summary", inspector)
            self.assertIn("artifacts", inspector)
            self.assertIn("validation", inspector)
            self.assertIn("problem_profile", inspector["artifacts"])
            self.assertIn("physics_model", inspector["artifacts"])
            self.assertIn("teaching_plan", inspector["artifacts"])
            self.assertEqual(delivery_bundle["artifact_tabs"][0]["id"], "summary")
            self.assertIn("simulation_canvas", delivery_bundle["default_open_panels"])
            self.assertIn("teacher_guidance", delivery_bundle["default_open_panels"])
            self.assertTrue(delivery_bundle["exportable"])
            self.assertEqual(delivery_bundle["export_mode"], "single-file-html")
            self.assertIn("renderer_payload", delivery_bundle["export_includes"])
            self.assertTrue(result["validation_report"]["export_ready"])
            self.assertIn("generation_trace", result["validation_report"])


class HarnessApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        app.state.runs_root = Path(self.temp_dir.name)
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _wait_for_terminal_status(self, run_id: str, timeout: float = 5.0) -> dict:
        deadline = time.time() + timeout
        while time.time() < deadline:
            response = self.client.get(f"/api/problem-to-simulation/runs/{run_id}")
            payload = response.json()
            if payload["status"] in {"completed", "failed"}:
                return payload
            time.sleep(0.05)
        self.fail(f"Run {run_id} did not reach terminal status before timeout")

    def test_create_run_returns_run_status_and_persists_status_snapshot(self) -> None:
        response = self.client.post(
            "/api/problem-to-simulation/runs",
            json={"text": ELASTIC_PROBLEM, "topic_hint": "high-school-physics"},
        )

        self.assertEqual(response.status_code, 202)
        payload = response.json()
        self.assertIn("run_id", payload)
        self.assertIn(payload["status"], {"queued", "planning"})
        self.assertEqual(payload["route"], f"/simulation/{payload['run_id']}")

        run_dir = Path(self.temp_dir.name) / payload["run_id"]
        self.assertTrue((run_dir / "status.json").exists())

    def test_list_runs_returns_recent_run_metadata(self) -> None:
        first = self.client.post(
            "/api/problem-to-simulation/runs",
            json={"text": CAT_STAGE_PROBLEM, "topic_hint": "force-analysis", "mode": "rule-based"},
        ).json()
        second = self.client.post(
            "/api/problem-to-simulation/runs",
            json={"text": ELASTIC_PROBLEM, "topic_hint": "high-school-physics", "mode": "rule-based"},
        ).json()
        self._wait_for_terminal_status(first["run_id"])
        self._wait_for_terminal_status(second["run_id"])

        response = self.client.get("/api/problem-to-simulation/runs")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertGreaterEqual(len(payload["items"]), 2)
        latest = payload["items"][0]
        self.assertEqual(latest["run_id"], second["run_id"])
        self.assertIn("title", latest)
        self.assertEqual(latest["status"], "completed")
        self.assertEqual(latest["model_family"], "symmetric-elastic-motion")
        self.assertEqual(latest["simulation_mode"], "restoring-force-lab")
        self.assertTrue(latest["export_ready"])

    def test_run_status_endpoint_returns_aggregated_progress(self) -> None:
        create = self.client.post(
            "/api/problem-to-simulation/runs",
            json={"text": ELASTIC_PROBLEM, "topic_hint": "high-school-physics"},
        ).json()

        payload = self._wait_for_terminal_status(create["run_id"])

        self.assertEqual(payload["run_id"], create["run_id"])
        self.assertIn(payload["status"], {"completed", "failed"})
        self.assertIn("current_stage", payload)
        self.assertIn("percent", payload)
        self.assertIn("steps", payload)
        self.assertGreater(len(payload["steps"]), 0)
        self.assertEqual(payload["steps"][-1]["status"], payload["status"])

    def test_result_and_artifact_endpoints_return_run_outputs(self) -> None:
        create = self.client.post(
            "/api/problem-to-simulation/runs",
            json={"text": ELASTIC_PROBLEM, "topic_hint": "high-school-physics"},
        ).json()
        self._wait_for_terminal_status(create["run_id"])

        result_response = self.client.get(f"/api/problem-to-simulation/runs/{create['run_id']}/result")
        self.assertEqual(result_response.status_code, 200)
        result_payload = result_response.json()
        self.assertEqual(result_payload["run_id"], create["run_id"])
        self.assertIn("delivery_bundle", result_payload)

        artifact_response = self.client.get(
            f"/api/problem-to-simulation/runs/{create['run_id']}/artifacts/problem_profile"
        )
        self.assertEqual(artifact_response.status_code, 200)
        self.assertEqual(artifact_response.json()["research_object"], "物块")

    def test_export_html_endpoint_generates_single_file_html(self) -> None:
        create = self.client.post(
            "/api/problem-to-simulation/runs",
            json={"text": ELASTIC_PROBLEM, "topic_hint": "high-school-physics"},
        ).json()
        self._wait_for_terminal_status(create["run_id"])

        export_response = self.client.post(f"/api/problem-to-simulation/runs/{create['run_id']}/export-html")
        self.assertEqual(export_response.status_code, 200)
        export_payload = export_response.json()
        self.assertEqual(export_payload["run_id"], create["run_id"])
        self.assertEqual(export_payload["export_mode"], "single-file-html")

        html_response = self.client.get(f"/api/problem-to-simulation/runs/{create['run_id']}/export-html")
        self.assertEqual(html_response.status_code, 200)
        self.assertIn("text/html", html_response.headers["content-type"])
        self.assertIn("Physics Problem to Simulation", html_response.text)
        self.assertIn("elastic-restoring-motion", html_response.text)


class ModelExecutorTests(unittest.TestCase):
    def test_execute_raises_immediately_on_socket_timeout_without_retry(self) -> None:
        executor = ModelExecutor()
        original_api_key = settings.openai_api_key

        try:
            settings.openai_api_key = "test-key"
            with patch(
                "urllib.request.urlopen",
                side_effect=socket.timeout("timed out"),
            ) as mocked_urlopen:
                with self.assertRaises(ModelExecutionTimeoutError):
                    executor.execute(
                        worker_name="problem_profile",
                        prompt="Extract JSON",
                        required_keys=["summary"],
                    )
        finally:
            settings.openai_api_key = original_api_key

        self.assertEqual(mocked_urlopen.call_count, 1)
        self.assertEqual(mocked_urlopen.call_args.kwargs["timeout"], REQUEST_TIMEOUT_SECONDS)

    def test_execute_returns_debug_trace_when_enabled(self) -> None:
        executor = ModelExecutor()
        original_api_key = settings.openai_api_key

        class _FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self) -> bytes:
                return json.dumps(
                    {
                        "choices": [
                            {
                                "message": {
                                    "content": json.dumps({"summary": "ok"}),
                                    "reasoning_content": "thinking...",
                                }
                            }
                        ]
                    }
                ).encode("utf-8")

        try:
            settings.openai_api_key = "test-key"
            with patch("urllib.request.urlopen", return_value=_FakeResponse()):
                payload, metadata = executor.execute(
                    worker_name="problem_profile",
                    prompt="Extract JSON",
                    required_keys=["summary"],
                    debug=True,
                )
        finally:
            settings.openai_api_key = original_api_key

        self.assertEqual(payload, {"summary": "ok"})
        self.assertIn("debug_trace", metadata)
        trace = metadata["debug_trace"]
        self.assertEqual(trace["worker_name"], "problem_profile")
        self.assertEqual(trace["response"]["reasoning_content"], "thinking...")
        self.assertEqual(trace["response"]["parsed_candidate"], {"summary": "ok"})
        self.assertEqual(trace["request_payload"]["messages"][-1]["content"], "Extract JSON")

    def test_execute_timeout_error_carries_debug_trace(self) -> None:
        executor = ModelExecutor()
        original_api_key = settings.openai_api_key

        try:
            settings.openai_api_key = "test-key"
            with patch(
                "urllib.request.urlopen",
                side_effect=socket.timeout("timed out"),
            ):
                with self.assertRaises(ModelExecutionTimeoutError) as context:
                    executor.execute(
                        worker_name="physics_model",
                        prompt="Build JSON",
                        required_keys=["model_type"],
                        debug=True,
                    )
        finally:
            settings.openai_api_key = original_api_key

        self.assertEqual(
            context.exception.debug_trace["request_payload"]["messages"][-1]["content"],
            "Build JSON",
        )
        self.assertEqual(context.exception.debug_trace["error"]["type"], "timeout")


class HarnessDebugTraceTests(unittest.TestCase):
    def test_debug_run_writes_llm_trace_artifacts(self) -> None:
        original_api_key = settings.openai_api_key

        class _FakeResponse:
            def __init__(self, payload: dict) -> None:
                self.payload = payload

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self) -> bytes:
                return json.dumps(self.payload, ensure_ascii=False).encode("utf-8")

        responses = [
            _FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "summary": "钢球滚下斜面后做平抛并击中可调木板",
                                        "research_object": "钢球",
                                        "scenario": "斜面出射后的平抛运动",
                                        "stages": [
                                            {
                                                "id": "stage-1",
                                                "label": "斜面滚下与出射",
                                                "description": "钢球从斜面滚下并水平出射",
                                                "contact_state": "与斜面/桌面接触",
                                                "key_question": "出射瞬间初速度如何确定？",
                                            },
                                            {
                                                "id": "stage-2",
                                                "label": "平抛飞行与击板",
                                                "description": "钢球离台后做平抛并击中木板",
                                                "contact_state": "空中飞行",
                                                "key_question": "h 改变时飞行时间和速度方向如何变化？",
                                            },
                                        ],
                                        "topic": "high-school-physics",
                                        "problem_family": "projectile-motion",
                                        "model_family": "projectile-motion",
                                        "stage_type": "projectile-board-impact",
                                        "simulation_mode": "trajectory-lab",
                                        "simulation_ready": True,
                                    },
                                    ensure_ascii=False,
                                ),
                                "reasoning_content": "profile reasoning",
                            }
                        }
                    ]
                }
            ),
            _FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "model_type": "projectile_motion",
                                        "research_object": "钢球",
                                        "force_cases": [
                                            {
                                                "stage_id": "stage-1",
                                                "forces": ["重力", "支持力"],
                                            },
                                            {
                                                "stage_id": "stage-2",
                                                "forces": ["重力"],
                                            },
                                        ],
                                        "misconceptions": ["误以为 h 改变不会影响末速度方向"],
                                        "derived_quantities": {
                                            "time_of_flight": "sqrt(2h/g)",
                                            "horizontal_displacement": "x=v0*sqrt(2h/g)",
                                            "vertical_speed": "vy=sqrt(2gh)",
                                        },
                                        "knowledge_points": ["平抛运动", "运动分解"],
                                        "option_analysis": {"A": "错误", "B": "正确"},
                                    },
                                    ensure_ascii=False,
                                ),
                                "reasoning_content": "model reasoning",
                            }
                        }
                    ]
                }
            ),
            _FakeResponse(
                {
                    "choices": [
                        {
                            "message": {
                                "content": json.dumps(
                                    {
                                        "classroom_use": "选项辨析 + 参数探究",
                                        "primary_goal": "显化 h、t、x 和末速度方向之间的关系",
                                        "observation_targets": ["飞行时间变化", "末速度方向变化"],
                                        "teacher_prompts": ["拖动 h 观察轨迹", "对照公式面板解释变化"],
                                    },
                                    ensure_ascii=False,
                                ),
                                "reasoning_content": "teaching reasoning",
                            }
                        }
                    ]
                }
            ),
        ]

        try:
            settings.openai_api_key = "test-key"
            with tempfile.TemporaryDirectory() as temp_dir:
                with patch("urllib.request.urlopen", side_effect=responses):
                    result = run_problem_to_simulation_harness(
                        ProblemInput(
                            text=PROJECTILE_PROBLEM,
                            topic_hint="high-school-physics",
                            mode="llm-assisted",
                            debug=True,
                        ),
                        runs_root=Path(temp_dir),
                    )

                run_dir = Path(temp_dir) / result["run_id"]
                for worker_name in ("problem_profile", "physics_model", "teaching_plan"):
                    trace_path = run_dir / "artifacts" / f"llm_debug_{worker_name}.json"
                    self.assertTrue(trace_path.exists(), msg=f"missing {trace_path}")
                    trace = json.loads(trace_path.read_text(encoding="utf-8"))
                    self.assertEqual(trace["worker_name"], worker_name)
                    self.assertIn("request_payload", trace)
                    self.assertIn("response", trace)
                    self.assertIn("elapsed_ms", trace)
                    self.assertIsNotNone(trace["response"]["reasoning_content"])
        finally:
            settings.openai_api_key = original_api_key


if __name__ == "__main__":
    unittest.main()
