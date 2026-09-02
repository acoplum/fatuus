"""Orquestração do pipeline agêntico da Camada 1."""

from dataclasses import dataclass
from typing import Any, Dict, List

from agno.workflow.loop import Loop
from agno.workflow.step import Step
from agno.workflow.types import StepInput, StepOutput
from agno.workflow.workflow import Workflow

from .agents import (
    build_anti_simetria_agent,
    build_cadencia_agent,
    build_integridade_agent,
    build_watermark_agent,
)
from .detector import FatuusDetector
from .gate import GateResult, evaluate_gate

DEFAULT_MAX_ITERATIONS = 3


@dataclass
class PipelineResult:
    final_text: str
    accepted: bool
    attempts: int
    gate: GateResult


def _needs_layer1(analysis: Dict[str, Any]) -> bool:
    return (
        analysis["slop_count"] > 0
        or analysis["invisible_char_count"] > 0
        or analysis["sentence_metrics"]["burstiness"] < 0
    )


def _needs_watermark_agent(analysis: Dict[str, Any]) -> bool:
    return analysis["invisible_char_count"] > 0


def _make_rewrite_step(name: str, agent: Any) -> Step:
    def _run(step_input: StepInput) -> StepOutput:
        current_text = step_input.previous_step_content or step_input.input or ""
        response = agent.run(current_text)
        return StepOutput(step_name=name, content=response.content, success=True)

    return Step(name=name, executor=_run, description=name)


def _make_integridade_step(name: str, agent: Any) -> Step:
    def _run(step_input: StepInput) -> StepOutput:
        original_text = step_input.input or ""
        current_text = step_input.previous_step_content or original_text
        prompt = (
            f"Texto original:\n{original_text}\n\n"
            f"Reescrita a revisar:\n{current_text}"
        )
        response = agent.run(prompt)
        return StepOutput(step_name=name, content=response.content, success=True)

    return Step(name=name, executor=_run, description=name)


class HumanizationPipeline:
    """Pipeline de agentes Agno da Camada 1, com gate determinístico final.

    Limitação conhecida: `attempts` é sempre 1 quando o pipeline roda,
    porque o retry entre tentativas é gerenciado internamente pelo `Loop`
    do Agno (via `end_condition`) e este módulo não expõe a contagem real
    de iterações do `WorkflowRunOutput`. Refinar quando houver necessidade
    real de expor isso na API.
    """

    def __init__(
        self,
        model: Any,
        lang: str = "pt",
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
    ):
        self.model = model
        self.lang = lang
        self.max_iterations = max_iterations
        self.detector = FatuusDetector(lang=lang)
        self._original_text = ""

    def _build_workflow(self, needs_watermark: bool) -> Workflow:
        steps: List[Step] = [
            _make_rewrite_step(
                "cadencia", build_cadencia_agent(self.model, self.lang)
            ),
            _make_rewrite_step(
                "anti_simetria", build_anti_simetria_agent(self.model, self.lang)
            ),
            _make_integridade_step(
                "integridade_semantica",
                build_integridade_agent(self.model, self.lang),
            ),
        ]
        if needs_watermark:
            steps.append(
                _make_rewrite_step(
                    "watermark_estatistico",
                    build_watermark_agent(self.model, self.lang),
                )
            )

        def _gate_end_condition(outputs: List[StepOutput]) -> bool:
            candidate_text = outputs[-1].content if outputs else ""
            return evaluate_gate(
                self.lang, self._original_text, candidate_text
            ).accepted

        loop = Loop(
            name="humanizacao_loop",
            steps=steps,
            max_iterations=self.max_iterations,
            end_condition=_gate_end_condition,
        )
        return Workflow(name="fatuus_camada1", steps=[loop])

    def run(self, sanitized_text: str) -> PipelineResult:
        """Executa a Camada 1 sobre um texto já limpo pela Camada 0."""
        self._original_text = sanitized_text
        original_analysis = self.detector.analyze(sanitized_text)

        if not _needs_layer1(original_analysis):
            gate = evaluate_gate(self.lang, sanitized_text, sanitized_text)
            return PipelineResult(
                final_text=sanitized_text, accepted=True, attempts=0, gate=gate
            )

        workflow = self._build_workflow(_needs_watermark_agent(original_analysis))
        run_output = workflow.run(input=sanitized_text)
        candidate_text = getattr(run_output, "content", None) or sanitized_text

        gate = evaluate_gate(self.lang, sanitized_text, candidate_text)

        if gate.accepted:
            return PipelineResult(
                final_text=candidate_text, accepted=True, attempts=1, gate=gate
            )

        return PipelineResult(
            final_text=sanitized_text, accepted=False, attempts=1, gate=gate
        )
