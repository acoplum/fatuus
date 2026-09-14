"""Orquestração do pipeline agêntico da Camada 1."""

from dataclasses import dataclass
from typing import Any, Dict, List, cast

from agno.run.base import RunStatus
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

# Densidade de travessão que, sozinha, justifica acionar a Camada 1.
EM_DASH_TRIGGER_PER_100_WORDS = 1.5

_FEEDBACK_TEMPLATES = {
    "pt": (
        "\n\n[Revisão automática: a reescrita anterior deste texto foi "
        "rejeitada pelos motivos: {reasons}. Produza uma reescrita que evite "
        "esses problemas. Devolva só o texto reescrito.]"
    ),
    "en": (
        "\n\n[Automated review: the previous rewrite of this text was "
        "rejected for: {reasons}. Produce a rewrite that avoids these "
        "problems. Return only the rewritten text.]"
    ),
}


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
        or analysis["structural_count"] > 0
        or analysis["sentence_metrics"]["burstiness"] < 0
        or analysis["typography"]["em_dash_per_100_words"]
        > EM_DASH_TRIGGER_PER_100_WORDS
    )


def _needs_watermark_agent(analysis: Dict[str, Any]) -> bool:
    return analysis["invisible_char_count"] > 0


def _response_text(response: Any) -> str:
    """Texto utilizável de um `RunOutput` do Agno, ou vazio se falhou.

    Numa falha o Agno não levanta: devolve `RunOutput` com `status=error` e
    a mensagem da exceção dentro de `content` (`agno/agent/_run.py`). Ler
    `content` sem checar o status entrega o texto do erro como se fosse a
    reescrita do agente.
    """
    if getattr(response, "status", None) != RunStatus.completed:
        return ""
    content = getattr(response, "content", None)
    if not isinstance(content, str) or not content.strip():
        return ""
    return content


def _failed_step(name: str) -> StepOutput:
    return StepOutput(
        step_name=name,
        content=None,
        success=False,
        error=f"agente {name} não devolveu texto utilizável",
    )


def _make_rewrite_step(name: str, agent: Any, feedback: str = "") -> Step:
    def _run(step_input: StepInput) -> StepOutput:
        current_text = step_input.previous_step_content or step_input.input or ""
        prompt = f"{current_text}{feedback}" if feedback else current_text
        text = _response_text(agent.run(prompt))
        if not text:
            return _failed_step(name)
        return StepOutput(step_name=name, content=text, success=True)

    return Step(name=name, executor=_run, description=name)


def _make_integridade_step(name: str, agent: Any) -> Step:
    def _run(step_input: StepInput) -> StepOutput:
        original_text = step_input.input or ""
        current_text = step_input.previous_step_content or original_text
        prompt = (
            f"Texto original:\n{original_text}\n\n"
            f"Reescrita a revisar:\n{current_text}"
        )
        text = _response_text(agent.run(prompt))
        if not text:
            return _failed_step(name)
        return StepOutput(step_name=name, content=text, success=True)

    return Step(name=name, executor=_run, description=name)


def _executed_steps(run_output: Any) -> List[Any]:
    """Steps que de fato rodaram, achatando resultados compostos."""
    steps: List[Any] = []
    for result in getattr(run_output, "step_results", None) or []:
        nested = getattr(result, "steps", None)
        steps.extend(nested if nested else [result])
    return steps


def _workflow_text(run_output: Any) -> str:
    if getattr(run_output, "status", None) == RunStatus.error:
        return ""
    content = getattr(run_output, "content", None)
    if not isinstance(content, str) or not content.strip():
        return ""
    return content


def _failure_reason(run_output: Any) -> str:
    errors = [
        step.error
        for step in _executed_steps(run_output)
        if not getattr(step, "success", True) and getattr(step, "error", None)
    ]
    detail = f": {'; '.join(dict.fromkeys(errors))}" if errors else ""
    return f"execução da Camada 1 falhou{detail}"


class HumanizationPipeline:
    """Pipeline de agentes Agno da Camada 1, com gate determinístico final.

    O retry é guiado: a partir da segunda tentativa, os motivos de rejeição
    do gate são anexados ao prompt dos agentes de reescrita (cadência,
    anti-simetria e watermark), transformando a reamostragem em correção
    dirigida. O agente de integridade semântica não recebe o feedback — o
    papel dele é comparar original e reescrita, não atacar os motivos.
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

    def _feedback_prompt(self, reasons: List[str]) -> str:
        lang_key = "pt" if self.lang.lower().startswith("pt") else "en"
        return _FEEDBACK_TEMPLATES[lang_key].format(reasons="; ".join(reasons))

    def _build_workflow(self, needs_watermark: bool, feedback: str = "") -> Workflow:
        steps: List[Step] = [
            _make_rewrite_step(
                "cadencia", build_cadencia_agent(self.model, self.lang), feedback
            ),
            _make_rewrite_step(
                "anti_simetria",
                build_anti_simetria_agent(self.model, self.lang),
                feedback,
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
                    feedback,
                )
            )
        return Workflow(name="fatuus_camada1", steps=cast(Any, steps))

    def run(self, sanitized_text: str, original_text: str = "") -> PipelineResult:
        """Executa a Camada 1 sobre um texto já limpo pela Camada 0.

        `original_text` é o texto pré-sanitização; vazio significa medir a
        razão de tamanho do gate contra o próprio texto sanitizado — ver
        `evaluate_gate`.
        """
        original_analysis = self.detector.analyze(sanitized_text)

        if not _needs_layer1(original_analysis):
            gate = evaluate_gate(self.lang, sanitized_text, sanitized_text)
            return PipelineResult(
                final_text=sanitized_text, accepted=True, attempts=0, gate=gate
            )

        needs_watermark = _needs_watermark_agent(original_analysis)
        feedback = ""
        last_gate = GateResult(accepted=False, reasons=["Camada 1 não executou"])

        for attempt in range(1, self.max_iterations + 1):
            workflow = self._build_workflow(needs_watermark, feedback)
            run_output = workflow.run(input=sanitized_text)
            candidate_text = _workflow_text(run_output)

            if not candidate_text:
                last_gate = GateResult(
                    accepted=False, reasons=[_failure_reason(run_output)]
                )
                feedback = ""
                continue

            gate = evaluate_gate(
                self.lang,
                sanitized_text,
                candidate_text,
                size_baseline_text=original_text,
            )
            if gate.accepted:
                return PipelineResult(
                    final_text=candidate_text,
                    accepted=True,
                    attempts=attempt,
                    gate=gate,
                )
            last_gate = gate
            feedback = self._feedback_prompt(gate.reasons)

        return PipelineResult(
            final_text=sanitized_text,
            accepted=False,
            attempts=self.max_iterations,
            gate=last_gate,
        )
