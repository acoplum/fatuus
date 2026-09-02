"""Fábricas dos agentes especializados da Camada 1."""

from typing import Any

from agno.agent import Agent

_INSTRUCTIONS = {
    "cadencia": {
        "pt": (
            "Você reescreve texto em português para variar o ritmo das frases, "
            "alternando frases curtas com frases mais longas e com subordinação. "
            "Não invente fatos, números, nomes ou dados que não estejam no texto "
            "recebido. Não adicione comentário: devolva só o texto reescrito."
        ),
        "en": (
            "You rewrite English text to vary sentence rhythm, alternating short "
            "sentences with longer, subordinate ones. Never invent facts, "
            "numbers, names, or data absent from the received text. Do not add "
            "commentary: return only the rewritten text."
        ),
    },
    "anti_simetria": {
        "pt": (
            "Você quebra paralelismos rígidos e listas excessivamente simétricas "
            "no texto em português recebido, sem alterar fatos, números ou "
            "nomes. Devolva só o texto reescrito, sem comentário."
        ),
        "en": (
            "You break rigid parallelisms and overly symmetric lists in the "
            "received English text, without changing facts, numbers, or names. "
            "Return only the rewritten text, with no commentary."
        ),
    },
    "integridade_semantica": {
        "pt": (
            "Você recebe um texto original e uma reescrita dele. Compare os "
            "dois e corrija a reescrita para restaurar qualquer fato, número, "
            "nome ou entidade do original que a reescrita tenha perdido ou "
            "alterado. Se a reescrita já preservar tudo, devolva-a sem mudança. "
            "Devolva só o texto final, sem comentário."
        ),
        "en": (
            "You receive an original text and a rewrite of it. Compare both "
            "and fix the rewrite to restore any fact, number, name, or entity "
            "from the original that the rewrite lost or changed. If the "
            "rewrite already preserves everything, return it unchanged. Return "
            "only the final text, with no commentary."
        ),
    },
    "watermark_estatistico": {
        "pt": (
            "Você recebe um texto que pode ter um padrão estatístico de "
            "escolha de palavras característico de um único modelo de LLM "
            "(watermark de token-sampling). Reescreva trocando escolhas de "
            "palavra previsíveis por alternativas igualmente naturais, sem "
            "alterar fatos, números ou nomes. Devolva só o texto reescrito, "
            "sem comentário."
        ),
        "en": (
            "You receive a text that may carry a statistical word-choice "
            "pattern characteristic of a single LLM (token-sampling "
            "watermark). Rewrite it by swapping predictable word choices for "
            "equally natural alternatives, without changing facts, numbers, or "
            "names. Return only the rewritten text, with no commentary."
        ),
    },
}


def _build(name: str, key: str, model: Any, lang: str) -> Agent:
    lang_key = "pt" if lang.lower().startswith("pt") else "en"
    return Agent(name=name, model=model, instructions=_INSTRUCTIONS[key][lang_key])


def build_cadencia_agent(model: Any, lang: str = "pt") -> Agent:
    return _build("Agente de Cadência", "cadencia", model, lang)


def build_anti_simetria_agent(model: Any, lang: str = "pt") -> Agent:
    return _build("Agente Anti-Simetria", "anti_simetria", model, lang)


def build_integridade_agent(model: Any, lang: str = "pt") -> Agent:
    return _build(
        "Agente de Integridade Semântica", "integridade_semantica", model, lang
    )


def build_watermark_agent(model: Any, lang: str = "pt") -> Agent:
    return _build("Agente de Watermark Estatístico", "watermark_estatistico", model, lang)
