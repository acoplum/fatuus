import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("GOOGLE_API_KEY", "test-key-for-unit-tests")

from agno.models.google import Gemini
from agno.run.agent import RunOutput
from agno.run.base import RunStatus
from agno.workflow.types import StepInput

from fatuus.pipeline import (
    HumanizationPipeline,
    _make_integridade_step,
    _make_rewrite_step,
)
from fatuus.sanitizer import FatuusSanitizer

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


class TestStepFailureHandling(unittest.TestCase):
    """Achado #4: falha do agente virava texto candidato.

    Numa falha, o Agno devolve `RunOutput` com `status=error` e o texto da
    exceção dentro de `content` (`agno/agent/_run.py`), então usar
    `response.content` sem checar status entrega a mensagem de erro como se
    fosse a reescrita.
    """

    def _agent(self, response):
        return SimpleNamespace(run=lambda *_args, **_kwargs: response)

    def test_rewrite_step_fails_when_the_agent_run_errors(self):
        erro = RunOutput(content="429 RESOURCE_EXHAUSTED", status=RunStatus.error)
        step = _make_rewrite_step("cadencia", self._agent(erro))

        output = step.executor(StepInput(input="texto original"))

        self.assertFalse(output.success)
        self.assertIsNone(output.content)
        self.assertIn("cadencia", output.error)

    def test_rewrite_step_fails_when_the_agent_returns_blank_content(self):
        vazio = RunOutput(content="   ", status=RunStatus.completed)
        step = _make_rewrite_step("cadencia", self._agent(vazio))

        output = step.executor(StepInput(input="texto original"))

        self.assertFalse(output.success)

    def test_integridade_step_fails_when_the_agent_run_errors(self):
        erro = RunOutput(content="500 INTERNAL", status=RunStatus.error)
        step = _make_integridade_step("integridade_semantica", self._agent(erro))

        output = step.executor(StepInput(input="texto original"))

        self.assertFalse(output.success)
        self.assertIsNone(output.content)

    def test_steps_accept_a_successful_response(self):
        ok = RunOutput(content="reescrita", status=RunStatus.completed)
        step = _make_rewrite_step("cadencia", self._agent(ok))

        output = step.executor(StepInput(input="texto original"))

        self.assertTrue(output.success)
        self.assertEqual(output.content, "reescrita")


class TestSanitizerToPipelineIntegration(unittest.TestCase):
    """Fluxo real do `/clean`: Camada 0 sanitiza, Camada 1 reescreve.

    Só o `Agent.run` é mockado — o `Workflow`, o `Loop` e o gate rodam de
    verdade. Foi o mock no nível de `Workflow.run` que escondeu o achado #3
    por dez revisões de task.
    """

    def setUp(self):
        self.model = Gemini(id="gemini-3.7-flash")
        self.sanitized = FatuusSanitizer(lang="pt").clean(ORIGINAL_WITH_SLOP)

    @patch("agno.agent.Agent.run")
    def test_realistic_rewrite_passes_the_gate_in_the_real_flow(self, mock_agent_run):
        mock_agent_run.return_value = RunOutput(
            content=GOOD_CANDIDATE, status=RunStatus.completed
        )
        pipeline = HumanizationPipeline(self.model, lang="pt")

        result = pipeline.run(
            self.sanitized["cleaned_text"], original_text=ORIGINAL_WITH_SLOP
        )

        self.assertTrue(result.accepted, result.gate.reasons)
        self.assertEqual(result.final_text, GOOD_CANDIDATE)
        self.assertEqual(result.attempts, 1)

    @patch("agno.agent.Agent.run")
    def test_gate_measures_size_against_the_pre_sanitization_text(
        self, mock_agent_run
    ):
        mock_agent_run.return_value = RunOutput(
            content=GOOD_CANDIDATE, status=RunStatus.completed
        )
        pipeline = HumanizationPipeline(self.model, lang="pt")

        sem_baseline = pipeline.run(self.sanitized["cleaned_text"])

        self.assertFalse(sem_baseline.accepted)
        self.assertTrue(
            any("variação de tamanho" in r for r in sem_baseline.gate.reasons),
            sem_baseline.gate.reasons,
        )

    @patch("agno.agent.Agent.run")
    def test_attempts_reports_the_real_iteration_count(self, mock_agent_run):
        mock_agent_run.return_value = RunOutput(
            content=BAD_CANDIDATE, status=RunStatus.completed
        )
        pipeline = HumanizationPipeline(self.model, lang="pt", max_iterations=3)

        result = pipeline.run(
            self.sanitized["cleaned_text"], original_text=ORIGINAL_WITH_SLOP
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.attempts, 3)
        self.assertEqual(mock_agent_run.call_count, 9)

    @patch("agno.agent.Agent.run")
    def test_reports_failure_instead_of_using_the_agent_error_as_text(
        self, mock_agent_run
    ):
        mock_agent_run.return_value = RunOutput(
            content="429 RESOURCE_EXHAUSTED: quota excedida", status=RunStatus.error
        )
        pipeline = HumanizationPipeline(self.model, lang="pt")

        result = pipeline.run(
            self.sanitized["cleaned_text"], original_text=ORIGINAL_WITH_SLOP
        )

        self.assertFalse(result.accepted)
        self.assertEqual(result.final_text, self.sanitized["cleaned_text"])
        self.assertNotIn("RESOURCE_EXHAUSTED", result.final_text)
        self.assertTrue(
            any("falhou" in r for r in result.gate.reasons), result.gate.reasons
        )


if __name__ == "__main__":
    unittest.main()
