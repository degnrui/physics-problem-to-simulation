import json
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.domain.problem import ProblemInput
from app.main import app
from app.orchestrator.graph import create_coordinator_graph
from app.orchestrator.runner import plan_problem_to_simulation, run_problem_to_simulation_harness
from app.runtime.generator_client import RuntimeGeneratorClient


NEW_SIMULATION_PROBLEM = (
    "如图所示，两根相同的橡皮绳连接物块，沿 AB 中垂线拉至 O 点后释放。"
    "请生成一个适合课堂讲评的 simulation，突出回复力方向、摩擦耗能和教学观察顺序。"
)

REVISION_PROBLEM = (
    "请在已有 simulation 的基础上修改：保留原有小球运动场景，"
    "新增速度-时间图和测量面板，并让教师模式默认展示证据面板。"
)


class CoordinatorGraphTests(unittest.TestCase):
    def test_plan_for_new_simulation_uses_new_stage_names(self) -> None:
        result = plan_problem_to_simulation(ProblemInput(text=NEW_SIMULATION_PROBLEM))

        self.assertEqual(result["run_state"]["request_mode"], "new_simulation")
        self.assertEqual(
            result["run_state"]["workflow_plan"],
            [
                "request_analysis",
                "domain_grounding",
                "instructional_modeling",
                "simulation_design",
                "runtime_package_assembly",
                "code_generation",
                "runtime_validation",
            ],
        )
        self.assertNotIn("compile_delivery", json.dumps(result, ensure_ascii=False))

    def test_plan_for_revision_route_marks_revision_mode(self) -> None:
        result = plan_problem_to_simulation(ProblemInput(text=REVISION_PROBLEM))

        self.assertEqual(result["run_state"]["request_mode"], "revision_existing_simulation")
        self.assertTrue(result["artifacts"]["request_analysis"]["has_existing_simulation"])

    def test_runtime_validation_failure_retries_code_generation_only(self) -> None:
        calls = {"count": 0}

        def fake_generate(self, runtime_package):  # noqa: ANN001
            calls["count"] += 1
            if calls["count"] == 1:
                html = "<html><body><h1>Simulation Payload</h1><pre>{}</pre></body></html>"
            else:
                html = """
                <html>
                  <body>
                    <main data-testid="runtime-root">
                      <canvas id="simulation-canvas"></canvas>
                      <button>play</button>
                      <button>pause</button>
                      <button>reset</button>
                      <input type="range" aria-label="mass control" />
                      <section id="measurement-panel">measurement</section>
                    </main>
                  </body>
                </html>
                """
            return {
                "files": {"simulation.html": html},
                "generator_metadata": {"provider": "test", "model": "fake-generator"},
                "primary_file": "simulation.html",
            }

        with patch.object(RuntimeGeneratorClient, "generate", fake_generate):
            result = run_problem_to_simulation_harness(
                ProblemInput(text=NEW_SIMULATION_PROBLEM),
                runs_root=Path(tempfile.mkdtemp()),
            )

        self.assertEqual(calls["count"], 2)
        trace_stages = [event["stage"] for event in result["execution_trace"]]
        self.assertGreaterEqual(trace_stages.count("code_generation"), 2)
        self.assertGreaterEqual(trace_stages.count("runtime_validation"), 2)
        self.assertEqual(result["run_state"]["stage_status"]["runtime_validation"]["status"], "approved")
        self.assertIn("delivery_runtime", result)

    def test_simulation_design_subgraph_requires_all_child_nodes(self) -> None:
        graph = create_coordinator_graph()
        self.assertIn("simulation_design", graph.stage_order)
        self.assertEqual(
            graph.subgraphs["simulation_design"],
            [
                "scene_design",
                "control_design",
                "chart_measurement_design",
                "pedagogical_view_design",
                "design_merge",
            ],
        )


class CoordinatorApiTests(unittest.TestCase):
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

    def test_run_result_uses_new_contract_only(self) -> None:
        create = self.client.post(
            "/api/problem-to-simulation/runs",
            json={"text": NEW_SIMULATION_PROBLEM},
        ).json()
        self._wait_for_terminal_status(create["run_id"])

        result = self.client.get(f"/api/problem-to-simulation/runs/{create['run_id']}/result")
        payload = result.json()

        self.assertEqual(result.status_code, 200)
        self.assertEqual(
            set(payload.keys()),
            {
                "run_id",
                "run_state",
                "artifacts",
                "approved_artifacts",
                "runtime_package",
                "generated_files",
                "delivery_runtime",
                "execution_trace",
            },
        )
        self.assertNotIn("compile_delivery", payload)
        self.assertIn("runtime_validation", payload["run_state"]["stage_status"])

    def test_artifact_endpoint_reads_new_stage_artifact(self) -> None:
        create = self.client.post(
            "/api/problem-to-simulation/runs",
            json={"text": NEW_SIMULATION_PROBLEM},
        ).json()
        self._wait_for_terminal_status(create["run_id"])

        artifact = self.client.get(
            f"/api/problem-to-simulation/runs/{create['run_id']}/artifacts/simulation_design"
        )
        payload = artifact.json()

        self.assertEqual(artifact.status_code, 200)
        self.assertIn("scene", payload)
        self.assertIn("controls", payload)
        self.assertIn("charts", payload)

    def test_export_html_returns_validated_runtime_only(self) -> None:
        create = self.client.post(
            "/api/problem-to-simulation/runs",
            json={"text": NEW_SIMULATION_PROBLEM},
        ).json()
        self._wait_for_terminal_status(create["run_id"])

        export_response = self.client.post(f"/api/problem-to-simulation/runs/{create['run_id']}/export-html")
        self.assertEqual(export_response.status_code, 200)
        export_payload = export_response.json()
        self.assertEqual(export_payload["export_mode"], "single-file-html")

        html_response = self.client.get(f"/api/problem-to-simulation/runs/{create['run_id']}/export-html")
        self.assertEqual(html_response.status_code, 200)
        self.assertIn("simulation-canvas", html_response.text)
        self.assertIn("play", html_response.text)
        self.assertNotIn("Simulation Payload", html_response.text)


if __name__ == "__main__":
    unittest.main()
