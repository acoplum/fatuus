"""Módulo de sanitização e des-clichêização determinística (Fatuus Sanitizer)."""

import re
from typing import Dict, List, Tuple
from .dicionarios import ZERO_WIDTH_CHARS

REPLACEMENTS_PT = [
    (r"\bé importante (ressaltar|destacar|notar|lembrar|salientar) que\b", ""),
    (r"\bé importante (ressaltar|destacar|notar|lembrar|salientar)\b", ""),
    (r"\bno cenário atual,?\b", "hoje,"),
    (r"\bno mundo de hoje,?\b", "atualmente,"),
    (r"\bno mundo contemporâneo,?\b", "hoje,"),
    (r"\bvale a pena (notar|ressaltar|destacar) que\b", ""),
    (r"\bem suma,?\b", "resumindo,"),
    (r"\bem conclusão,?\b", "portanto,"),
    (r"\bpor fim, mas não menos importante,?\b", "finalmente,"),
    (r"\bum divisor de águas\b", "um marco"),
    (r"\bdesempenha um papel (fundamental|crucial|vital|central)\b", "é essencial"),
    (r"\buma ampla gama de\b", "vários"),
    (r"\bum vislumbre de\b", "uma visão de"),
    (r"\bmergulhar fundo em\b", "aprofundar em"),
    (r"\bmergulhar em\b", "explorar"),
    (r"\bdesvendar os segredos\b", "analisar"),
    (r"\bfarol de (esperança|inovação|luz)\b", "referência"),
    (r"\btapeçaria (vibrante|complexa|cultural)\b", "estrutura"),
    (r"\bum testemunho (de|do|da|vivo)\b", "uma prova"),
    (r"\bsempre em constante evolução\b", "em evolução"),
    (r"\bpodemos concluir que\b", "conclui-se que"),
]

REPLACEMENTS_EN = [
    (r"\bit is important to (note|remember|highlight) that\b", ""),
    (r"\bit is important to (note|remember|highlight)\b", ""),
    (r"\bdelve into\b", "explore"),
    (r"\ba testament to\b", "evidence of"),
    (r"\btapestry of\b", "mix of"),
    (r"\bbeacon of\b", "guide for"),
    (r"\bcrucial role\b", "key role"),
    (r"\bpivotal (moment|role|step)\b", "essential \\1"),
    (r"\bgame-changer\b", "significant change"),
    (r"\bin today's fast-paced world,?\b", "today,"),
    (r"\bin today's digital landscape,?\b", "currently,"),
    (r"\bnavigating the landscape of\b", "managing"),
    (r"\bharnessing the power of\b", "using"),
    (r"\bunleash(ing)? the potential of\b", "enabling"),
    (r"\ba myriad of\b", "many"),
    (r"\ba plethora of\b", "many"),
    (r"\bfostering a sense of\b", "building"),
    (r"\bvibrant ecosystem\b", "active ecosystem"),
    (r"\bin conclusion,?\b", "in summary,"),
    (r"\blast but not least,?\b", "finally,"),
]


class FatuusSanitizer:
    """Higienizador determinístico de texto sintético."""

    def __init__(self, lang: str = "pt"):
        self.lang = lang.lower()
        self.replacements = (
            REPLACEMENTS_PT if self.lang.startswith("pt") else REPLACEMENTS_EN
        )

    def remove_invisible_chars(self, text: str) -> Tuple[str, int]:
        """Remove todos os caracteres invisíveis e de zero-width."""
        count = 0
        cleaned = []
        for char in text:
            if char in ZERO_WIDTH_CHARS:
                count += 1
            else:
                cleaned.append(char)
        return "".join(cleaned), count

    def deslop_text(self, text: str) -> Tuple[str, int]:
        """Substitui clichês óbvios de LLM por formulações diretas."""
        cleaned = text
        replacements_made = 0
        for pattern, replacement in self.replacements:
            new_text, n = re.subn(pattern, replacement, cleaned, flags=re.IGNORECASE)
            if n > 0:
                replacements_made += n
                cleaned = new_text

        cleaned = re.sub(r" {2,}", " ", cleaned)
        cleaned = re.sub(r"\s+([,.!?;:])", r"\1", cleaned)
        return cleaned, replacements_made

    def clean(self, text: str) -> Dict[str, any]:
        """Executa limpeza determinística completa."""
        no_invisible, invisible_count = self.remove_invisible_chars(text)
        deslopped, slop_replacements = self.deslop_text(no_invisible)

        return {
            "cleaned_text": deslopped,
            "invisible_removed": invisible_count,
            "slop_replaced": slop_replacements,
        }
