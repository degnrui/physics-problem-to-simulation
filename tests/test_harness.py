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
from app.harness.orchestrator import plan_problem_to_simulation, run_problem_to_simulation_harness


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

PENDULUM_PROBLEM = (
    "如图所示,不可伸长的光滑细线穿过质量为 0.1kg 的小铁球,两端 A、B 悬挂在倾角为 30°的固定斜杆上,间距为 1.5m。"
    "小球平衡时,A 端细线与杆垂直;当小球受到垂直纸面方向的扰动做微小摆动时,等效于悬挂点位于小球重垂线与 AB 交点的单摆,"
    "重力加速度g = 10m/s^{2},则(   )"
    "A. 摆角变小,周期变大 "
    "B. 小球摆动周期约为 2s "
    "C. 小球平衡时,A 端拉力为sqrt(3)/2 N "
    "D. 小球平衡时,A 端拉力小于 B 端拉力 "
    "答案：B "
    "解析：根据单摆的周期公式 T=2pi sqrt(l/g) 可知周期与摆角无关；"
    "摆长为 1 m，周期约为 2 s；同一根绳中两端张力相等。"
)


class HarnessOrchestratorTests(unittest.TestCase):
    def test_plan_uses_stage_runtime_without_legacy_model_routing(self) -> None:
        result = plan_problem_to_simulation(
            ProblemInput(text=CAT_STAGE_PROBLEM, topic_hint="force-analysis")
        )

        self.assertNotIn("planner", result)
        self.assertIn("run_profiling", result)
        self.assertNotIn("problem_family", result["run_profiling"])
        self.assertNotIn("model_family", result["run_profiling"])
        self.assertNotIn("simulation_mode", result["run_profiling"])
        self.assertEqual(result["task_plan"]["tasks"][0]["type"], "run_profiling")
        self.assertEqual(result["task_plan"]["tasks"][-1]["type"], "compile_delivery")
        self.assertEqual(result["stage_graph"][3], "structured_task_model")

    def test_plan_builds_stage_graph_for_generic_contact_transition_problem(self) -> None:
        result = plan_problem_to_simulation(
            ProblemInput(text=GENERIC_TRANSITION_PROBLEM, topic_hint="force-analysis")
        )

        self.assertEqual(result["run_profiling"]["input_profile"], "problem_only")
        self.assertIn("knowledge_grounding", result["stage_graph"])
        self.assertIn("final_validation", result["stage_graph"])

    def test_plan_builds_stage_graph_for_modeling_problem_without_analysis_route_alias(self) -> None:
        result = plan_problem_to_simulation(
            ProblemInput(text=MODELING_PROBLEM, topic_hint="force-analysis")
        )

        self.assertEqual(result["task_plan"]["tasks"][-1]["type"], "compile_delivery")
        self.assertTrue(result["task_plan"]["tasks"][-1]["conditional"])

    def test_run_writes_new_stage_artifacts_and_final_package(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_problem_to_simulation_harness(
                ProblemInput(text=CAT_STAGE_PROBLEM, topic_hint="force-analysis"),
                runs_root=Path(temp_dir),
            )

            run_dir = Path(temp_dir) / result["run_id"]
            self.assertTrue((run_dir / "task_plan.json").exists())
            self.assertTrue((run_dir / "task_log.ndjson").exists())
            self.assertTrue((run_dir / "artifacts" / "run_profiling.json").exists())
            self.assertTrue((run_dir / "artifacts" / "knowledge_grounding.json").exists())
            self.assertTrue((run_dir / "artifacts" / "structured_task_model.json").exists())
            self.assertTrue((run_dir / "artifacts" / "instructional_design_brief.json").exists())
            self.assertTrue((run_dir / "artifacts" / "physics_model.json").exists())
            self.assertTrue((run_dir / "artifacts" / "representation_interaction_design.json").exists())
            self.assertTrue((run_dir / "artifacts" / "experience_mode_adaptation.json").exists())
            self.assertTrue((run_dir / "artifacts" / "simulation_spec_generation.json").exists())
            self.assertTrue((run_dir / "artifacts" / "final_validation.json").exists())
            self.assertTrue((run_dir / "artifacts" / "compile_delivery.json").exists())
            self.assertTrue((run_dir / "final_package.json").exists())
            self.assertGreaterEqual(len(result["task_log"]), 9)

            final_package = json.loads((run_dir / "final_package.json").read_text(encoding="utf-8"))
            self.assertEqual(final_package["structured_task_model"]["research_object"], "小猫")
            self.assertIn("run_profiling", final_package)
            self.assertIn("final_validation", final_package)
            self.assertIn("compile_delivery", final_package)
            self.assertNotIn("planner", final_package)
            self.assertNotIn("problem_profile", final_package)
            self.assertTrue((run_dir / "status.json").exists())

    def test_run_builds_staged_force_scene_for_generic_contact_transition_problem(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_problem_to_simulation_harness(
                ProblemInput(text=GENERIC_TRANSITION_PROBLEM, topic_hint="force-analysis"),
                runs_root=Path(temp_dir),
            )

            scene_spec = result["simulation_spec_generation"]["scene_spec"]
            self.assertTrue(scene_spec["template_id"].startswith("physics-"))
            self.assertGreaterEqual(len(scene_spec["controls"]), 1)

    def test_plan_does_not_emit_legacy_projectile_family_route(self) -> None:
        result = plan_problem_to_simulation(
            ProblemInput(text=PROJECTILE_PROBLEM, topic_hint="high-school-physics")
        )

        self.assertNotIn("problem_family", result["run_profiling"])
        self.assertEqual(result["run_profiling"]["input_profile"], "problem_only")

    def test_plan_does_not_emit_legacy_elastic_family_route(self) -> None:
        result = plan_problem_to_simulation(
            ProblemInput(text=ELASTIC_PROBLEM, topic_hint="high-school-physics")
        )

        self.assertNotIn("problem_family", result["run_profiling"])
        self.assertEqual(result["run_profiling"]["input_profile"], "problem_only")

    def test_run_builds_generic_stage_package_without_legacy_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_problem_to_simulation_harness(
                ProblemInput(text=ELASTIC_PROBLEM, topic_hint="high-school-physics"),
                runs_root=Path(temp_dir),
            )

            self.assertEqual(result["structured_task_model"]["research_object"], "物块")
            self.assertIn("scene_spec", result["simulation_spec_generation"])
            self.assertIn("simulation_spec", result["simulation_spec_generation"])
            self.assertEqual(result["compile_delivery"]["delivery_bundle"]["primary_view"], "simulation-viewport")
            self.assertTrue(result["final_validation"]["ready_for_generation"])

    def test_task_plan_includes_post_package_simulation_tasks(self) -> None:
        result = plan_problem_to_simulation(
            ProblemInput(text=ELASTIC_PROBLEM, topic_hint="high-school-physics")
        )

        task_types = [task["type"] for task in result["task_plan"]["tasks"]]
        self.assertIn("simulation_spec_generation", task_types)
        self.assertIn("final_validation", task_types)
        self.assertIn("compile_delivery", task_types)

    def test_elastic_package_meets_simulation_lab_quality_bar(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_problem_to_simulation_harness(
                ProblemInput(text=ELASTIC_PROBLEM, topic_hint="high-school-physics"),
                runs_root=Path(temp_dir),
            )

            blueprint = result["compile_delivery"]["simulation_blueprint"]
            delivery_bundle = result["compile_delivery"]["delivery_bundle"]
            renderer_payload = result["compile_delivery"]["renderer_payload"]

            self.assertEqual(blueprint["delivery_mode"], "interactive-teaching-demo")
            self.assertTrue(blueprint["minimum_quality_bar"]["interactive_controls"])
            self.assertTrue(blueprint["minimum_quality_bar"]["teacher_guidance"])
            self.assertTrue(blueprint["minimum_quality_bar"]["evidence_panel"])
            self.assertTrue(blueprint["minimum_quality_bar"]["formula_panel"])

            self.assertEqual(renderer_payload["layout_mode"], "physics-workbench")

            self.assertIn("evidence-panel", delivery_bundle["secondary_views"])
            self.assertIn("formula-panel", delivery_bundle["secondary_views"])
            self.assertIn("teacher-guidance", delivery_bundle["secondary_views"])
            self.assertIn("validation-report", delivery_bundle["secondary_views"])

            required_panels = {
                "simulation_canvas",
                "evidence_panel",
                "formula_panel",
                "teacher_guidance",
            }
            self.assertTrue(required_panels.issubset(set(delivery_bundle["panel_contract"].keys())))

    def test_renderer_payload_carries_frontend_design_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_problem_to_simulation_harness(
                ProblemInput(text=ELASTIC_PROBLEM, topic_hint="high-school-physics"),
                runs_root=Path(temp_dir),
            )

            renderer_payload = result["compile_delivery"]["renderer_payload"]
            delivery_bundle = result["compile_delivery"]["delivery_bundle"]

            self.assertEqual(renderer_payload["layout_mode"], "physics-workbench")
            self.assertEqual(renderer_payload["component_key"], "generic-physics-runtime")
            self.assertIn("scene_spec", renderer_payload)
            self.assertIn("simulation_spec", renderer_payload)

            inspector = delivery_bundle["inspector_contract"]
            self.assertIn("summary", inspector)
            self.assertIn("artifacts", inspector)
            self.assertIn("validation", inspector)
            self.assertIn("knowledge_grounding", inspector["artifacts"])
            self.assertIn("physics_model", inspector["artifacts"])
            self.assertIn("simulation_spec_generation", inspector["artifacts"])
            self.assertEqual(delivery_bundle["artifact_tabs"][0]["id"], "summary")
            self.assertIn("simulation_canvas", delivery_bundle["default_open_panels"])
            self.assertIn("teacher_guidance", delivery_bundle["default_open_panels"])
            self.assertTrue(delivery_bundle["exportable"])
            self.assertEqual(delivery_bundle["export_mode"], "single-file-html")
            self.assertIn("compile_delivery", delivery_bundle["export_includes"])
            self.assertTrue(result["final_validation"]["export_ready"])
            self.assertIn("stage_validations", result)

    def test_pendulum_problem_is_not_forced_into_legacy_force_analysis_route(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_problem_to_simulation_harness(
                ProblemInput(text=PENDULUM_PROBLEM, topic_hint="high-school-physics"),
                runs_root=Path(temp_dir),
            )

            self.assertEqual(result["run_profiling"]["input_profile"], "problem_with_solution")
            self.assertNotIn("planner", result)
            self.assertIn("单摆", json.dumps(result["knowledge_grounding"], ensure_ascii=False))
            self.assertIn("单摆", json.dumps(result["physics_model"], ensure_ascii=False))
            self.assertTrue(
                result["simulation_spec_generation"]["scene_spec"]["template_id"].startswith("physics-")
            )


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
        terminal = self._wait_for_terminal_status(payload["run_id"])
        self.assertIn(terminal["status"], {"completed", "failed"})

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
        self.assertEqual(latest["input_profile"], "problem_only")
        self.assertEqual(latest["experience_mode"], "hybrid")
        self.assertGreaterEqual(latest["score"], 90)
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
        self.assertIn("compile_delivery", result_payload)

        artifact_response = self.client.get(
            f"/api/problem-to-simulation/runs/{create['run_id']}/artifacts/structured_task_model"
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
        self.assertIn("physics-", html_response.text)


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
                                        "input_profile": "problem_only",
                                        "run_mode": "generate_from_problem",
                                        "information_density": "high",
                                        "experience_mode": "teacher_demo",
                                        "needs_external_completion": False,
                                        "needs_solution_generation": True,
                                        "needs_solution_verification": True,
                                        "missing_context": [],
                                        "next_stage_plan": ["02_knowledge_grounding", "03_structured_task_model"],
                                        "has_explicit_problem": True,
                                        "has_explicit_solution": False,
                                        "has_diagram_reference": True,
                                        "has_existing_simulation": False,
                                    },
                                    ensure_ascii=False,
                                ),
                                "reasoning_content": "run profiling reasoning",
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
                                        "completion_status": "skipped",
                                        "evidence_bundle": {
                                            "reference_solution_status": "needs-verification",
                                            "diagram_parsed": False,
                                            "assumptions_added": False,
                                        },
                                    },
                                    ensure_ascii=False,
                                ),
                                "reasoning_content": "evidence completion reasoning",
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
                                        "grounding_type": "problem_solution_verified",
                                        "trustworthy": True,
                                        "concept_boundaries": ["平抛分解", "离台后仅受重力"],
                                        "assumptions": ["忽略空气阻力"],
                                        "solution_basis": ["平抛运动独立分解"],
                                    },
                                    ensure_ascii=False,
                                ),
                                "reasoning_content": "grounding reasoning",
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
                for worker_name in ("run_profiling", "knowledge_grounding", "structured_task_model"):
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
