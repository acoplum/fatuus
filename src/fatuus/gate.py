"""Gate determinístico de aceitação para o output da Camada 1."""

from dataclasses import dataclass, field
from typing import List

from .detector import FatuusDetector

WORD_COUNT_RATIO_MIN = 0.3
WORD_COUNT_RATIO_MAX = 1.4


@dataclass
class GateResult:
    accepted: bool
    reasons: List[str] = field(default_factory=list)
    original_burstiness: float = 0.0
    candidate_burstiness: float = 0.0


def evaluate_gate(
    lang: str,
    original_text: str,
    candidate_text: str,
    size_baseline_text: str = "",
) -> GateResult:
    """Valida se `candidate_text` pode substituir `original_text`.

    A checagem de variação de tamanho é um proxy determinístico para
    integridade semântica nesta versão — não é similaridade semântica real
    (exigiria embeddings, fora do orçamento zero-cost da Camada 0).

    `size_baseline_text` é o texto contra o qual a razão de tamanho é medida;
    vazio significa medir contra `original_text`. A Camada 1 recebe texto já
    sanitizado, que perdeu as palavras de conexão junto com os clichês — uma
    reescrita natural restaura esse tecido conectivo e fica perto da contagem
    de palavras do texto *pré-sanitização*, não da do sanitizado. Medir contra
    o sanitizado estoura o limite superior sistematicamente, por isso o
    `/clean` passa aqui o texto original do usuário.
    """
    detector = FatuusDetector(lang=lang)
    original_analysis = detector.analyze(original_text)
    candidate_analysis = detector.analyze(candidate_text)
    size_baseline_analysis = (
        detector.analyze(size_baseline_text)
        if size_baseline_text
        else original_analysis
    )

    reasons: List[str] = []

    if candidate_analysis["slop_count"] > 0:
        reasons.append(
            f"clichê reintroduzido: {candidate_analysis['slop_count']} ocorrência(s)"
        )

    if candidate_analysis["invisible_char_count"] > 0:
        reasons.append(
            "caractere invisível reintroduzido: "
            f"{candidate_analysis['invisible_char_count']}"
        )

    original_burstiness = original_analysis["sentence_metrics"]["burstiness"]
    candidate_burstiness = candidate_analysis["sentence_metrics"]["burstiness"]
    if candidate_burstiness <= original_burstiness:
        reasons.append(
            f"burstiness não melhorou: {original_burstiness} -> {candidate_burstiness}"
        )

    baseline_words = size_baseline_analysis["word_count"]
    candidate_words = candidate_analysis["word_count"]
    if baseline_words > 0:
        ratio = candidate_words / baseline_words
        if ratio < WORD_COUNT_RATIO_MIN or ratio > WORD_COUNT_RATIO_MAX:
            reasons.append(
                f"variação de tamanho fora do limite ({ratio:.2f}x o original)"
            )

    return GateResult(
        accepted=len(reasons) == 0,
        reasons=reasons,
        original_burstiness=original_burstiness,
        candidate_burstiness=candidate_burstiness,
    )
