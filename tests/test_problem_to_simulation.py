import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.domain.problem import ProblemInput
from app.pipeline.problem_to_simulation import run_problem_to_simulation


FORCE_ANALYSIS_PROBLEM = (
    "质量为2kg的木块静止在粗糙水平面上，受到大小为10N、方向水平向右的拉力作用。"
    "已知木块与地面间的摩擦力大小为4N，请分析木块的受力情况和运动状态。"
)

CAT_STAGE_PROBLEM = (
    "小猫从地面蹬地后跃起，在空中追逐前方飞行的蝴蝶。"
    "请分别分析小猫蹬地阶段和腾空阶段的受力情况，并判断在腾空后哪些力仍然存在。"
)

FOOTBALL_STAGE_PROBLEM = (
    "足球被踢出后在空中飞行并最终触网。忽略空气阻力，"
    "请围绕飞行阶段和触网阶段分析足球的受力特点，并判断哪些力在不同阶段存在或消失。"
)


class ProblemToSimulationPipelineTests(unittest.TestCase):
    def test_pipeline_builds_force_analysis_result_with_stage_logs(self) -> None:
        result = run_problem_to_simulation(
            ProblemInput(text=FORCE_ANALYSIS_PROBLEM, topic_hint="force-analysis")
        )

        self.assertEqual(result.physics_model["model_type"], "force_analysis")
        self.assertEqual(result.scene["scene_type"], "force-analysis")
        self.assertEqual(len(result.stage_logs), 4)
        self.assertIn("research_object", result.structured_problem)
        self.assertIn("forces", result.physics_model)
        self.assertIn("visual_elements", result.scene)

    def test_pipeline_exposes_debug_contract_fields(self) -> None:
        result = run_problem_to_simulation(
            ProblemInput(text=FORCE_ANALYSIS_PROBLEM, topic_hint="force-analysis", debug=True)
        )

        self.assertTrue(hasattr(result, "stage_logs"))
        self.assertEqual(result.stage_logs[0]["task_type"], "problem_parser")
        self.assertIn("warnings", result.model_dump())

    def test_pipeline_builds_multi_stage_force_scene_for_cat_problem(self) -> None:
        result = run_problem_to_simulation(
            ProblemInput(text=CAT_STAGE_PROBLEM, topic_hint="force-analysis")
        )

        self.assertEqual(result.physics_model["model_type"], "force_analysis")
        self.assertGreaterEqual(len(result.structured_problem["stages"]), 2)
        self.assertEqual(result.structured_problem["stages"][0]["label"], "蹬地阶段")
        self.assertEqual(result.structured_problem["stages"][1]["label"], "腾空阶段")
        self.assertGreaterEqual(len(result.physics_model["force_cases"]), 2)
        self.assertEqual(result.scene["parameters"]["active_stage_id"], "stage-1")
        self.assertGreaterEqual(len(result.scene["parameters"]["stage_options"]), 2)

    def test_pipeline_builds_multi_stage_force_scene_for_football_problem(self) -> None:
        result = run_problem_to_simulation(
            ProblemInput(text=FOOTBALL_STAGE_PROBLEM, topic_hint="force-analysis")
        )

        self.assertEqual(result.structured_problem["stages"][0]["label"], "飞行阶段")
        self.assertEqual(result.structured_problem["stages"][1]["label"], "触网阶段")
        self.assertEqual(result.scene["template_id"], "force-analysis-staged-v1")
        self.assertIn("stage-2", result.scene["parameters"]["forces_by_stage"])
        self.assertEqual(result.scene["parameters"]["forces_by_stage"]["stage-1"][0]["name"], "重力")


if __name__ == "__main__":
    unittest.main()
