"""Módulo de sanitização e des-clichêização determinística (Fatuus Sanitizer)."""

import re
from typing import Dict, List, Tuple
from .dicionarios import (
    LINE_SEPARATOR_CHARS,
    SPACE_LOOKALIKE_CHARS,
    TYPOGRAPHIC_REPLACEMENTS,
    VARIATION_SELECTORS,
    ZERO_WIDTH_CHARS,
    is_emoji_base,
)

REPLACEMENTS_PT = [
    (r"\bé importante (ressaltar|destacar|notar|lembrar|salientar) que\b", ""),
    (r"\bé importante (ressaltar|destacar|notar|lembrar|salientar)\b", ""),
    (r"\bno cenário atual,?\b", "hoje,"),
    (r"\bno mundo de hoje,?\b", "atualmente,"),
    (r"\bno mundo contemporâneo,?\b", "hoje,"),
    (r"\bvale a pena (notar|ressaltar|destacar) que\b", ""),
    (r"\bvale a pena (notar|ressaltar|destacar)\b", r"vale \1"),
    (r"\bvale lembrar que\b", ""),
    (r"\bem suma,?\b", "resumindo,"),
    (r"\bem conclusão,?\b", "portanto,"),
    (r"\bpor fim, mas não menos importante,?\b", "finalmente,"),
    (r"\bcomo mencionado anteriormente,?\b", "como mencionado,"),
    (r"\bum divisor de águas\b", "um marco"),
    (r"\bdesempenha um papel (fundamental|crucial|vital|central)\b", "é essencial"),
    (r"\buma ampla gama de\b", "vários"),
    (r"\buma vasta gama de\b", "vários"),
    (r"\bum vislumbre de\b", "uma visão de"),
    (r"\bmergulhar (?:mais )?fundo em\b", "aprofundar em"),
    (r"\bmergulhar em\b", "explorar"),
    (r"\bdesvendar os segredos\b", "analisar"),
    (r"\bfarol de (esperança|inovação|luz)\b", "referência"),
    (r"\btapeçaria (vibrante|complexa|cultural)\b", "estrutura"),
    (r"\bum testemunho (de|do|da|vivo)\b", "uma prova"),
    (r"\bessencial para garantir\b", "necessário para garantir"),
    (r"\bsempre em constante evolução\b", "em evolução"),
    (r"\bimpulsionar o crescimento\b", "acelerar o crescimento"),
    (r"\bpodemos concluir que\b", "conclui-se que"),
    (r"\bé inegável que\b", ""),
    (r"\bcabe destacar que\b", ""),
    (r"\bnos dias de hoje,?\b", "hoje,"),
    (r"\bdiante desse cenário,?\b", "diante disso,"),
    (r"\bcada vez mais presente\b", "mais presente"),
    (r"\buma verdadeira revolução\b", "uma mudança grande"),
    (r"\bmudança de paradigma\b", "mudança de modelo"),
    (r"\babordagem holística\b", "abordagem ampla"),
    (r"\bembarcar em uma jornada\b", "começar"),
    (r"\belevar o (nível|patamar)\b", "melhorar"),
    (r"\bdesbloquear o potencial\b", "aproveitar o potencial"),
    (r"\bé fundamental (compreender|entender|destacar)\b", r"é preciso \1"),
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
    (r"\bin today's world,?\b", "today,"),
    (r"\bnavigating the landscape of\b", "managing"),
    (r"\bnavigating the landscape\b", "finding a path"),
    (r"\bharnessing the power of\b", "using"),
    (r"\bunleash(ing)? the potential of\b", "enabling"),
    (r"\bunleashing the potential\b", "realizing the potential"),
    (r"\bunleash the potential\b", "realize the potential"),
    (r"\ba myriad of\b", "many"),
    (r"\ba plethora of\b", "many"),
    (r"\bfostering a sense of\b", "building"),
    (r"\bpoised to\b", "set to"),
    (r"\bunderscores the need\b", "shows the need"),
    (r"\bvibrant ecosystem\b", "active ecosystem"),
    (r"\bin conclusion,?\b", "in summary,"),
    (r"\blast but not least,?\b", "finally,"),
    (r"\bever-evolving\b", "changing"),
    (r"\bever-changing\b", "changing"),
    (r"\bin the realm of\b", "in"),
    (r"\bat the end of the day,?\b", "ultimately,"),
    (r"\bwhen it comes to\b", "for"),
    (r"\bit('| i)s worth noting that\b", ""),
    (r"\bit('| i)s worth noting\b", ""),
    (r"\bneedless to say,?\b", ""),
    (r"\bembark on a journey\b", "start"),
    (r"\bdive (deep|deeper) into\b", "examine"),
    (r"\btreasure trove of\b", "rich source of"),
    (r"\bparadigm shift\b", "major shift"),
    (r"\bholistic approach\b", "broad approach"),
    (r"\bseamlessly integrate(s|d)?\b", r"integrate\1 smoothly"),
    (r"\belevate your\b", "improve your"),
    (r"\bunlock the (full )?(power|potential|secrets) of\b", "make the most of"),
    (r"\bunlock the (full )?(power|potential|secrets)\b", r"use the \2"),
]

_SENTENCE_END_CHARS = ".!?\n"


class FatuusSanitizer:
    """Higienizador determinístico de texto sintético."""

    def __init__(self, lang: str = "pt"):
        self.lang = lang.lower()
        self.replacements = (
            REPLACEMENTS_PT if self.lang.startswith("pt") else REPLACEMENTS_EN
        )

    def remove_invisible_chars(self, text: str) -> Tuple[str, int]:
        """Remove caracteres invisíveis, zero-width e controles bidirecionais.

        Seletores de variação são preservados quando seguem uma base emoji
        (apresentação legítima) e removidos em qualquer outra posição.
        """
        count = 0
        cleaned = []
        for i, char in enumerate(text):
            if char in ZERO_WIDTH_CHARS or (
                char in VARIATION_SELECTORS
                and not (i > 0 and is_emoji_base(text[i - 1]))
            ):
                count += 1
            else:
                cleaned.append(char)
        return "".join(cleaned), count

    def normalize_typography(self, text: str) -> Tuple[str, int]:
        """Normaliza espaços disfarçados, separadores de linha, aspas curvas e reticências."""
        count = 0
        cleaned = []
        for char in text:
            if char in SPACE_LOOKALIKE_CHARS:
                cleaned.append(" ")
                count += 1
            elif char in LINE_SEPARATOR_CHARS:
                cleaned.append("\n")
                count += 1
            elif char in TYPOGRAPHIC_REPLACEMENTS:
                cleaned.append(TYPOGRAPHIC_REPLACEMENTS[char])
                count += 1
            else:
                cleaned.append(char)
        return "".join(cleaned), count

    def _apply_pattern(
        self, text: str, regex: "re.Pattern[str]", replacement: str
    ) -> Tuple[str, List[int], int]:
        """Aplica um padrão registrando a posição de cada substituição no texto novo."""
        parts: List[str] = []
        positions: List[int] = []
        out_len = 0
        last = 0
        made = 0
        for match in regex.finditer(text):
            head = text[last : match.start()]
            parts.append(head)
            out_len += len(head)
            positions.append(out_len)
            expanded = match.expand(replacement)
            parts.append(expanded)
            out_len += len(expanded)
            last = match.end()
            made += 1
        parts.append(text[last:])
        return "".join(parts), positions, made

    def _capitalize_at(self, text: str, positions: List[int]) -> str:
        """Capitaliza a primeira palavra em posições de substituição que caem
        em início de sentença.

        Só palavras inteiramente minúsculas são tocadas: "iPhone" ou "macOS"
        em início de frase ficam como estão.
        """
        chars = list(text)
        for pos in positions:
            i = pos
            while i < len(chars) and chars[i] in " \t":
                i += 1
            if i >= len(chars) or not chars[i].islower():
                continue
            j = pos - 1
            while j >= 0 and chars[j] in " \t":
                j -= 1
            if j >= 0 and chars[j] not in _SENTENCE_END_CHARS:
                continue
            word_end = i
            while word_end < len(chars) and chars[word_end].isalpha():
                word_end += 1
            word = "".join(chars[i:word_end])
            if word == word.lower():
                chars[i] = chars[i].upper()
        return "".join(chars)

    def deslop_text(self, text: str) -> Tuple[str, int]:
        """Substitui clichês óbvios de LLM por formulações diretas."""
        cleaned = text
        replacements_made = 0
        for pattern, replacement in self.replacements:
            regex = re.compile(pattern, re.IGNORECASE)
            cleaned, positions, made = self._apply_pattern(
                cleaned, regex, replacement
            )
            if made:
                replacements_made += made
                cleaned = self._capitalize_at(cleaned, positions)

        cleaned = re.sub(r" {2,}", " ", cleaned)
        cleaned = re.sub(r"\s+([,.!?;:])", r"\1", cleaned)
        cleaned = re.sub(r"(^|\n) +", r"\1", cleaned)
        return cleaned, replacements_made

    def clean(self, text: str) -> Dict[str, any]:
        """Executa limpeza determinística completa."""
        no_invisible, invisible_count = self.remove_invisible_chars(text)
        normalized, typography_count = self.normalize_typography(no_invisible)
        deslopped, slop_replacements = self.deslop_text(normalized)

        return {
            "cleaned_text": deslopped,
            "invisible_removed": invisible_count,
            "typography_normalized": typography_count,
            "slop_replaced": slop_replacements,
        }
