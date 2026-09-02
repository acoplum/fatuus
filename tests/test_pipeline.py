import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("GOOGLE_API_KEY", "test-key-for-unit-tests")

from agno.models.google import Gemini

from fatuus.pipeline import HumanizationPipeline

ORIGINAL_WITH_SLOP = (
    "É importante ressaltar que o sistema funciona bem. É importante "
    "ressaltar que o sistema é rápido. É importante ressaltar que o sistema "
    "é seguro."
)
GOOD_CANDIDATE = (
    "O sistema funciona bem. É rápido, seguro, e resolveu um problema real "
    "que ninguém tinha atacado antes com essa profundidade."
)
BAD_CANDIDATE = "É importante ressaltar que o sistema funciona bem."


class TestHumanizationPipeline(unittest.TestCase):
    def setUp(self):
        self.model = Gemini(id="gemini-3.7-flash")

    def test_skips_pipeline_when_layer0_signals_are_clean(self):
        pipeline = HumanizationPipeline(self.model, lang="pt")
        result = pipeline.run("O sistema funciona bem.")
        self.assertTrue(result.accepted)
        self.assertEqual(result.attempts, 0)
        self.assertEqual(result.final_text, "O sistema funciona bem.")

    def test_build_workflow_includes_watermark_step_when_needed(self):
        pipeline = HumanizationPipeline(self.model, lang="pt")
        workflow = pipeline._build_workflow(needs_watermark=True)
        step_names = [step.name for step in workflow.steps[0].steps]
        self.assertEqual(
            step_names,
            [
                "cadencia",
                "anti_simetria",
                "integridade_semantica",
                "watermark_estatistico",
            ],
        )

    def test_build_workflow_excludes_watermark_step_by_default(self):
        pipeline = HumanizationPipeline(self.model, lang="pt")
        workflow = pipeline._build_workflow(needs_watermark=False)
        step_names = [step.name for step in workflow.steps[0].steps]
        self.assertEqual(
            step_names, ["cadencia", "anti_simetria", "integridade_semantica"]
        )

    @patch("fatuus.pipeline.Workflow.run")
    def test_accepts_candidate_that_passes_the_gate(self, mock_run):
        mock_run.return_value = SimpleNamespace(content=GOOD_CANDIDATE)
        pipeline = HumanizationPipeline(self.model, lang="pt")
        result = pipeline.run(ORIGINAL_WITH_SLOP)
        self.assertTrue(result.accepted)
        self.assertEqual(result.final_text, GOOD_CANDIDATE)

    @patch("fatuus.pipeline.Workflow.run")
    def test_falls_back_to_input_when_candidate_fails_the_gate(self, mock_run):
        mock_run.return_value = SimpleNamespace(content=BAD_CANDIDATE)
        pipeline = HumanizationPipeline(self.model, lang="pt")
        result = pipeline.run(ORIGINAL_WITH_SLOP)
        self.assertFalse(result.accepted)
        self.assertEqual(result.final_text, ORIGINAL_WITH_SLOP)


if __name__ == "__main__":
    unittest.main()
